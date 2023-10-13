import glob
import re
import os
import shutil
import sys
from chirun import mkdir_p
from chirun.plasTeXRenderer.Imagers.pdf2svg import Imager as VectorImager
from chirun.plasTeXRenderer.Imagers.pdftoppm import Imager as Imager
from pathlib import Path
import plasTeX
from plasTeX import Environment
import plasTeX.Compile
from plasTeX.Tokenizer import EscapeSequence
from plasTeX.TeX import TeX
from plasTeX.Logging import getLogger
import plasTeX.Logging
from plasTeX.Config import defaultConfig
from plasTeX.ConfigManager import ConfigManager
from chirun.plasTeXRenderer.Renderers.ChirunRenderer import Renderer
import chirun.plasTeXRenderer.Renderers.ChirunRenderer.Config as html_config
from . import overrides


def reset_idgen():
    """
        Reset plasTeX's ID generator, so it produces the same IDs each time it is run on the same document.
    """

    def idgen():
        """ Generate a unique ID """
        i = 1
        while 1:
            yield 'a%.10d' % i
            i += 1

    plasTeX.idgen = idgen()

logger = getLogger()
imagelog = getLogger('imager')
imagelog.setLevel('INFO')


def getEmbeddedImages(course, html, item):

    # TODO: make this extensible
    patterns = [
        re.compile(r'<img.*? src="(?P<url>[^"]*)".*?>', re.DOTALL),
    ]

    def fix_image_path(m):
        # TODO: don't rewrite URLs with a URI scheme, i.e. only rewrite relative URLs
        raw_path = Path(m.group('url'))
        inFile = raw_path.name
        inPath = item.temp_path() / 'images' / inFile
        finalURL = item.out_path / 'images' / inFile
        outPath = course.get_build_dir() / finalURL

        # Move the file into build tree's static dir
        mkdir_p(outPath.parent)
        shutil.copyfile(str(inPath), str(outPath))

        # Update the output of plastex to reflect the change
        start, end = m.span('url')
        start -= m.start()
        end -= m.start()
        img = m.group(0)
        return img[:start] + '/' + str(finalURL) + img[end:]

    for pattern in patterns:
        html = pattern.sub(fix_image_path, html)

    return html


def _processIfContent(self, which, debug=False):
    # Since the true content always comes first, we need to set
    # True to case 0 and False to case 1.
    if isinstance(which, bool):
        if which:
            which = 0
        else:
            which = 1
    cases = [[]]
    nesting = 0
    correctly_terminated = False
    iterator = self.itertokens()
    for t in iterator:
        name = getattr(t, 'macroName', '') or ''
        if name == 'newif':
            cases[-1].append(t)
            cases[-1].append(next(iterator))
            continue
        elif name.startswith('if') and name not in ['iframe']:
            cases[-1].append(t)
            nesting += 1
        elif name == 'fi':
            if not nesting:
                correctly_terminated = True
                break
            cases[-1].append(t)
            nesting -= 1
        elif not (nesting) and name == 'else':
            cases.append([])
            continue
        elif not (nesting) and name == 'or':
            cases.append([])
            continue
        else:
            cases[-1].append(t)
    if not correctly_terminated:
        logger.warning(r'\end occurred when \if was incomplete')
    cases.append([])
    self.pushTokens(cases[which])


class PlastexRunner:

    def exception_handler(exception_type, exception, traceback):
        print("%s: %s" % (exception_type.__name__, exception))

    def load_latex_content(self, item, out_file=None):
        """
            Convert a LaTeX file to HTML, and do some processing with its images
        """
        self.runPlastex(item, out_file)
        plastex_output = {}

        for section, filename in self.renderer.files.items():
            filepath = item.temp_path() / filename
            if filepath.is_file():
                with open(filepath, encoding='utf-8-sig') as f:
                    html = getEmbeddedImages(self, f.read(), item)

                plastex_output[filepath.name] = {
                    # TODO: an abstraction for applying the following as a series of filters
                    'html': html,
                    'title': section.title if isinstance(section.title, str) else section.title.textContent.strip(),
                    'source': filepath.name,
                    'level': getattr(section, 'level', None),
                    'counter': getattr(section, 'counter', None),
                    'ref': section.ref.textContent.strip() if section.ref else None
                }

        return plastex_output

    def parse(self, filename: str, config: ConfigManager) -> TeX:
        """ 
            Modified from plasTeX.Compile.parse.
        """

        # Create document instance that output will be put into
        document = self.document = plasTeX.TeXDocument(config=config)

        document.context.importMacros(vars(overrides))
        TeX.processIfContent = _processIfContent     # TODO - check if this changed in plasTeX 3

        # Instantiate the TeX processor
        tex = TeX(document, file=str(filename))

        # Populate variables for use later
        if config['document']['title']:
            document.userdata['title'] = config['document']['title']

        jobname = document.userdata['jobname'] = tex.jobname
        cwd = document.userdata['working-dir'] = '.'

        # Load aux files for cross-document references
        pauxname = '%s.paux' % jobname
        rname = config['general']['renderer']
        for dirname in [cwd] + config['general']['paux-dirs']:
            for fname in glob.glob(os.path.join(dirname, '*.paux')):
                if os.path.basename(fname) == pauxname:
                    continue
                document.context.restore(fname, rname)

        # Parse the document
        tex.parse()
        return tex

    def runPlastex(self, item, out_file=None):
        if not item.course.args.veryverbose:
            plasTeX.Logging.disableLogging()

        old_texinputs = os.environ['TEXINPUTS']
        try:
            wd = os.getcwd()

            logger.debug("PlasTeX: " + str(item.source))
            root_dir = self.get_root_dir()
            outPath = item.temp_path().resolve()
            outPaux = self.temp_path().resolve()
            inPath = Path(wd) / root_dir / item.source

            os.environ['TEXINPUTS'] += f':{inPath.parent}'

            os.chdir(inPath.parent)

            reset_idgen()

            plastex_config = defaultConfig(loadConfigFiles = False)
            plastex_config['general']['plugins'].append('chirun.plasTeXRenderer')
            plastex_config['general']['plugins'].append('chirun.plastex')
            html_config.addConfig(plastex_config)

            plastex_config['files']['filename'] = str(item.plastex_filename_rules(out_file))
            plastex_config['files']['split-level'] = item.splitlevel
            plastex_config['general']['renderer'] = 'ChirunRenderer'
            plastex_config['document']['base-url'] = self.get_web_root()
            plastex_config['images']['vector-imager'] = 'none'
            plastex_config['images']['imager'] = 'none'


            sys.excepthook = PlastexRunner.exception_handler

            tex = self.parse(inPath, plastex_config)
            document = tex.ownerDocument
            cwd = document.userdata['working-dir'] = '.'
            jobname = document.userdata['jobname'] = tex.jobname

            os.chdir(outPath)

            renderer = self.renderer = Renderer()
            #renderer.loadTemplates(self.document)
            renderer.importDirectory(str(Path(wd) / self.theme.source / 'plastex'))
            renderer.vectorImager = VectorImager(self.document, self.renderer.vectorImageTypes)
            renderer.imager = Imager(self.document, self.renderer.imageTypes)

            # Apply renderer
            try:
                renderer.render(document)
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise e

            os.chdir(wd)

            original_paux_path = item.temp_path() / item.base_file.with_suffix('.paux')
            collated_paux_path = self.temp_path() / (str(item.out_path).replace('/', '-') + '.paux')

            shutil.copyfile(str(original_paux_path), str(collated_paux_path))

        finally:
            os.environ['TEXINPUTS'] = old_texinputs


class NoCharSubEnvironment(Environment):
    """
    A subclass of Environment which prevents character substitution inside
    itself.
    """

    def normalize(self, charsubs=None):
        """ Normalize, but don't allow character substitutions """
        return Environment.normalize(self, charsubs=None)


class VerbatimEnvironment(NoCharSubEnvironment):
    """
    A subclass of Environment that prevents processing of the contents. This is
    used for the verbatim environment.

    It is also useful in cases where you want to leave the processing to the
    renderer (e.g. via the imager) and the content is sufficiently complex that
    we don't want plastex to deal with the commands within it.

    For example, for tikzpicture, there are many Tikz commands and it would be
    tedious to attempt to define all of them in the python file, when we are
    not going to use them anyway.
    """

    blockType = True
    captionable = True

    def invoke(self, tex):
        """
        We enter verbatim mode by setting all category codes to CC_LETTER
        or CC_OTHER. However, we will have to manually scan for the end of the
        environment since the tokenizer does not tokenize the end of the
        environment as an EscapeSequence Token.
        """
        if self.macroMode == Environment.MODE_END:
            return

        escape = self.ownerDocument.context.categories[0][0]
        bgroup = self.ownerDocument.context.categories[1][0]
        egroup = self.ownerDocument.context.categories[2][0]
        self.ownerDocument.context.push(self)
        self.parse(tex)
        self.ownerDocument.context.setVerbatimCatcodes()
        tokens = [self]

        # Get the name of the currently expanding environment
        name = self.nodeName
        if self.macroMode != Environment.MODE_NONE:
            if self.ownerDocument.context.currenvir is not None:
                name = self.ownerDocument.context.currenvir

        envname = None
        if self.ownerDocument.context.currenvir is not None:
            envname = self.ownerDocument.context.currenvir
            # If we were invoked by a command but should be ended by an
            # \end{...}, look for and \end{...} and check if it really contains
            # \endverbatim
            endpattern3 = list(r'%send%s%s%s' % (escape, bgroup, envname, egroup))
            endlength3 = len(endpattern3)

        # If we were invoked by a \begin{...} look for an \end{...}
        endpattern = list(r'%send%s%s%s' % (escape, bgroup, name, egroup))

        # If we were invoked as a command (i.e. \verbatim) look
        # for an end without groupings (i.e. \endverbatim)
        endpattern2 = list(r'%send%s' % (escape, name))

        endlength = len(endpattern)
        endlength2 = len(endpattern2)
        # Iterate through tokens until the endpattern is found
        for tok in tex:
            tokens.append(tok)
            if len(tokens) >= endlength:
                if tokens[-endlength:] == endpattern:
                    tokens = tokens[:-endlength]
                    self.ownerDocument.context.pop(self)
                    # Expand the end of the macro
                    end = self.ownerDocument.createElement(name)
                    end.parentNode = self.parentNode
                    end.macroMode = Environment.MODE_END
                    res = end.invoke(tex)
                    if res is None:
                        res = [end]
                    tex.pushTokens(res)
                    break
            if len(tokens) >= endlength2:
                if tokens[-endlength2:] == endpattern2:
                    tokens = tokens[:-endlength2]
                    self.ownerDocument.context.pop(self)
                    # Expand the end of the macro
                    end = self.ownerDocument.createElement(name)
                    end.parentNode = self.parentNode
                    end.macroMode = Environment.MODE_END
                    res = end.invoke(tex)
                    if res is None:
                        res = [end]
                    tex.pushTokens(res)
                    break
            if envname is not None and len(tokens) >= endlength3:
                if tokens[-endlength3:] == endpattern3:
                    tokens = tokens[:-endlength3]
                    self.ownerDocument.context.pop(self)
                    # Expand the end of the macro
                    endenv = self.ownerDocument.createElement(envname)
                    endenv.parentNode = self.parentNode
                    endenv.macroMode = Environment.MODE_END
                    res = endenv.invoke(tex)
                    end = EscapeSequence('end%s' % name)
                    if end in res:
                        tex.pushTokens(res)
                        break
        return tokens
