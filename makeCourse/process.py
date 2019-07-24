import logging
from . import latex
from .item import load_item
from pathlib import Path
import os
import re
from makeCourse import mkdir_p, gen_dict_extract

logger = logging.getLogger(__name__)

class ItemProcess(object):
    """ 
        Performs a process on each item in the course structure. 
        Visits each item in a depth-first search.
    """

    name = ''

    def __init__(self,course):
        self.course = course

    def visit(self, item):
        if item.is_hidden:
            return
        logging.info("Processing {}".format(item))
        fn = getattr(self,'visit_'+item.type)
        return fn(item)

    def __getattr__(self, name):
        if name[:6]=='visit_':
            return self.visit_default
        else:
            raise AttributeError

    def visit_default(self, item):
        """ Default visit method, used when a type-specific visit method isn't defined """
        pass

class PandocProcess(ItemProcess):

    name = 'Run pandoc'

    def visit_default(self, item):
        self.course.run_pandoc(item)

    def visit_part(self, item):
        self.visit_default(item)
        for subitem in item.content:
            self.visit(subitem)

    def visit_url(self, item):
        pass

    def visit_slides(self, item):
        self.course.run_pandoc(item)
        self.course.run_pandoc(item, template_file='slides.revealjs', out_format='slides.html', force_local=self.course.args.local)

class PDFProcess(ItemProcess):

    name = 'Make PDFs'
    
    def visit(self,item):
        if not self.course.config['build_pdf']:
            return
        super().visit(item)

    def visit_chapter(self, item):
        self.course.makePDF(item)

    def visit_slides(self, item):
        self.course.makePDF(item)

class CourseProcessor:

    def temp_path(self, sourceItem=False):
        tmp_dir = Path('tmp')
        if not tmp_dir.exists():
            os.makedirs(str(tmp_dir))

        tmp_theme_dir = tmp_dir / self.theme.path
        if not tmp_theme_dir.exists():
            os.makedirs(str(tmp_theme_dir))

        if sourceItem:
            tpath = tmp_theme_dir / re.sub('/', '-', sourceItem.url)
        else:
            tpath = tmp_theme_dir
        return tpath

    def replaceLabels(self, mdContents):
        for l in gen_dict_extract('label', self.config):
            mdLink = re.compile(r'\[([^\]]*)\]\(' + l['label'] + r'\)')
            mdContents = mdLink.sub(lambda m: "[" + m.group(1) + "](" + self.get_web_root() + l['outFile'] + ".html)", mdContents)
        return mdContents

    def getVimeoHTML(self, code):
        return '<div class="vimeo-aspect-ratio"><iframe class="vimeo" src="https://player.vimeo.com/video/' + code + '" frameborder="0" \
				webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>'

    def getRecapHTML(self, code):
        return '<div class="recap-aspect-ratio"><iframe class="recap" src="https://campus.recap.ncl.ac.uk/Panopto/Pages/Embed.aspx?id=' + code + '&v=1" \
				frameborder="0" gesture=media webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>'

    def getYoutubeHTML(self, code):
        return '<div class="youtube-aspect-ratio"><iframe class="youtube" src="https://www.youtube.com/embed/' + code + '?ecver=1" \
				frameborder="0" allowfullscreen></iframe></div>'

    def getNumbasHTML(self, URL):
        return '<iframe class="numbas" src="' + URL + '" frameborder="0"></iframe>'

    def burnInExtras(self, mdContents, force_local, out_format):
        mdContentsOrig = mdContents
        reVimeo = re.compile(r'{%vimeo\s*([\d\D]*?)\s*%}')
        reRecap = re.compile(r'{%recap\s*([\d\DA-z-]*?)\s*%}')
        reYoutube = re.compile(r'{%youtube\s*([\d\D]*?)\s*%}')
        reNumbas = re.compile(r'{%numbas\s*([^%{}]*?)\s*%}')
        reSlides = re.compile(r'{%slides\s*([^%{}]*?)\s*%}')
        if out_format == 'pdf':
            mdContents = reVimeo.sub(lambda m: r"\n\n\url{https://vimeo.com/" + m.group(1) + "}", mdContents)
            mdContents = reRecap.sub(lambda m: r"\n\n\url{https://campus.recap.ncl.ac.uk/Panopto/Pages/Viewer.aspx?id=" + m.group(1) + "}", mdContents)
            mdContents = reYoutube.sub(lambda m: r"\n\n\url{https://www.youtube.com/watch?v=" + m.group(1) + "}", mdContents)
            mdContents = reNumbas.sub(lambda m: r"\n\n\url{" + m.group(1) + "}", mdContents)
            mdContents = reSlides.sub(lambda m: r"\n\n\url{" + self.getSlidesURL(m.group(1)) + "}", mdContents)
        else:
            mdContents = reVimeo.sub(lambda m: self.getVimeoHTML(m.group(1)), mdContents)
            mdContents = reRecap.sub(lambda m: self.getRecapHTML(m.group(1)), mdContents)
            mdContents = reYoutube.sub(lambda m: self.getYoutubeHTML(m.group(1)), mdContents)
            mdContents = reNumbas.sub(lambda m: self.getNumbasHTML(m.group(1)), mdContents)

        if force_local:
            relativeImageDir = self.get_local_root() + self.theme.path + "/static/"
        else:
            relativeImageDir = self.get_web_root() + self.theme.path + "/static/"

        logger.debug("    Webize images: replacing './build/static/' with '%s' in paths." % relativeImageDir)
        mdContents = mdContents.replace('./build/static/', relativeImageDir)

        if mdContents != mdContentsOrig:
            logger.debug('    Embedded iframes & extras.')
        mdContents = self.replaceLabels(mdContents)
        return mdContents

    def makePDF(self, item):
        ext = item.source.suffix
        if ext == '.tex':
            latex.runPdflatex(self, item)
        elif item.type == 'slides':
            self.run_decktape(item)
        else:
            self.run_pandoc(item, template_file='notes.latex', out_format='pdf', force_local=True)

    processor_classes = [PandocProcess, PDFProcess]

    def process(self):
        logger.debug("Starting processing...")

        logger.debug('Preprocessing Structure...')
        self.structure = [load_item(self, obj) for obj in self.config['structure']]

        logger.debug('Deep exploring Structure...')

        partsEnabled = False
        for item in self.structure:
            if item.type=='part':
                partsEnabled = True
                break
        if partsEnabled:
            for item in self.structure:
                if item.type not in ['introduction','part']:
                    raise Exception("Error: Both parts and chapters found at top level. To fix: put all chapters inside parts or don't include parts at all. Quitting...\n")

        processors = [p(self) for p in self.processor_classes]
        for processor in processors:
            logger.info(processor.name+'\n'+'-'*len(processor.name))
            for item in self.structure:
                processor.visit(item)

        logger.debug('Done processing!')
