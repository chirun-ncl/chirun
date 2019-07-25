import logging
from . import latex
from .item import load_item
from pathlib import Path
import os
import re
from makeCourse import mkdir_p
from .pandoc import pandoc_item
from .render import Renderer

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

class RenderProcess(ItemProcess):

    name = 'Run pandoc'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.renderer = Renderer(self.course)

    def visit_default(self, item):
        self.renderer.render_item(item)

    def visit_part(self, item):
        self.visit_default(item)
        for subitem in item.content:
            self.visit(subitem)

    def visit_url(self, item):
        pass

#    def visit_slides(self, item):
#        pandoc_item(self.course, item)
#        pandoc_item(self.course, item, template_file='slides.revealjs', out_format='slides.html', force_local=self.course.args.local)

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

    def temp_path(self, subpath=None):
        path = Path('tmp') / self.theme.path

        if subpath:
            path = path / subpath

        mkdir_p(path)
        return path


    def makePDF(self, item):
        ext = item.source.suffix
        if ext == '.tex':
            latex.runPdflatex(self, item)
        elif item.type == 'slides':
            self.run_decktape(item)
        else:
            pandoc_item(self.course, item, template_file='notes.latex', out_format='pdf', force_local=True)

    processor_classes = [RenderProcess, PDFProcess]

    def process(self):
        logger.debug("Starting processing...")

        logger.debug('Preprocessing Structure...')
        self.structure = [load_item(self, obj) for obj in self.config['structure']]

        logger.debug('Deep exploring Structure...')

        self.partsEnabled = False
        for item in self.structure:
            if item.type=='part':
                self.partsEnabled = True
                break
        if self.partsEnabled:
            for item in self.structure:
                if item.type not in ['introduction','part']:
                    raise Exception("Error: Both parts and chapters found at top level. To fix: put all chapters inside parts or don't include parts at all. Quitting...\n")

        processors = [p(self) for p in self.processor_classes]
        for processor in processors:
            logger.info(processor.name+'\n'+'-'*len(processor.name))
            for item in self.structure:
                processor.visit(item)

        logger.debug('Done processing!')
