from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import argparse
import io
import logging
from pathlib import Path

import nbformat as nbformat
from nbconvert.utils.io import unicode_std_stream

from .notedown import (MarkdownReader,
                       MarkdownWriter,
                       Knitr,
                       run,
                       strip)


templates_path = Path(__file__).parent / 'templates'
markdown_template = str((templates_path / 'markdown.tpl').resolve())

def convert(content, informat, outformat, strip_outputs=False):
    if os.path.exists(content):
        with io.open(content, 'r', encoding='utf-8') as f:
            contents = f.read()
    else:
        contents = content

    readers = {'notebook': nbformat,
               'markdown': MarkdownReader(precode='',
                                          magic=False,
                                          match='fenced')
               }

    writers = {'notebook': nbformat,
               'markdown': MarkdownWriter(markdown_template,
                                          strip_outputs=strip_outputs)
               }

    reader = readers[informat]
    writer = writers[outformat]

    print(content)
    notebook = reader.reads(contents, as_version=4)
    return writer.writes(notebook)
