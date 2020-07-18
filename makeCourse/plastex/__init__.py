import glob
import re
import os
import shutil
import sys
from makeCourse import mkdir_p
from pathlib import Path
from subprocess import Popen, PIPE
from plasTeX import TeXDocument
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
        re.compile(r'<img.*? src="(?P<url>[^"]*)".*?>'),
        re.compile(r'<object class=\"tikzpicture\" data=\"(?P<url>[^\)]*)\" type=\"image/svg\+xml\">'),
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

        source_file = item.temp_path() / item.out_file
        with open(str(source_file), encoding='utf-8') as f:
            html = f.read()
        # TODO: an abstraction for applying the following as a series of filters
        html = getEmbeddedImages(self, html, item)
        return html

    def runPlastex(self, item):
        if not item.course.args.veryverbose:
            plasTeX.Logging.disableLogging()

        logger.debug("PlasTeX: "+str(item.source))
        root_dir = self.get_root_dir()
        outPath = item.temp_path()
        outPaux = self.temp_path().resolve()
        inPath = root_dir / item.source

        wd = os.getcwd()

        plastex_config['files']['filename'] = item.out_file
        rname = plastex_config['general']['renderer'] = 'makecourse'
        plastex_config['document']['base-url'] = self.get_web_root()
        document = TeXDocument(config=plastex_config)
        document.userdata['working-dir'] = '.'
        tikzPath = self.config.get('tikz_template')
        if tikzPath:
            logger.debug('Using tikz template: ' + tikzPath)
            document.userdata['tikz-template'] = tikzPath
        document.context.importMacros(vars(macros))
        document.context.importMacros(vars(overrides))

        f = open(str(Path(wd) / inPath))
        tex = TeX(document, myfile=f)
        document.userdata['jobname'] = tex.jobname
        pauxname = os.path.join(document.userdata.get('working-dir','.'),
                            '%s.paux' % document.userdata.get('jobname',''))

        for fname in glob.glob(str(outPaux / '*.paux')):
            if os.path.basename(fname) == pauxname:
                continue
            document.context.restore(fname,'makecourse')

        sys.excepthook = PlastexRunner.exception_handler
        tex.parse()
        f.close()

        os.chdir(str(outPath))
        renderer = Renderer()
        renderer.loadTemplates(document)
        renderer.importDirectory(str(Path(wd) / self.theme.source / 'plastex'))
        renderer.render(document)

        os.chdir(wd)

        original_paux_path = item.temp_path() / item.base_file.with_suffix('.paux')
        collated_paux_path = self.temp_path() / (str(item.out_path).replace('/','-') + '.paux')
        shutil.copyfile(str(original_paux_path), str(collated_paux_path))
