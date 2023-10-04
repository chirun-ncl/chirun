import logging
from . import slugify
from .render import Renderer, SlidesRenderer, NotebookRenderer
from .latex import PDFLatex
import asyncio

logger = logging.getLogger(__name__)


class ItemProcess(object):
    """
        Performs a process on each item in the course structure.
        Visits each item in a depth-first search.
    """

    name = ''
    num_runs = 1

    def __init__(self, course):
        self.course = course
        self.renderer = Renderer(self.course)
        self.slides_renderer = SlidesRenderer(self.course)
        self.nb_renderer = NotebookRenderer(self.course)

    def visit(self, item):
        fn = getattr(self, 'visit_' + item.type)
        return fn(item)

    def __getattr__(self, name):
        if name[:6] == 'visit_':
            return self.visit_default
        else:
            raise AttributeError

    def visit_default(self, item):
        """ Default visit method, used when a type-specific visit method isn't defined """
        pass

    def visit_part(self, item):
        for subitem in item.content:
            self.visit(subitem)

class SlugCollisionProcess(ItemProcess):
    name = 'Checking for duplicated filenames or paths'
    slugs = {}

    def visit(self, item):
        logger.debug("Checking slug: {}".format(item.slug))

        if self.course.theme.path not in self.slugs.keys():
            self.slugs[self.course.theme.path] = []

        n = 1
        oldslug = item.slug
        newslug = None
        while item.slug in self.slugs[self.course.theme.path]:
            newslug = slugify(item.title, n)
            item.slug = newslug
            n = n + 1

        if newslug is not None:
            logger.info(f"Slug changed from {oldslug} to {item.slug}")

        self.slugs[self.course.theme.path].append(item.slug)
        super().visit(item)


class LastBuiltProcess(ItemProcess):
    name = 'Establish when each item was last built'

    def visit_default(self, item):
        item.config_modified = self.course.get_main_file().stat().st_mtime
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit_default(self, item):
        self.course.force_relative_build = False
        self.renderer.render_item(item)

    def visit_part(self, item):
        self.visit_default(item)
        super().visit_part(item)

    def visit_document(self, item):
        item.generate_chapter_subitems()
        self.visit_default(item)
        super().visit_part(item)

    def visit_standalone(self, item):
        self.visit_document(item)

    def visit_url(self, item):
        pass

    def visit_slides(self, item):
        ext = item.source.suffix
        self.slides_renderer.render_item(item)

class PDFProcess(ItemProcess):

    name = 'Make PDFs'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_runs = self.course.config['num_pdf_runs']

    def visit(self, item):
        self.course.force_relative_build = True
        super().visit(item)

    def visit_document(self, item):
        if not item.has_pdf:
            return
        ext = item.source.suffix
        if ext == '.tex':
            item.toc = PDFLatex(self.course, item).process_split_pdf()
        elif ext == '.md':
            self.makePDF(item)

    def visit_chapter(self, item):
        self.makePDF(item)

    def visit_notebook(self, item):
        self.makePDF(item)

    def visit_exam(self, item):
        self.makePDF(item)

    def visit_standalone(self, item):
        self.visit_document(item)

    def visit_slides(self, item):
        ext = item.source.suffix
        if ext == '.tex':
            PDFLatex(self.course, item).process_pdf()
        elif ext == '.md':
            asyncio.get_event_loop().run_until_complete(self.slides_renderer.to_pdf(item))

    def makePDF(self, item):
        if not item.has_pdf:
            return
        ext = item.source.suffix
        if ext == '.tex':
            PDFLatex(self.course, item).process_pdf()
        elif ext == '.md':
            asyncio.get_event_loop().run_until_complete(self.renderer.to_pdf(item))


class NotebookProcess(ItemProcess):

    name = 'Render items to Jupyter Notebook'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit_default(self, item):
        pass

    def visit_notebook(self, item):
        self.course.force_relative_build = False
        self.nb_renderer.render_item(item)
