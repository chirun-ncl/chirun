import glob
import re
import os
import shutil
import sys
from makeCourse import mkdir_p
from makeCourse.plastex.Imagers.pdf2svg import Imager as VectorImager
from makeCourse.plastex.Imagers.pdftoppm import Imager as Imager
from makeCourse.plasTeXRenderer import Renderer
from pathlib import Path
from subprocess import Popen, PIPE
from plasTeX import Environment, TeXDocument
from plasTeX.TeX import TeX
from plasTeX.Logging import getLogger
import plasTeX.Logging
from plasTeX.Config import defaultConfig
from plasTeX.Renderers.HTML5.Config import addConfig as add_html_config
from makeCourse.plastex import macros
from makeCourse.plastex import overrides

plastex_config = defaultConfig()
add_html_config(plastex_config)

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
        plastex_config['general']['renderer'] = 'makecourse'
        plastex_config['general']['packages-dirs'] = os.path.dirname(__file__)
        plastex_config['document']['base-url'] = self.get_web_root()
        plastex_config['images']['vector-imager'] = 'none'
        plastex_config['images']['imager'] = 'none'
        plastex_config['html5']['use-theme-js'] = False
        plastex_config['html5']['use-theme-css'] = False
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
        self.renderer.imager = Imager(self.document, self.renderer.imageTypes)
        self.renderer.render(self.document)

        os.chdir(wd)

        original_paux_path = item.temp_path() / item.base_file.with_suffix('.paux')
        collated_paux_path = self.temp_path() / (str(item.out_path).replace('/','-') + '.paux')
        shutil.copyfile(str(original_paux_path), str(collated_paux_path))
