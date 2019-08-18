import logging
import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from . import mkdir_p

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

    def url_filter(self, url):
        return self.course.get_web_root() + url

    def render_item(self, item, template_attr = 'template_name', out_attr = 'out_file'):
        template_file = getattr(item,template_attr)
        logger.debug("Rendering {item} using {template}".format(item=item, template=template_file))

        outPath = self.course.get_build_dir() / getattr(item,out_attr)
        outDir = outPath.parent
        mkdir_p(outDir)

        if self.course.args.lazy and item.recently_built():
            return

        template = self.env.get_template(template_file)
        context = {
            'course': self.course,
            'item': item,
            'ROOT_URL': self.course.get_web_root(),
            'date': datetime.date.today(),
        }
        html = template.render(context)

        with open(str(outPath),'w') as f:
            f.write(html)
