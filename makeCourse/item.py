import logging
import re
import yaml
from makeCourse.markdownRenderer import MarkdownRenderer
from pathlib import Path, PurePath
from . import slugify
from .filter import HTMLFilter

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
    splitlevel = -2
    is_index = False

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
        self.has_pdf = self.data.get('build_pdf', False)
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
        if self.in_file.suffix in ['.md', '.html', '.htm']:
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
        if 'pdf_url' in self.data:
            return self.data['pdf_url']
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
                    logger.info('    Note: Markdown file {} contains a YAML header. It will be merged in...'
                                .format(self.source))
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
            elif ext == '.html':
                with open(str(self.course.get_root_dir() / self.source), encoding='utf-8') as f:
                    html = f.read()
            else:
                raise Exception("Error: Unrecognised source type for {}: {}.".format(self, self.source))

        html = HTMLFilter().apply(self, html, out_format='html')
        return html

    def temp_path(self):
        """
            Path to a temporary directory which can store files produced while processing this item
        """
        return self.course.temp_path(self.url.replace('/', '-'))

    def content_tree(self):
        attr_dict = {
            'type': self.type,
            'slug': self.slug,
            'title': self.title,
            'source': str(self.source),
            'pdf_url': self.pdf_url,
            'build_pdf': self.has_pdf,
        }
        return attr_dict


class Html(Item):
    type = 'html'
    title = 'Untitled'
    template_name = 'chapter.html'
    has_sidebar = False

    @property
    def out_path(self):
        path = ''
        if self.parent:
            path = self.parent.out_path / path
        return path

    @property
    def out_file(self):
        return self.out_path / self.in_file


class Part(Item):
    type = 'part'
    title = 'Untitled part'
    template_name = 'part.html'

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.leading_text = self.data.get('leading_text', '')
        self.location = self.data.get('location', 'below')

    def recently_built(self):
        config_stable = self.last_built is not None and self.last_built > self.config_modified
        return super().recently_built() and config_stable

    def get_context(self):
        context = super().get_context()
        context.update({
            'part-slug': self.slug,
            'chapters': [item.get_context() for item in self.content if not item.is_hidden],
        })
        return context

    def content_tree(self):
        attr_dict = super().content_tree()
        attr_dict['content'] = [item.content_tree() for item in self.content]
        return attr_dict


class Document(Item):
    type = 'document'
    title = 'Untitled part'
    template_name = 'part.html'
    splitlevel = 0
    generated = False
    has_sidebar = True
    has_topbar = True

    @property
    def out_struct_file(self):
        return self.source.with_suffix('.dst')

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.has_sidebar = self.data.get('sidebar', self.has_sidebar)
        self.has_topbar = self.data.get('topbar', self.has_topbar)
        self.splitlevel = self.data.get('splitlevel', self.splitlevel)
        self.has_pdf = self.data.get('build_pdf', self.course.config['build_pdf'])

    def recently_built(self):
        if self.out_struct_file.exists():
            logger.debug('Loading document structure from cache file: {}'.format(self.out_struct_file))
            with open(str(self.out_struct_file), 'r') as f:
                try:
                    self.cached_struct = yaml.load(f, Loader=yaml.CLoader)
                except AttributeError:
                    self.cached_struct = yaml.load(f, Loader=yaml.Loader)
        return super().recently_built() and self.cached_struct.get('splitlevel', -2) == self.splitlevel

    def generate_chapter_subitems(self):
        ext = self.source.suffix

        def copy_attrs(item):
            item.last_built = self.last_built
            item.has_sidebar = self.has_sidebar
            item.has_topbar = self.has_topbar
            item.source_modified = self.source_modified
            item.config_modified = self.config_modified
            for subitem in item.content:
                copy_attrs(subitem)

        def setup_pdf_url(item, chapter):
            replace_words = ["appendix", "bibliography"]
            item.has_pdf = self.has_pdf
            if item.has_pdf:
                item_code = "{}.{}".format(chapter['counter'], chapter['ref'])
                # Match by TOC code
                tocitem = next((e for e in self.toc if e.code == item_code), None)

                # Match other close TOC entries
                for w in replace_words:
                    if not tocitem:
                        tocitem = next((e for e in self.toc if e.code == item_code.replace("chapter", w)), None)
                    if not tocitem:
                        tocitem = next((e for e in self.toc if e.code == item_code.replace("section", w)), None)

                # Match by title
                if not tocitem:
                    tocitem = next((e for e in self.toc if e.title == item.title), None)

                # Match by docstart
                if not tocitem and not self.content:
                    tocitem = next((e for e in self.toc), None)

                if tocitem:
                    item.data['pdf_url'] = str(self.out_path / Path('pdf') / Path(tocitem.slug).with_suffix('.pdf'))
                else:
                    item.data.pop('pdf_url', None)
                    item.has_pdf = False

        def run_plastex_for_structure():
            """ Run plastex and use the result to generate a document structure cache"""
            plastex_output = self.course.load_latex_content(self)
            last_item = {-2: self}
            for fn, chapter in plastex_output.items():
                chapter['html'] = burnInExtras(self, chapter['html'], out_format='html')
                if chapter['html'].isspace():
                    chapter['html'] = ''
                if chapter['level'] < -1:
                    self.data['html'] = chapter['html']
                    last_item[-2] = self
                elif chapter['level'] < self.splitlevel:
                    i = -2
                    while i < chapter['level']:
                        if i in last_item:
                            parent = last_item[i]
                        i = i + 1
                    item = Part(self.course, chapter, parent)
                    copy_attrs(item)
                    setup_pdf_url(item, chapter)
                    last_item[chapter['level']] = item
                    parent.content.append(item)
                elif chapter['level'] == self.splitlevel:
                    i = -2
                    while i < chapter['level']:
                        if i in last_item:
                            parent = last_item[i]
                        i = i + 1
                    item = Html(self.course, chapter, self)
                    copy_attrs(item)
                    setup_pdf_url(item, chapter)
                    parent.content.append(item)
            self.has_pdf = False
            self.generated = True
            logger.debug('Writing out document structure cache file: {}'.format(self.out_struct_file))
            with open(self.out_struct_file, 'w') as f:
                yaml.dump(self.content_tree(), f)

        def load_cached_structure():
            """
            Load the cached document structure if one exists and is current

            Returns true if the document structure is loaded or has already been generated
            """
            if self.generated:
                return True
            if self.recently_built():
                self.content = [load_item(self.course, obj, self) for obj in self.cached_struct.get('content', [])]
                for item in self.content:
                    copy_attrs(item)
                self.has_pdf = False
                self.generated = True
                return True
            self.last_built = None
            return False

        if ext == '.tex':
            if not load_cached_structure():
                run_plastex_for_structure()
        else:
            raise Exception("Error: Unrecognised source type used for LaTeX Document item {}: {}"
                            .format(self.title, self.source))

    @property
    def plastex_filename_rules(self):
        fnstr = self.out_path / '[$id, $title(4), $num(4)]'
        return '{} {}'.format(self.out_file, fnstr)

    def get_context(self):
        context = super().get_context()
        context.update({
            'part-slug': self.slug,
            'chapters': [item.get_context() for item in self.content if not item.is_hidden],
            'pdf': '{}.pdf'.format(self.url)
        })
        return context

    def content_tree(self):
        attr_dict = super().content_tree()
        attr_dict['content'] = [item.content_tree() for item in self.content]
        attr_dict['splitlevel'] = self.splitlevel
        return attr_dict


class Url(Item):
    type = 'url'
    title = 'Untitled URL'

    def __init__(self, course, data, parent=None):
        super().__init__(course, data, parent)
        self.source = self.data.get('source', '')
        self.data['html'] = ''

    @property
    def url(self):
        return str(self.source)

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
        self.has_pdf = self.data.get('build_pdf', self.course.config['build_pdf'])

    def get_context(self):
        context = super().get_context()
        context.update({
            'build_pdf': self.has_pdf,
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


class Introduction(Part):
    type = 'introduction'
    template_name = 'index.html'
    title = 'index'
    is_index = True

    def __str__(self):
        return 'introduction'

    out_path = Path('')
    out_file = Path('index.html')
    url = ''

    def get_context(self):
        context = super().get_context()
        context['links'] = [s.get_context() for s in self.course.structure
                            if s.type != 'introduction' and not s.is_hidden]

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
    is_index = True


class Notebook(Chapter):
    type = 'notebook'
    has_nb = True

    def get_context(self):
        context = super().get_context()
        context.update({
            'notebook': self.nb_url,
            'pdf': self.pdf_url,
        })
        return context

    @property
    def out_nb(self):
        return self.named_out_file.with_suffix('.ipynb')

    @property
    def nb_url(self):
        return str(self.out_nb)


item_types = {
    'introduction': Introduction,
    'part': Part,
    'document': Document,
    'chapter': Chapter,
    'standalone': Standalone,
    'url': Url,
    'html': Html,
    'slides': Slides,
    'exam': Exam,
    'notebook': Notebook,
}
