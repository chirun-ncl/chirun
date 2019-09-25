"""
Extension for markbox to make all images lightbox

copyright @2015 Alicia Schep <aschep@gmail.com>

"""
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown import Extension
from markdown.util import etree
from copy import copy


class FigureTreeprocessor(Treeprocessor):
    """ Figure Treeprocessor """
    def __init__(self, md, figure_classes=None, img_classes=None ):
        Treeprocessor.__init__(self, md)
        self._figure_classes = figure_classes
        self._img_classes = img_classes

    def run(self, root):
        parent_map = {c: p for p in root.iter() for c in p}
        images = root.getiterator("img")
        for count, image in enumerate(images):
            alttext = image.attrib["alt"]
            image.set("alt", alttext)
            parent = parent_map[image]
            idx = list(parent).index(image)

            figure = etree.Element('figure')

            if self._figure_classes is not None:
                figure.set("class", self._figure_classes)
            else:
                figure.set("class", "figure" + str(count + 1))

            if self._img_classes is not None:
                image.set("class", self._img_classes)

            figure.set("data-title", alttext)
            figure.tail = copy(image.tail)
            parent.insert(idx, figure)
            parent.remove(image)
            image.tail = markdown.util.AtomicString("")
            figure.append(image)

class FigureExtension(Extension):
    """
    LightboxImagesExtension
    Extension class for markdown
    """
    def __init__(self, **kwargs):
        self.config = {
            'figure_classes': [None, "Class attributes assigned to the <figure /> tag"],
            'img_classes': [None, "Class attributes assigned to the <img /> tag"],
        }
        super(FigureExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        figures = FigureTreeprocessor(md,
                                      self.getConfig('figure_classes'),
                                      self.getConfig('img_classes'))
        md.treeprocessors.add("figure", figures, "_end")
        md.registerExtension(self)
