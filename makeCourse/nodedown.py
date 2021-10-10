from notedown import MarkdownReader
from . import mkdir_p

logger = logging.getLogger(__name__)


class NotebookRenderer(object):
    def __init__(self, course):
        self.course = course

    def render_item(self, item):
        if item.recently_built():
            return
        outPath = self.course.get_build_dir() / item.out_file
        outDir = outPath.parent
        mkdir_p(outDir)
        if not (item.source.name == ''):
            logger.info("Building Notebook: {item}".format(item=item.source))
        nb = MarkdownReader().to_notebook(item.markdown_content())
        with open(str(outPath), 'w', encoding='utf-8') as f:
            f.write(nb)
