import glob
import re
import os
import shutil
import sys
from makeCourse import mkdir_p
from makeCourse.plastex.Imagers.pdf2svg import Imager as VectorImager
from pathlib import Path
from subprocess import Popen, PIPE
from plasTeX import Environment, TeXDocument
from makeCourse.plasTeXRenderer import Renderer
from plasTeX.TeX import TeX
from plasTeX.Logging import getLogger
import plasTeX.Logging
from plasTeX.Config import config as plastex_config
import makeCourse.plasTeXRenderer.Config as html_config
from . import macros
from . import overrides

plastex_config += html_config.config

logger = getLogger()
imagelog = getLogger('imager')
imagelog.setLevel('INFO')

# Add makecourse's custom plastex packages to the path
sys.path.insert(0,os.path.dirname(__file__))

def getEmbeddedImages(course, html, item):

    # TODO: make this extensible
    patterns = [
        re.compile(r'<img.*? src="(?P<url>[^"]*)".*?>(?s)'),
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
        return img[:start] + '/' +str(finalURL) + img[end:]

    for pattern in patterns:
        html = pattern.sub(fix_image_path, html)

    return html

class PlastexRunner:

    def exception_handler(exception_type, exception, traceback):
        print("%s: %s" % (exception_type.__name__, exception))

    def load_latex_content(self, item):
        """
            Convert a LaTeX file to HTML, and do some processing with its images
        """
        self.runPlastex(item)
        plastex_output = {}

        for section,filename in self.renderer.files.items():
            filepath = item.temp_path() / filename
            if filepath.is_file():
                with open(filepath, encoding='utf-8') as f:
                    plastex_output[filepath.name] = {
                        # TODO: an abstraction for applying the following as a series of filters
                        'html': getEmbeddedImages(self, f.read(), item),
                        'title': section.title if isinstance(section.title,str) else section.title.textContent.strip(),
                        'source': filepath.name
                    }
        return plastex_output

    def runPlastex(self, item):
        if not item.course.args.veryverbose:
            plasTeX.Logging.disableLogging()

        logger.debug("PlasTeX: "+str(item.source))
        root_dir = self.get_root_dir()
        outPath = item.temp_path()
        outPaux = self.temp_path().resolve()
        inPath = root_dir / item.source

        wd = os.getcwd()

        plastex_config['files']['filename'] = item.plastex_filename_rules
        plastex_config['files']['split-level'] = item.splitlevel
        rname = plastex_config['general']['renderer'] = 'makecourse'
        plastex_config['document']['base-url'] = self.get_web_root()
        plastex_config['images']['vector-imager'] = 'none'
        plastex_config['images']['imager'] = 'pdftoppm'
        self.document = TeXDocument(config=plastex_config)
        self.document.userdata['working-dir'] = '.'

        self.document.context.importMacros(vars(macros))
        self.document.context.importMacros(vars(overrides))

        f = open(str(Path(wd) / inPath))
        tex = TeX(self.document, myfile=f)
        self.document.userdata['jobname'] = tex.jobname
        pauxname = os.path.join(self.document.userdata.get('working-dir','.'),
                            '%s.paux' % self.document.userdata.get('jobname',''))

        for fname in glob.glob(str(outPaux / '*.paux')):
            if os.path.basename(fname) == pauxname:
                continue
            self.document.context.restore(fname,'makecourse')

        sys.excepthook = PlastexRunner.exception_handler
        tex.parse()
        f.close()

        os.chdir(str(outPath))
        self.renderer = Renderer()
        self.renderer.loadTemplates(self.document)
        self.renderer.importDirectory(str(Path(wd) / self.theme.source / 'plastex'))
        self.renderer.vectorImager = VectorImager(self.document, self.renderer.vectorImageTypes)
        self.renderer.render(self.document)

        os.chdir(wd)

        original_paux_path = item.temp_path() / item.base_file.with_suffix('.paux')
        collated_paux_path = self.temp_path() / (str(item.out_path).replace('/','-') + '.paux')
        shutil.copyfile(str(original_paux_path), str(collated_paux_path))

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

        return tokens
