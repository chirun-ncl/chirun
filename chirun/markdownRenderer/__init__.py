from chirun.markdownRenderer.arithmatex import ArithmatexExtension
import chirun.markdownRenderer.codemirror
from chirun.html_filter import HTMLFilter
import filecmp
from markdown import markdown
from pathlib import Path, PurePath
import re
from shutil import copyfile
import subprocess
from urllib.parse import urlparse, urlunparse

from .link_processor.linkproc import LinkProcessorExtension
from .markdown_figure.mdfigure import FigureExtension


def rewrite_media_sources(soup, item):
    """
        Rewrite the source attributes of media elements such as ``img`` and ``video``.
    """
    tags = {
        'img': ['src'],
        'video': ['src'],
        'audio': ['src'],
        'source': ['src'],
    }

    for tag, attrs in tags.items():
        for el in soup.find_all(tag):
            for attr in attrs:
                # Get the URL from the element's attribute
                url = el.get(attr)

                parsed_url = urlparse(url)
                # Ignore URLs with a scheme, which must not be included in the package.
                if parsed_url.scheme != '':
                    continue

                source_file = item.source.parent / url

                # Ignore the URLs pointing to files which don't exist in the source
                if not source_file.exists():
                    continue

                # Find a filename for the file in the build directory, under the ``images`` directory.
                # Files with the same name will have a number added to differentiate them.
                # Multiple references to the same file will only cause the file to be copied to the output once.
                scheme, netloc, path, parameters, query, fragment = parsed_url
                path = Path(parsed_url.path)
                out_name = PurePath('images') / path.name
                if out_name.suffix == '.pdf':
                    out_name = out_name.with_suffix('.svg')
                out_path = item.course.get_build_dir() / item.out_path
                out_file = (out_path / out_name)
                i = 0
                while out_file.exists():
                    if filecmp.cmp(out_file, source_file):
                        break

                    out_name = out_name.with_stem(f'{path.stem}-{i:04d}')
                    out_file = (out_path / out_name)
                    i += 1

                out_src = urlunparse((scheme, netloc, str(out_name), parameters, query, fragment))

                if not out_file.exists():
                    out_file.parent.mkdir(exist_ok=True, parents=True)

                    if source_file.suffix == '.pdf':
                        subprocess.run(['pdf2svg', source_file.name, str(out_file)],errors="backslashreplace")
                    else:
                        copyfile(source_file, out_file)

                el[attr] = out_src


class MarkdownImageFilter(HTMLFilter):
    filters = [rewrite_media_sources]

class MarkdownRenderer(object):
    def __init__(self):
        self.extension_configs = {
            "pymdownx.striphtml": {
                'strip_comments': True,
                'strip_js_on_attributes': False,
                'strip_attributes': []
            },
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        'name': 'runnable',
                        'class': 'runnable',
                        'format': chirun.markdownRenderer.codemirror.runnable_formatter,
                        'validator': chirun.markdownRenderer.codemirror.runnable_validator
                    }, 
                    {
                        'name': 'output',
                        'class': 'output',
                        'format': chirun.markdownRenderer.codemirror.output_formatter,
                        'validator': chirun.markdownRenderer.codemirror.output_validator
                    }
                ]
            }
        }

    def render(self, content_item, outdir, md_string=None):
        struct = content_item.course.structure
        mdx_extensions = [
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

        output, _ = MarkdownImageFilter().apply(content_item, output)

        return output
