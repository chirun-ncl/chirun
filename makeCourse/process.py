import logging
from . import latex
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

    def visit_part(self, item):
        for subitem in item.content:
            self.visit(subitem)

class RenderProcess(ItemProcess):

    name = 'Render items to HTML'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.renderer = Renderer(self.course)

    def visit_default(self, item):
        self.renderer.render_item(item)

    def visit_part(self, item):
        self.visit_default(item)
        super().visit_part(item)

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
        self.makePDF(item)

    def visit_slides(self, item):
        self.makePDF(item)

    def makePDF(self, item):
        ext = item.source.suffix
        if ext == '.tex':
            latex.runPdflatex(self.course, item)
        elif item.type == 'slides':
            self.course.run_decktape(item)
        else:
            pandoc_item(self.course, item, template_file='notes.latex', out_format='pdf', force_local=True)
        item.has_pdf = True
