import logging
import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from . import mkdir_p
import asyncio
from pyppeteer import launch

logger = logging.getLogger(__name__)

class Renderer(object):
    def __init__(self, course):
        self.course = course
        self.env = Environment(
            loader=FileSystemLoader(str(self.course.theme.template_path)),
            autoescape=select_autoescape(['html'])
        )
        self.env.filters['url'] = self.url_filter
        def static_url(url):
            return self.url_filter('static/'+url)
        self.env.filters['static_url'] = static_url

    def url_filter(self, url, theme=False):
        return self.course.get_web_root(force_theme=theme) + url

    def render_item(self, item):
        if self.course.args.lazy and item.recently_built():
            return
        outPath = self.course.get_build_dir() / item.out_file
        outDir = outPath.parent
        mkdir_p(outDir)
        template_file = item.template_name
        logger.debug("Rendering {item} using {template}{local}.".format(item=item, template=template_file, local=' with local paths' if self.course.force_local or self.course.args.local else ''))
        html = self.to_html(item, template_file)
        with open(str(outPath),'w') as f:
            f.write(html)

    def to_html(self, item, template_file):
        template = self.env.get_template(template_file)
        context = {
            'course': self.course,
            'item': item,
            'date': datetime.date.today(),
        }
        return template.render(context)

    async def to_pdf(self, item):
        if self.course.args.lazy and item.recently_built():
            return
        self.render_item(item)
        headerHTML= self.to_html(item, item.template_pdfheader)
        footerHTML= self.to_html(item, item.template_pdffooter)

        logger.info("Printing {} to PDF".format(item))
        absHTMLPath = self.course.get_root_dir().resolve() / self.course.get_build_dir() / item.out_file
        outPath = self.course.get_build_dir() / item.named_out_file.with_suffix('.pdf')
        logger.debug('    {src} => {dest}'.format(src=item.title, dest=outPath))
        browser = await launch({'headless': True})
        page = await browser.newPage()
        await page.goto('file://{}'.format(absHTMLPath))
        await page.waitForFunction('window.mathjax_is_loaded == 1', options = {'timeout':10000});
        await page.pdf({'path': outPath, 'format': 'A4', 'displayHeaderFooter': True, \
                'headerTemplate': headerHTML, 'footerTemplate': footerHTML, \
                'printBackground': True})
        await browser.close()

class SlidesRenderer(Renderer):
    def __init__(self, course):
        super().__init__(course)

    def render_item(self, item):
        super().render_item(item)
        outPath = self.course.get_build_dir() / item.out_slides
        template_file = item.template_slides
        html = self.to_html(item, template_file)
        with open(str(outPath),'w') as f:
            f.write(html)

    async def to_pdf(self, item):
        if self.course.args.lazy and item.recently_built():
            return
        self.render_item(item)
        logger.info("Printing {} as PDF".format(item))
        absHTMLPath = self.course.get_root_dir().resolve() / self.course.get_build_dir() / item.named_out_file.with_suffix('.slides.html')
        outPath = self.course.get_build_dir() / item.named_out_file.with_suffix('.pdf')
        logger.debug('    {src} => {dest}'.format(src=item.title, dest=outPath))
        browser = await launch({'headless': True})
        page = await browser.newPage()
        await page.goto('file://{}?print-pdf'.format(absHTMLPath))
        await page.setViewport({'width': 1366, 'height': 768})
        await page.waitForFunction('Reveal.isReady() && window.mathjax_is_loaded == 1', options = {'timeout':10000});
        await page.pdf({'path': outPath, 'width': 1366, 'height': 768})
        await browser.close()
