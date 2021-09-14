import logging
import re
from makeCourse.markdownRenderer import MarkdownRenderer
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
    source_modified = None
    last_built = None
    has_footer = True
    has_topbar = True
    has_pdf = False
    splitlevel = -2

    def __init__(self, course, data, parent=None):
        self.course = course
        self.parent = parent
        self.data = data
        self.title = self.data.get('title', self.title)
        self.slug = slugify(self.title)
        self.author = self.data.get('author', self.parent.author if self.parent else self.course.config.get('author'))
        self.source = Path(self.data.get('source', ''))
        self.is_hidden = self.data.get('hidden', False)
        self.has_topbar = self.data.get('topbar', self.has_topbar)
        self.has_footer = self.data.get('footer', self.has_footer)
        self.thumbnail = self.data.get('thumbnail', None)
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
        if self.in_file.suffix == '.md':
            return self.last_built is not None and self.last_built > self.source_modified

        elif self.in_file.suffix == '.tex':
            if self.has_pdf:
                extensions = ['.log', '.aux', '.out', '.bbl', '.snm', '.nav', '.toc', '.fls']
                in_dir = self.course.get_root_dir() / self.source.parent
                fls_filename = in_dir / self.in_file.with_suffix('.fls')

                if not fls_filename.exists() or self.last_built is None:
                    return False

                with open(fls_filename) as f:
                    for line in f:
                        if 'INPUT' in line:
                            input_file = Path(line[6:-1])
                            if not input_file.is_absolute():
                                input_file = in_dir / input_file
                            if not input_file.exists():
                                return False
                            if input_file.stat().st_mtime > self.last_built and input_file.suffix not in extensions:
                                return False
                return True
            else:
                return self.last_built is not None and self.last_built > self.source_modified

        else:
            return False

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
    def plastex_filename_rules(self):
        return self.out_file

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
    def breadcrumbs(self):
        if self.parent is None:
            return [self]
        else:
            return self.parent.breadcrumbs + [self]

    @property
    def base_file(self):
        return Path(self.in_file.stem)

    def markdown_content(self, out_format='html'):
        if 'html' in self.data:
            return self.data['html']

        body = ''
        if 'source' in self.data:
            ext = self.source.suffix
            if ext == '.md':
                with open(str(self.course.get_root_dir() / self.source), encoding='utf-8') as f:
                    mdContents = f.read()
                if mdContents[:3] == '---':
                    logger.info('    Note: Markdown file {} contains a YAML header. It will be merged in...'.format(self.source))
                    mdContents = re.sub(r'^---.*?---\n', '', mdContents, re.S)
                body = mdContents
            elif ext == '.tex':
                plastex_output = self.course.load_latex_content(self)
                body = plastex_output['index.html']['html']
            else:
                raise Exception("Error: Unrecognised source type for {}: {}.".format(self.title, self.source))

        return body

    def as_html(self):
        if 'html' in self.data:
            return self.data['html']

        html = ''
        if 'source' in self.data:
            ext = self.source.suffix
            if ext == '.md':
                outPath = (self.course.get_build_dir() / self.out_file).parent
                html = self.markdownRenderer.render(self, outPath)
            elif ext == '.tex':
                plastex_output = self.course.load_latex_content(self)
                html = plastex_output['index.html']['html']
            else:
                raise Exception("Error: Unrecognised source type for {}: {}.".format(self, self.source))

        html = burnInExtras(self, html, out_format='html')
        return html

    def temp_path(self):
        """
            Path to a temporary directory which can store files produced while processing this item
        """
        return self.course.temp_path(self.url.replace('/','-'))

    def content_tree(self):
        if self.content:
            return {'type': self.type, 'slug': self.slug, 'title': self.title, 'content': [item.content_tree() for item in self.content]}
        else:
            return {'type': self.type, 'slug': self.slug, 'title': self.title, 'source': str(self.source)}

class Html(Item):
    type = 'html'
    title = 'Untitled'
    template_name = 'chapter.html'
    has_sidebar = False
    pdf_url = False

    @property
    def out_path(self):
        path = ''
        if self.parent:
            path = self.parent.out_path / path
        return path

    @property
    def out_file(self):
        return self.out_path / self.in_file

    def markdown_content(self,*args,**kwargs):
        return self.data.get('html', '')

    def as_html(self):
        return self.data.get('html', '')

class Part(Item):
    type = 'part'
    title = 'Untitled part'
    template_name = 'part.html'
    pdf_url = False

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.leading_text = self.data.get('leading_text', '')
        self.location = self.data.get('location', 'below')

    def get_context(self):
        context = super().get_context()
        context.update({
            'part-slug': self.slug,
            'chapters': [item.get_context() for item in self.content if not item.is_hidden],
        })
        return context

class Document(Item):
    type = 'document'
    title = 'Untitled part'
    template_name = 'part.html'
    splitlevel = 0
    generated = False
    has_sidebar = True
    has_topbar = True

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.has_sidebar = self.data.get('sidebar', self.has_sidebar)
        self.has_topbar = self.data.get('topbar', self.has_topbar)
        self.splitlevel = self.data.get('splitlevel', self.splitlevel)
        self.has_pdf = self.course.config['build_pdf']

    def generate_chapter_subitems(self):
        ext = self.source.suffix

        def copy_attrs(item):
            item.last_built = self.last_built
            item.has_sidebar = self.has_sidebar
            item.has_topbar = self.has_topbar
            item.has_pdf = self.course.config['build_pdf']
            item.pdf_url = self.pdf_url

        if ext == '.tex':
            if not self.generated:
                self.generated = True
                plastex_output = self.course.load_latex_content(self)
                last_item = {-1:self}
                for fn, chapter in plastex_output.items():
                    chapter['html'] = burnInExtras(self, chapter['html'], out_format='html')
                    if chapter['html'].isspace():
                        chapter['html'] = ''
                    if chapter['level'] < 0:
                        self.data['html'] = chapter['html']
                        last_item[-1] = self
                    elif chapter['level'] < self.splitlevel:
                        i = -1
                        while i < chapter['level']:
                            if i in last_item:
                                parent = last_item[i]
                            i = i + 1
                        item = Part(self.course, chapter, parent)
                        copy_attrs(item)
                        last_item[chapter['level']] = item
                        parent.content.append(item)
                    elif chapter['level'] == self.splitlevel:
                        i = -1
                        while i < chapter['level']:
                            if i in last_item:
                                parent = last_item[i]
                            i = i + 1
                        item = Html(self.course, chapter, self)
                        copy_attrs(item)
                        parent.content.append(item)
        else:
            raise Exception("Error: Unrecognised source type used for LaTeX Document item {}: {}.".format(self.title, self.source))

    @property
    def plastex_filename_rules(self):
        fnstr = self.out_path / '[$id, $title(4), $num(4)]'
        return '%s %s'%(self.out_file, fnstr)

    def get_context(self):
        context = super().get_context()
        context.update({
            'part-slug': self.slug,
            'chapters': [item.get_context() for item in self.content if not item.is_hidden],
            'pdf': '{}.pdf'.format(self.url),
        })
        return context

class Url(Item):
    type = 'url'
    title = 'Untitled URL'
    template_name = 'part.html'

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.source = self.data.get('source', '')
        self.data['html'] = ''

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
    has_topbar = True

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.has_sidebar = self.data.get('sidebar', self.has_sidebar)

    def get_context(self):
        context = super().get_context()
        context.update({
            'build_pdf': self.course.config['build_pdf'],
            'file': '{}.html'.format(self.url),
            'pdf': '{}.pdf'.format(self.url),
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
        self.title_slide = self.data.get('title_slide', True)

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

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.leading_text = self.data.get('leading_text', '')

    def __str__(self):
        return 'introduction'

    out_path = Path('')
    out_file = Path('index.html')
    url = ''

    def get_context(self):
        context = super().get_context()
        context['links'] = [s.get_context() for s in self.course.structure if s.type != 'introduction' and not s.is_hidden]

        struct = [s for s in self.course.structure if s.type != 'introduction' and not s.is_hidden]
        if len(struct) > 0 and struct[0].type == 'part':
            context['isPart'] = 1

        return context

class Standalone(Chapter):
    type = 'standalone'
    title = 'document'
    out_path = Path('')
    out_file = Path('index.html')
    url = ''

item_types = {
    'introduction': Introduction,
    'part': Part,
    'document': Document,
    'chapter': Chapter,
    'standalone': Standalone,
    'url': Url,
    'html': Html,
    'slides': Slides,
    'recap': Recap,
    'exam': Exam,
}


