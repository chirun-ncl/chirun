r"""
Here we tweak the arithmatex extension to handle inline math with $$Equation$$ so that it does not need to be in
it's own block.

Arithmetic: https://github.com/facelessuser/pymdown-extensions/pymdownx/arithmatex.py
MIT license.
Copyright (c) 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from pymdownx import arithmatex
import xml.etree.ElementTree as etree
from markdown import util as md_util

arithmatex.RE_SMART_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?<!\$)(?=\$)|(?<!\\)(?<!\$)(\$)(?!\s)((?:\\.|[^\\$])+?)(?<!\s)(?<!\$)(?:\$))'  # noqa: E501
arithmatex.RE_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?<!\$)(?=\$)|(?<!\\)(?<!\$)(\$)((?:\\.|[^\\$])+?)(?<!\$)(?:\$))'
arithmatex.RE_DOUBLE_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?=\$\$)|(?<!\\)(\$\$)((?:\\.|[^\\$])+?)(?:\$\$))'
arithmatex.RE_BRACKET_INLINE_BLOCK = r'(?:(?<!\\)((?:\\{2})+?)(?=\\\[)|(?<!\\)(\\\[)((?:\\[^\]]|[^\\])+?)(?:\\\]))'
arithmatex.RE_TEX_INLINE_BLOCK = r'(\\begin\{(?P<env>[a-z]+\*?)\}(?:\\.|[^\\])+?\\end\{(?P=env)\})'


def _block_mathjax_format(math, preview=False):
    """Block math formatter."""
    if preview:
        el = etree.Element('span')
        pre = etree.SubElement(el, 'span', {'class': 'MathJax_Preview'})
        pre.text = md_util.AtomicString(math)
        script = etree.SubElement(el, 'script', {'type': 'math/tex; mode=display'})
        script.text = md_util.AtomicString(math)
    else:
        el = etree.Element('script', {'type': 'math/tex; mode=display'})
        el.text = md_util.AtomicString(math)
    return el


class InlineBlockArithmatexPattern(arithmatex.InlineArithmatexPattern):
    def handleMatch(self, m, data):
        """Handle notations and switch them to something that will be more detectable in HTML."""

        # Handle escapes
        escapes = m.group(1)
        if not escapes:
            escapes = m.group(4)
        if escapes:
            return escapes.replace('\\\\', self.ESCAPED_BSLASH), m.start(0), m.end(0)

        # Handle Tex
        math = m.group(3)
        if not math:
            math = m.group(6)
        if not math:
            math = m.group(7)

        if self.generic:
            return arithmatex.fence_generic_format(math, wrap=self.wrap), m.start(0), m.end(0)
        else:
            return _block_mathjax_format(math, self.preview), m.start(0), m.end(0)


class ArithmatexExtension(arithmatex.ArithmatexExtension):
    def extendMarkdown(self, md):
        super().extendMarkdown(md)
        config = self.getConfigs()

        allowed_block = set(config.get('block_syntax', ['dollar', 'square', 'begin']))
        inline_block_patterns = []
        if 'dollar' in allowed_block:
            inline_block_patterns.append(arithmatex.RE_DOUBLE_DOLLAR_INLINE)
        if 'square' in allowed_block:
            inline_block_patterns.append(arithmatex.RE_BRACKET_INLINE_BLOCK)
        if 'begin' in allowed_block:
            inline_block_patterns.append(arithmatex.RE_TEX_INLINE_BLOCK)
        if inline_block_patterns:
            inline_block = InlineBlockArithmatexPattern('(?:%s)' % '|'.join(inline_block_patterns), config)
            md.inlinePatterns.register(inline_block, 'arithmatex-inline-block', 189.9)
