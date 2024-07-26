"""
Replace `<p>` tags whose only children are images with `<figure>` tags.
"""

from markdown.treeprocessors import Treeprocessor
from markdown import Extension

def safe_text(txt):
    return txt if txt is not None else ''

class FigureTreeprocessor(Treeprocessor):
    def run(self, root):
        img_tags = ('img', 'svg', 'object')

        for p in root.iter('p'):
            text_content = safe_text(p.text) + ''.join(safe_text(c.tail) for c in p)

            if all(c.tag in img_tags for c in p) and text_content.strip()=='':
                p.tag = 'figure'
        return

class FigureExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        figures = FigureTreeprocessor(md)
        md.treeprocessors.add("figure", figures, "_end")
        md.registerExtension(self)
