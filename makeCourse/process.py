import logging
import shutil
import os
import re
from . import latex, mkdir_p
from .render import Renderer, SlidesRenderer
from pathlib import Path
import asyncio

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
        self.renderer = Renderer(self.course)
        self.slides_renderer = SlidesRenderer(self.course)

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
        item.last_built = None

class RenderProcess(ItemProcess):

    name = 'Render items to HTML'
    num_runs = 2

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def visit_default(self, item):
        self.course.force_relative_build = False
        self.renderer.render_item(item)

    def visit_part(self, item):
        self.visit_default(item)
        super().visit_part(item)

    def visit_url(self, item):
        pass

    def visit_slides(self, item):
        item.has_slides = True
        self.slides_renderer.render_item(item)

class PDFProcess(ItemProcess):

    name = 'Make PDFs'
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def visit(self,item):
        if not self.course.config['build_pdf']:
            return
        self.course.force_relative_build = True
        super().visit(item)

    def visit_chapter(self, item):
        item.has_pdf = True
        self.makePDF(item)

    def visit_exam(self, item):
        item.has_pdf = True
        self.makePDF(item)

    def visit_standalone(self, item):
        item.has_pdf = True
        self.makePDF(item)

    def visit_slides(self, item):
        item.has_pdf = True
        ext = item.source.suffix
        if ext == '.tex':
            latex.runPdflatex(self.course, item)
        elif ext == '.md':
            asyncio.get_event_loop().run_until_complete(self.slides_renderer.to_pdf(item))

    def makePDF(self, item):
        ext = item.source.suffix
        if ext == '.tex':
            latex.runPdflatex(self.course, item)
        elif ext == '.md':
            asyncio.get_event_loop().run_until_complete(self.renderer.to_pdf(item))
