import logging
import re
import os
import shutil
import sys
from makeCourse import mkdir_p
from pathlib import Path
from subprocess import Popen, PIPE
from plasTeX import TeXDocument
from plasTeX.Renderers.HTML5ncl import Renderer
from plasTeX.TeX import TeX
from plasTeX.Config import config as plastex_config
import plasTeX.Renderers.HTML5.Config as html_config

plastex_config += html_config.config

logger = logging.getLogger(__name__)

def fixPlastexQuirks(text):
    # Stop markdown from listifying things.
    reItemList = re.compile(r'<p>\s*([\(\[]*)([A-z0-9]{1,3})([\)\]\.\:])')
    text = reItemList.sub(lambda m: '<p>' + m.group(1) + m.group(2) + "\\" + m.group(3), text)

    # Stop pandoc from interpreting plastex output as code
    reStartSpaces = re.compile(r'^ +', re.M)
    text = reStartSpaces.sub('', text)
    reSmartQuotes = re.compile(r'`(.*?)\'')
    text = reSmartQuotes.sub(lambda m: "\'" + m.group(1) + "\'", text)

    # Remove empty paragraphs
    reEmptyP = re.compile(r'<p></p>')
    text = reEmptyP.sub('', text)

    return text

def getEmbeddedImages(course, html, sourceItem):
    title = sourceItem.title
    logger.debug('    Moving embedded images:')
    # Markdown Images

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
        finalURL = Path('images') / inFile
        outPath = course.get_build_dir() / sourceItem.out_file.parent / finalURL
        #logger.debug('        %s => %s' % (inPath, outPath))

        # Move the file into build tree's static dir
        mkdir_p(outPath.parent)
        shutil.copyfile(str(inPath), str(outPath))

        # Update the output of plastex to reflect the change
        start, end = m.span('url')
        start -= m.start()
        end -= m.start()
        img = m.group(0)
        return img[:start] + str(finalURL) + img[end:]

    for pattern in patterns:
        html = pattern.sub(fix_image_path, html)

    return html
class PlastexRunner:

    tmpDir = ''

    def load_latex_content(self, sourceItem):
        """
            Convert a LaTeX file to HTML, and do some processing with its images
        """
        tmpDir = sourceItem.temp_path()
        self.runPlastex(sourceItem)

        # All the paux files for the course are collected in the temp_path
        original_paux_path = sourceItem.temp_path() / sourceItem.base_file.with_suffix('.paux')
        collated_paux_path = self.temp_path() / (str(sourceItem.out_file).replace('/','-') + '.paux')
        logger.debug('    Moving paux output: {original_paux_path} => {collated_paux_path}'.format(
            original_paux_path=original_paux_path,
            collated_paux_path=collated_paux_path
        ))
        shutil.move(str(original_paux_path), str(collated_paux_path))

        root_dir = self.get_root_dir()

        source_file = root_dir / tmpDir / sourceItem.url
        with open(str(source_file), encoding='utf-8') as f:
            html = f.read()
        # TODO: an abstraction for applying the following as a series of filters
        html = fixPlastexQuirks(html)
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
        outPath = root_dir / sourceItem.temp_path()
        outPaux = root_dir / self.temp_path()
        inPath = root_dir / sourceItem.source

        wd = os.getcwd()
        os.chdir(outPath)

        plastex_config['files']['filename'] = sourceItem.url
        plastex_config['general']['paux-dirs'] = [outPaux]
        doc = TeXDocument(config=plastex_config)
        doc.userdata['working-dir'] = '.'

        with open(Path(wd) / inPath) as f:
            tex = TeX(doc, myfile=f)
            doc.userdata['jobname'] = tex.jobname
            pauxname = os.path.join(doc.userdata.get('working-dir','.'),
                                '%s.paux' % doc.userdata.get('jobname',''))
            tex.parse()

        Renderer().render(doc)
 
        os.chdir(wd)
