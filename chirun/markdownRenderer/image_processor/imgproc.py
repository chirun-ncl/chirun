from markdown.treeprocessors import Treeprocessor
from markdown import Extension
import filecmp
import logging
import subprocess
import shlex
from shutil import copyfile
from pathlib import Path
from chirun import mkdir_p

logger = logging.getLogger(__name__)


class ImageTreeprocessor(Treeprocessor):
    def __init__(self, md, item_sourcedir, item_outdir):
        Treeprocessor.__init__(self, md)
        self._item_sourcedir = Path(item_sourcedir)
        self._item_outdir = Path(item_outdir)
        self.image_id = 0

    def pdf2png(self, src, dst):
        subprocess.run(shlex.split('pdftoppm -png -r 150 -singlefile {} {}'.format(src, dst)))

    def run(self, root):
        moved_images = set()
        images = root.iter("img")
        for count, image in enumerate(images):
            if image in moved_images:
                continue
            src = image.attrib["src"]
            if src[0] != '/' and not src.startswith(('http://', 'https://', 'ftp://')):
                imageFile = self._item_sourcedir / src
                if imageFile.exists():
                    # Copy relative imagefile to build directory
                    out_src = Path('images') / Path(src).name
                    out_file = self._item_outdir / out_src
                    while out_file.exists() and not filecmp.cmp(out_file, imageFile):
                        new = Path('images') / (str(self.image_id).zfill(4) + '-' + Path(src).name)
                        logger.debug("Output filename {} already used and the image is different. Trying {}..."
                                     .format(out_src, new))
                        out_src = new
                        out_file = self._item_outdir / out_src
                        self.image_id = self.image_id + 1
                    mkdir_p(out_file.parent)
                    if imageFile.suffix == '.pdf':
                        self.pdf2png(str(imageFile), str(out_file.with_suffix('')))
                        out_src = out_src.with_suffix('.png')
                    else:
                        copyfile(str(imageFile), str(out_file))
                    image.attrib["src"] = str(out_src)
            moved_images.add(image)


class ImageProcessorExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'item_sourcedir': ['.', "Source directory of the chirun content item"],
            'item_outdir': ['.', "Output build location for the chirun content item"],
        }
        super(ImageProcessorExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)

        images = ImageTreeprocessor(md, self.getConfig('item_sourcedir'), self.getConfig('item_outdir'))
        md.treeprocessors.register(images, "imageprocessor", 5)
