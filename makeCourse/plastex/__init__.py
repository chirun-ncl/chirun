import logging
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
import plasTeX.Logging
from plasTeX.Config import config as plastex_config
import makeCourse.plasTeXRenderer.Config as html_config
from . import macros

plastex_config += html_config.config

logger = logging.getLogger(__name__)

def getEmbeddedImages(course, html, sourceItem):
    title = sourceItem.title
    logger.debug('    Moving embedded images')

    # TODO: make this extensible
    patterns = [
        re.compile(r'<img.*? src="(?P<url>[^"]*)".*?>'),
        re.compile(r'<object class=\"tikzpicture\" data=\"(?P<url>[^\)]*)\" type=\"image/svg\+xml\">'),
    ]

    def fix_image_path(m):
        # TODO: don't rewrite URLs with a URI scheme, i.e. only rewrite relative URLs
        raw_path = Path(m.group('url'))
        inFile = raw_path.name
        inPath = sourceItem.temp_path() / 'images' / inFile
        finalURL = sourceItem.out_file / 'images' / inFile
        outPath = course.get_build_dir() / finalURL

        # Move the file into build tree's static dir
        mkdir_p(outPath.parent)
        shutil.copyfile(str(inPath), str(outPath))

        # Update the output of plastex to reflect the change
        start, end = m.span('url')
        start -= m.start()
        end -= m.start()
        img = m.group(0)
        return img[:start] + course.get_web_root() + str(finalURL) + img[end:]

    for pattern in patterns:
        html = pattern.sub(fix_image_path, html)

    return html
class PlastexRunner:

    def load_latex_content(self, sourceItem):
        """
            Convert a LaTeX file to HTML, and do some processing with its images
        """
        tmpDir = sourceItem.temp_path()
        self.runPlastex(sourceItem)

        # All the paux files for the course are collected in the temp_path
        original_paux_path = sourceItem.temp_path() / sourceItem.base_file.with_suffix('.paux')
        collated_paux_path = self.temp_path() / (str(sourceItem.out_file).replace('/','-') + '.paux')
        shutil.move(str(original_paux_path), str(collated_paux_path))

        root_dir = self.get_root_dir()

        source_file = tmpDir / sourceItem.url
        with open(str(source_file), encoding='utf-8') as f:
            html = f.read()
        # TODO: an abstraction for applying the following as a series of filters
        html = getEmbeddedImages(self, html, sourceItem)
        return html


    def getTikzTemplateArgs(self):
        tikzPath = self.config.get('tikz_template')
        if tikzPath:
            logger.debug('Using tikz template: ' + tikzPath)
            return "--tikz-template=%s" % tikzPath
        else:
            return ""

    def runPlastex(self, sourceItem):
        logger.debug("PlasTeX: "+str(sourceItem.source))
        root_dir = self.get_root_dir()
        outPath = sourceItem.temp_path()
        outPaux = self.temp_path()
        inPath = root_dir / sourceItem.source
        plasTeX.Logging.disableLogging()

        wd = os.getcwd()
        os.chdir(str(outPath))

        plastex_config['files']['filename'] = sourceItem.url
        plastex_config['general']['paux-dirs'] = [outPaux]
        doc = TeXDocument(config=plastex_config)
        doc.userdata['working-dir'] = '.'
        doc.context.importMacros({"numbas": macros.numbas, "youtube": macros.youtube, "vimeo": macros.vimeo, "embed": macros.embed, "math": macros.math})

        with open(str(Path(wd) / inPath)) as f:
            tex = TeX(doc, myfile=f)
            doc.userdata['jobname'] = tex.jobname
            pauxname = os.path.join(doc.userdata.get('working-dir','.'),
                                '%s.paux' % doc.userdata.get('jobname',''))
            tex.parse()

        renderer = Renderer()
        renderer.loadTemplates(doc)
        renderer.importDirectory(str(self.theme.source / 'plastex'))
        renderer.render(doc)
 
        os.chdir(wd)
