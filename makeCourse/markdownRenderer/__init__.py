from markdown import markdown
import makeCourse.markdownRenderer.codemirror
from .markdown_figure.mdfigure import FigureExtension
from .image_processor.imgproc import ImageProcessorExtension


class MarkdownRenderer(object):
    def __init__(self):
        self.extension_configs={
                "pymdownx.arithmatex": {
                    "preview": False
                    },
                "pymdownx.superfences": {
                    "custom_fences": [{
                        'name': 'runnable',
                        'class': 'runnable',
                        'format': makeCourse.markdownRenderer.codemirror.runnable_formatter,
                        'validator': makeCourse.markdownRenderer.codemirror.runnable_validator
                    },{
                        'name': 'editable',
                        'class': 'editable',
                        'format': makeCourse.markdownRenderer.codemirror.editable_formatter,
                        'validator': makeCourse.markdownRenderer.codemirror.editable_validator
                    },{
                        'name': 'output',
                        'class': 'output',
                        'format': makeCourse.markdownRenderer.codemirror.output_formatter,
                        'validator': makeCourse.markdownRenderer.codemirror.output_validator
                    }]
                }
            }

    def render(self, content_item, outdir):
        mdx_extensions = [
                ImageProcessorExtension(item_sourcedir=str(content_item.source.parent), item_outdir=str(outdir)),
                FigureExtension(),
                'mdx_outline',
                'pymdownx.highlight',
                'pymdownx.arithmatex',
                'pymdownx.extra',
                'pymdownx.superfences'
                ]
        return markdown(content_item.markdown_content(), extensions=mdx_extensions, extension_configs=self.extension_configs)
