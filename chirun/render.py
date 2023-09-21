import asyncio
from   babel.support import Translations
import chirun.filter
from   chirun.markdownRenderer import MarkdownRenderer
import datetime
from   jinja2 import Environment, FileSystemLoader, select_autoescape, contextfilter, TemplateNotFound
import logging
import nbformat
from   notedown import MarkdownReader
from   pyppeteer import launch
import re
from   urllib.parse import urlparse
from . import mkdir_p

logger = logging.getLogger(__name__)


async def get_browser():
    browser = None
    attempts = 0

    while browser is None and attempts < 20:
        try:
            browser = await launch({
                'headless': True,
                'args': ['--no-sandbox', '--disable-setuid-sandbox', '--single-process']
            })
        except Exception:
            logger.info('Warning: Browser failed to start. Trying again...({})'.format(str(attempts)))
            attempts = attempts + 1

    if not browser:
        raise Exception('Error: Headless chrome failed to start!')

    return browser


class Renderer(object):
    def __init__(self, course):
        self.course = course
        self.env = Environment(
            loader = FileSystemLoader(str(self.course.theme.template_path)),
            autoescape = select_autoescape(['html']),
            extensions = ['jinja2.ext.i18n',]
        )
        try:
            with open(self.course.theme.translations_path, 'rb') as translations_file:
                self.env.install_gettext_translations(Translations(translations_file), newstyle=True)
        except FileNotFoundError:
            self.env.install_null_translations(newstyle=True)

        @contextfilter
        def url_filter(context, url, theme=False):
            self.course.force_theme = theme
            item = context.get('item')
            if item is not None and not re.search(r'^[^:]+:\/\/', url):
                url = self.course.make_relative_url(context['item'], url)
            self.course.force_theme = False
            return url
        self.env.filters['url'] = url_filter

        @contextfilter
        def static_url(context, url):
            return url_filter(context, 'static/' + url)

        self.env.filters['static_url'] = static_url

    def render_template(self, template_file, context):
        try:
            template = self.env.get_template(template_file)
        except TemplateNotFound as e:
            print(self.course.theme.template_path)
            raise e
        return template.render(context)

    def render_item(self, item):
        if item.recently_built():
            return

        outPath = self.course.get_build_dir() / item.out_file
        outDir = outPath.parent

        mkdir_p(outDir)

        template_file = item.template_name

        if not (item.source.name == ''):
            logger.info("Rendering: {item}".format(item=item.source))

        logger.debug("Rendering {item} using {template}{rel}".format(item=item, template=template_file,
                     rel=' using relative paths' if self.course.force_relative_build or not self.course.args.absolute
                     else ''))

        html = self.to_html(item, template_file, item.out_file)

        with open(str(outPath), 'w', encoding='utf-8') as f:
            f.write(html)

    def to_html(self, item, template_file, out_file=None):
        context = {
            'course': self.course,
            'item': item,
            'date': datetime.date.today(),
            'CHIRUN_HOME_URL': 'https://chirun.org.uk',
            'ACCESSIBILITY_STATEMENT_URL': 'https://chirun.org.uk/accessibility-statement/material',
            'out_file': out_file,
        }
        return self.render_template(template_file, context)

    async def to_pdf(self, item):
        if item.recently_built():
            return
        self.render_item(item)
        headerHTML = self.to_html(item, item.template_pdfheader)
        footerHTML = self.to_html(item, item.template_pdffooter)

        logger.info("Printing {} to PDF".format(item))
        absHTMLPath = self.course.get_root_dir().resolve() / self.course.get_build_dir() / item.out_file
        outPath = self.course.get_build_dir() / item.named_out_file.with_suffix('.pdf')
        logger.debug('    {src} => {dest}'.format(src=item.title, dest=outPath))
        browser = await get_browser()
        page = await browser.newPage()
        await page.goto('file://{}'.format(absHTMLPath))
        await page.waitForFunction('window.mathjax_is_loaded == 1', options={'timeout': 10000})
        await page.evaluate(r'''(function() { MathJax.typesetPromise().then(() => window.mathjax_has_run = true)})''')
        await page.waitForFunction('window.mathjax_has_run && document.fonts.ready', options={'timeout': 10000})
        await page.pdf({'path': outPath, 'format': 'A4', 'displayHeaderFooter': True,
                        'headerTemplate': headerHTML, 'footerTemplate': footerHTML,
                        'printBackground': True})
        await browser.close()


class SlidesRenderer(Renderer):
    def __init__(self, course):
        super().__init__(course)

    def render_item(self, item):
        super().render_item(item)

        outPath = self.course.get_build_dir() / item.out_slides
        template_file = item.template_slides

        logger.debug("Rendering {item} using {template}{rel}".format(item=item, template=template_file,
                     rel=' using relative paths' if self.course.force_relative_build or not self.course.args.absolute
                     else ''))

        html = self.to_html(item, template_file, item.out_slides)

        with open(str(outPath), 'w', encoding='utf-8') as f:
            f.write(html)

    async def to_pdf(self, item):
        if item.recently_built():
            return
        self.render_item(item)
        logger.info("Printing {} as PDF".format(item))
        absHTMLPath = (self.course.get_root_dir().resolve()
                       / self.course.get_build_dir()
                       / item.named_out_file.with_suffix('.slides.html'))
        outPath = self.course.get_build_dir() / item.named_out_file.with_suffix('.pdf')
        logger.debug('    {src} => {dest}'.format(src=item.title, dest=outPath))
        browser = await get_browser()
        page = await browser.newPage()
        await page.goto('file://{}?print-pdf'.format(absHTMLPath))
        await page.setViewport({'width': 1366, 'height': 768})
#        await page.waitForFunction('window.mathjax_is_loaded == 1', options={'timeout': 10000})
        await page.pdf({'path': outPath, 'width': 1366, 'height': 768})
        await browser.close()


class NotebookRenderer(object):
    def __init__(self, course):
        self.course = course
        self.markdownRenderer = MarkdownRenderer()

    def render_item(self, item):
        if item.recently_built():
            return
        outPath = self.course.get_build_dir() / item.out_nb
        outDir = outPath.parent
        mkdir_p(outDir)
        if not (item.source.name == ''):
            logger.info("Building Notebook: {item}".format(item=item.source))
        nb = MarkdownReader().to_notebook(item.markdown_content())
        chirun.filter.CellFilter().apply(item, nb)
        for cell in nb.cells:
            if cell['cell_type'] == 'markdown':
                html = self.markdownRenderer.render(item, outDir, cell['source'])
                cell['source'], _ = chirun.filter.CellHTMLFilter().apply(item, html, out_format='html')
        with open(str(outPath), 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
