from markdown import markdown
import makeCourse.markdownRenderer.codemirror
from mdfigure import FigureExtension


class MarkdownRenderer(object):
    def __init__(self):
        self.extensions = [FigureExtension(),'mdx_outline',
                'pymdownx.highlight','pymdownx.arithmatex',
                'pymdownx.extra','pymdownx.superfences']
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

    def render(self, content):
        return markdown(content, extensions=self.extensions, extension_configs=self.extension_configs)

class SlidesMarkdownRenderer(MarkdownRenderer):
     def __init__(self):
        super().__init__()

        self.extensions = [FigureExtension(),'pymdownx.highlight','pymdownx.arithmatex','pymdownx.extra','pymdownx.superfences']

