import logging
import shutil
import os
import re
from . import latex, mkdir_p
from .pandoc import pandoc_item
from .render import Renderer
from pathlib import Path

logger = logging.getLogger(__name__)

class ItemProcess(object):
    """ 
        Performs a process on each item in the course structure. 
        Visits each item in a depth-first search.
    """

    name = ''
    num_runs = 1

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

class LastBuiltProcess(ItemProcess):
    name = 'Establish when each item was last built'

    def visit_default(self, item):
        item.source_modified = (self.course.get_root_dir() / item.source).stat().st_mtime

        outPath = self.course.get_build_dir() / item.out_file
        if outPath.exists():
            item.last_built = outPath.stat().st_mtime
        else:
            item.last_built = None

    def visit_url(self, item):
        pass

class RenderProcess(ItemProcess):

    name = 'Render items to HTML'
    num_runs = 2

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
        elif ext == '.md':
            pandoc_item(self.course, item, template_file='notes.latex', out_format='pdf', force_local=True)
        item.has_pdf = True
