#!/usr/bin/env python

import os
import subprocess
import binascii
from plasTeX.Imagers import VectorImager, Image
from pathlib import Path


class PDFSVG(VectorImager):
    """ Imager that uses pdf2svg """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdf2svg', 'pdfcrop --help']
    compiler = 'pdflatex'
    imagesFilename = 'tmp-images-uc.pdf'
    croppedImagesFilename = 'tmp-images.pdf'

    def getImage(self, node):
        name = getattr(node, 'imageoverride', None)

        if name in self.staticimages:
            return self.staticimages[name]

        if name is not None and Path(name).suffix.lower() == '.pdf':
            return self.single_pdf_to_svg(name)

        return super().getImage(node)

    def single_pdf_to_svg(self, name):
        """
            Convert a single PDF file to an SVG file.

            Returns:
                plasTeX.Imagers.Image
        """
        path = self.newFilename()
        Path(path).parent.mkdir(exist_ok=True,parents=True)
        cmd = ['pdf2svg', name, path]
        r = subprocess.run(cmd)
        img = Image(path, self.ownerDocument.config['images'])
        self.staticimages[name] = img
        return img

    def executeConverter(self, output):
        while Path(self.imagesFilename).exists():
            self.imagesFilename = binascii.b2a_hex(os.urandom(5)).decode("utf-8") + '-' + self.imagesFilename
        while Path(self.croppedImagesFilename).exists():
            self.croppedImagesFilename = (binascii.b2a_hex(os.urandom(5)).decode("utf-8")
                                          + '-' + self.croppedImagesFilename)

        open(self.imagesFilename, 'wb').write(output.read())
        subprocess.call(["pdfcrop", self.imagesFilename, self.croppedImagesFilename], stdout=subprocess.PIPE)

        rc = 0
        page = 1
        while 1:
            filename = 'img%d.svg' % page
            rc = subprocess.call(['pdf2svg', self.croppedImagesFilename, filename, str(page)], stdout=subprocess.PIPE)
            if rc:
                break

            if not open(filename).read().strip():
                os.remove(filename)
                break
            page += 1
            if page > len(self.images):
                break
        return rc, None

    def writePreamble(self, document):
        ret = super().writePreamble(document)
        self.source.write(r'''
\ifcsname setbeamerfont\endcsname
\setbeamertemplate{background canvas}[default]
\setbeamercolor{background canvas}{bg=}
\beamertemplatenavigationsymbolsempty
\fi
''')
        return ret


Imager = PDFSVG
