import markdown
from markdown.treeprocessors import Treeprocessor
from markdown import Extension
from markdown.util import etree
import subprocess
import shlex
from copy import copy
from shutil import copyfile
from pathlib import Path, PurePath
from makeCourse import mkdir_p


class ImageTreeprocessor(Treeprocessor):
    def __init__(self, md, item_sourcedir, item_outdir):
        Treeprocessor.__init__(self, md)
        self._item_sourcedir = Path(item_sourcedir)
        self._item_outdir = Path(item_outdir)
        self.imageID = 0

    def pdf2png(self, src, dst):
        subprocess.run(shlex.split('pdftoppm -png -r 150 -singlefile {} {}'.format(src,dst)))

    def run(self, root):
        moved_images = set()
        images = root.iter("img")
        for count, image in enumerate(images):
            if image in moved_images:
                continue
            src = image.attrib["src"]
            if src[0] != '/' and not src.startswith(('http://','https://','ftp://')):
                imageFile = self._item_sourcedir / src
                if imageFile.exists():
                    # Copy relative imagefile to build directory
                    outSrc = Path('images') / (str(self.imageID).zfill(4) + '-' + Path(src).name)
                    outFile = self._item_outdir / outSrc
                    mkdir_p(outFile.parent)
                    if imageFile.suffix == '.pdf':
                        self.pdf2png(str(imageFile),str(outFile.with_suffix('')))
                        outSrc = outSrc.with_suffix('.png')
                    else:
                        copyfile(str(imageFile),str(outFile))
                    image.attrib["src"] = str(outSrc)
                    self.imageID = self.imageID + 1
            moved_images.add(image)

class ImageProcessorExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'item_sourcedir': ['.', "Source directory of the coursebuilder content item"],
            'item_outdir': ['.', "Output build location for the coursebuilder content item"],
        }
        super(ImageProcessorExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        images = ImageTreeprocessor(md, self.getConfig('item_sourcedir'), self.getConfig('item_outdir'))
        md.treeprocessors.add("imageprocessor", images, "_end")
        md.registerExtension(self)
