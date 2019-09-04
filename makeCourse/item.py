import logging
import re
from makeCourse.markdownRenderer import MarkdownRenderer,SlidesMarkdownRenderer
from pathlib import Path, PurePath
from . import slugify
from .filter import burnInExtras

logger = logging.getLogger(__name__)

def load_item(course, data, parent=None):
    try:
        item_type = data['type']
    except KeyError:
        raise Exception("Item has undefined type")

    try:
        constructor = item_types[item_type]
    except KeyError:
        raise Exception("Unknown item type {}".format(data['type']))

    return constructor(course, data, parent)

class Item(object):
    template_name = 'item.html'
    type = None
    source_mtime = None
    last_built = None

    def __init__(self, course, data, parent=None):
        self.course = course
        self.parent = parent
        self.data = data
        self.title = self.data.get('title', self.title)
        self.slug = slugify(self.title)
        self.source = Path(self.data.get('source', ''))
        self.is_hidden = self.data.get('hidden', False)
        self.content = [load_item(course, obj, self) for obj in self.data.get('content', [])]
        self.markdownRenderer = MarkdownRenderer()

    def __str__(self):
        return '{} "{}"'.format(self.type, self.title)

    def get_context(self):
        context = {
            'title': self.title,
            'slug': self.slug,
        }
        return context

    def recently_built(self):
        """
            Has this item been built since the source was last modified?
        """
        return self.last_built is not None and self.last_built > self.source_modified

    @property
    def out_path(self):
        path = PurePath(self.slug)
        if self.parent:
            path = self.parent.out_path / path
        return path

    @property
    def out_file(self):
        return self.out_path / 'index.html'

    @property
    def named_out_file(self):
        return self.out_path / PurePath(self.slug)

    @property
    def url(self):
        return str(self.out_file)

    @property
    def pdf_url(self):
        return str(self.named_out_file.with_suffix('.pdf'))

    @property
    def in_file(self):
        base = Path(self.source.name)
        return base

    @property
    def base_file(self):
        return Path(self.in_file.stem)

    def markdown_content(self, out_format='html'):
        ext = self.source.suffix

        if ext == '.md':
            with open(str(self.course.get_root_dir() / self.source), encoding='utf-8') as f:
                mdContents = f.read()
            if mdContents[:3] == '---':
                logger.info('    Note: Markdown file {} contains a YAML header. It will be merged in...'.format(self.source))
                mdContents = re.sub(r'^---.*?---\n', '', mdContents, re.S)
            body = mdContents
        elif ext == '.tex':
            body = self.course.load_latex_content(self)
        else:
            raise Exception("Error: Unrecognised source type for {}: {}.".format(self.title, self.source))

        return body

    def as_html(self):
        ext = self.source.suffix
        
        if ext == '.md':
            html = self.markdownRenderer.render(self.markdown_content())
        elif ext == '.tex':
            html = self.course.load_latex_content(self)
        else:
            raise Exception("Error: Unrecognised source type for {}: {}.".format(self, self.source))

        html = burnInExtras(self.course, html, out_format='html')
        return html

    def temp_path(self):
        """
            Path to a temporary directory which can store files produced while processing this item
        """
        return self.course.temp_path(self.url.replace('/','-'))

class NoContentMixin:
    def markdown_content(self,*args,**kwargs):
        return ''

    def as_html(self):
        return ''

class Part(NoContentMixin, Item):
    type = 'part'
    title = 'Untitled part'
    template_name = 'part.html'

    def get_context(self):
        context = super().get_context()
        context.update({
            'part-slug': self.slug,
            'chapters': [item.get_context() for item in self.content if not item.is_hidden],
        })
        return context

class Url(NoContentMixin, Item):
    type = 'url'
    title = 'Untitled URL'
    template_name = 'part.html'

    def get_context(self):
        return {
            'title': self.title,
            'external_url': self.source,
        }


class Chapter(Item):
    type = 'chapter'
    title = 'Untitled chapter'
    template_name = 'chapter.html'
    template_pdfheader = 'print_header.html'
    template_pdffooter = 'print_footer.html'

    has_sidebar = True

    def get_context(self):
        context = super().get_context()
        context.update({
            'build_pdf': self.course.config['build_pdf'],
            'file': '{}.html'.format(self.url),
            'pdf': '{}.pdf'.format(self.url),
            'sidebar': self.has_sidebar,
        })

        if self.parent:
            context['part'] = self.parent.title
            context['part-slug'] = self.parent.slug

        return context

    def siblings(self):
        if self.parent:
            return self.parent.content
        else:
            return [item for item in self.course.structure if item.type != 'introduction']

class Exam(Chapter):
    type = 'exam'
    title = 'Untitled exam'
    template_name = 'exam.html'
    has_sidebar = False

class Slides(Chapter):
    type = 'slides'
    title = 'Untitled Slides'
    template_name = 'slides.html'
    template_slides = 'slides_reveal.html'

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.markdownRenderer = SlidesMarkdownRenderer()

    def get_context(self):
        context = super().get_context()
        context.update({
            'slides': '{}.slides.html'.format(self.url),
            'pdf': '{}.pdf'.format(self.url),
        })
        return context

    @property
    def out_slides(self):
      return self.named_out_file.with_suffix('.slides.html')

    @property
    def slides_url(self):
      return str(self.out_slides)

class Recap(Chapter):
    type = 'recap'
    title = 'Untitled Recap'
    template_name = 'chapter.html'
    has_sidebar = False

    def get_context(self):
        context = super().get_context()
        context.update({
            'build_pdf': False,
        })
        return context


class Introduction(Item):
    type = 'introduction'
    template_name = 'index.html'
    title = 'index'

    def __str__(self):
        return 'introduction'

    out_path = Path('')
    out_file = 'index.html'
    url = ''

    def get_context(self):
        context = super().get_context()
        context['links'] = [s.get_context() for s in self.course.structure if s.type != 'introduction' and not s.is_hidden]

        struct = [s for s in self.course.structure if s.type != 'introduction' and not s.is_hidden]
        if len(struct) > 0 and struct[0].type == 'part':
            context['isPart'] = 1

        return context


item_types = {
    'introduction': Introduction,
    'part': Part,
    'chapter': Chapter,
    'url': Url,
    'slides': Slides,
    'recap': Recap,
    'exam': Exam,
}


