import asyncio
from   babel.support import Translations
import chirun.filter
from   chirun.markdownRenderer import MarkdownRenderer
import contextlib
import datetime
from   http.server import HTTPServer, SimpleHTTPRequestHandler
from   jinja2 import Environment, FileSystemLoader, select_autoescape, contextfilter, TemplateNotFound
import logging
import nbformat
from   notedown import MarkdownReader
import pyppeteer
import re
import socket
import threading
from   urllib.parse import urlparse
from . import mkdir_p

logger = logging.getLogger(__name__)

def find_free_port():
    """
        Find and return the number of an open port.
    """
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def http_server(directory=None, port=8000, end_signal=None):

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    server_address = ('' ,port)
    httpd = HTTPServer(server_address, Handler)
    while not end_signal.is_set():
        httpd.handle_request()

@contextlib.asynccontextmanager
async def get_browser(directory):
    """
        Context manager which opens a headless browser session through pyppeteer, and starts a local HTTP server. 
        Both are destroyed when the context is destroyed.

        Yields a pair (browser, http_port)
    """
    browser = None
    attempts = 0

    try:
        end_signal = threading.Event()
        http_port = find_free_port()
        http_thread = threading.Thread(
            target=http_server,
            kwargs = {
                'directory': directory,
                'port': http_port,
                'end_signal': end_signal
            },
            daemon = True
        )
        http_thread.start()
        while browser is None and attempts < 20:
            try:
                browser = await pyppeteer.launch({
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--single-process',
                        '--disable-web-security',
                    ],
                })
            except Exception:
                logger.info('Warning: Browser failed to start. Trying again...({})'.format(str(attempts)))
                attempts = attempts + 1

        if not browser:
            raise Exception('Error: Headless chrome failed to start!')

        yield (browser, http_port)
    finally:
        await browser.close()
        end_signal.set()

class BaseRenderer(object):
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

        timestamp = datetime.datetime.now().timestamp()

        @contextfilter
        def static_url(context, url):
            return url_filter(context, 'static/' + url) + f'?build_time={timestamp}'

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
            'CHIRUN_VERSION': self.course.VERSION,
            'ACCESSIBILITY_STATEMENT_URL': 'https://chirun.org.uk/accessibility-statement/material',
            'out_file': out_file,
        }
        return self.render_template(template_file, context)

    def pdf_outPath(self, item):
        return self.course.get_build_dir() / item.named_out_file.with_suffix('.pdf')

    def pdf_kwargs(self, item):
        return {
            'path': self.pdf_outPath(item),
            'format': 'A4', 
            'printBackground': True
        }

    def pdf_absHTMLPath(self, item):
        return item.out_file

    async def to_pdf(self, item):
        if item.recently_built():
            return

        self.render_item(item)

        logger.info("Printing {} to PDF".format(item))

        root_dir = self.course.get_build_dir().resolve()
        absHTMLPath = self.pdf_absHTMLPath(item)
        pdf_kwargs = self.pdf_kwargs(item)

        logger.debug('    {src} => {dest}'.format(src = item.title, dest = pdf_kwargs['path']))

        async with get_browser(root_dir) as (browser, port):
            page = await browser.newPage()
            page_url = f'http://localhost:{port}/{absHTMLPath}'
            await page.goto(page_url)
            await self.wait_for_pdf_ready(page)
            await page.pdf(pdf_kwargs)

    async def wait_for_pdf_ready(self, page):
        await page.waitForFunction('window.mathjax_is_loaded == 1', options={'timeout': 100000})
        await page.evaluate(r'''(function() { MathJax.typesetPromise().then(() => window.mathjax_has_run = true)})''')
        await page.waitForFunction('window.mathjax_has_run && document.fonts.ready', options={'timeout': 10000})

class Renderer(BaseRenderer):
    def pdf_kwargs(self, item):
        kwargs = super().pdf_kwargs(item)

        headerHTML = self.to_html(item, item.template_pdfheader)
        footerHTML = self.to_html(item, item.template_pdffooter)
        kwargs.update({
            'displayHeaderFooter': True,
            'headerTemplate': headerHTML,
            'footerTemplate': footerHTML,
        })

        return kwargs

class SlidesRenderer(BaseRenderer):
    def __init__(self, course):
        super().__init__(course)

    def render_item(self, item):
        # First build the item in document format.
        super().render_item(item)

        # Then build it as slides.
        outPath = self.course.get_build_dir() / item.out_slides
        template_file = item.template_slides

        logger.debug("Rendering {item} using {template}{rel}".format(item=item, template=template_file,
                     rel=' using relative paths' if self.course.force_relative_build or not self.course.args.absolute
                     else ''))

        html = self.to_html(item, template_file, item.out_slides)

        with open(str(outPath), 'w', encoding='utf-8') as f:
            f.write(html)

    def pdf_kwargs(self, item):
        kwargs = super().pdf_kwargs(item)
        kwargs['landscape'] = True
        return kwargs

    def pdf_absHTMLPath(self, item):
        return item.out_slides

    def pdf_outPath(self, item):
        return self.course.get_build_dir() / item.named_out_file.with_suffix('.pdf')

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
