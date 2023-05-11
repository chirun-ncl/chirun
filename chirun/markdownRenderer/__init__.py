from   chirun.markdownRenderer.arithmatex import ArithmatexExtension
import chirun.markdownRenderer.codemirror
from   markdown import markdown
import re
from   .image_processor.imgproc import ImageProcessorExtension
from   .link_processor.linkproc import LinkProcessorExtension
from   .markdown_figure.mdfigure import FigureExtension


class MarkdownRenderer(object):
    def __init__(self):
        self.extension_configs = {
            "pymdownx.striphtml": {
                'strip_comments': True,
                'strip_js_on_attributes': False,
                'strip_attributes': []
            },
            "pymdownx.superfences": {
                "custom_fences": [{
                    'name': 'runnable',
                    'class': 'runnable',
                    'format': chirun.markdownRenderer.codemirror.runnable_formatter,
                    'validator': chirun.markdownRenderer.codemirror.runnable_validator
                }, {
                    'name': 'editable',
                    'class': 'editable',
                    'format': chirun.markdownRenderer.codemirror.editable_formatter,
                    'validator': chirun.markdownRenderer.codemirror.editable_validator
                }, {
                    'name': 'output',
                    'class': 'output',
                    'format': chirun.markdownRenderer.codemirror.output_formatter,
                    'validator': chirun.markdownRenderer.codemirror.output_validator
                }]
            }
        }

    def render(self, content_item, outdir, md_string=None):
        struct = content_item.course.structure
        mdx_extensions = [
            ImageProcessorExtension(item_sourcedir=str(content_item.source.parent),
                                    item_outdir=str(outdir)),
            LinkProcessorExtension(item_sourcedir=str(content_item.source.parent),
                                   item_outdir=str(outdir),
                                   course_structure=struct),
            FigureExtension(),
            ArithmatexExtension(preview=False),
            'pymdownx.highlight',
            'pymdownx.extra',
            'pymdownx.superfences',
            'pymdownx.striphtml',
        ]

        if md_string is None:
            md_string = content_item.markdown_content()

        sections = re.split(r'$\n\n---+\n\n', md_string, flags=re.M)

        output = ''
        for section_md in sections:
            content = markdown(section_md, extensions=mdx_extensions,
                           extension_configs=self.extension_configs)
            output += f'<section>\n{content}\n</section>\n'

        return output
