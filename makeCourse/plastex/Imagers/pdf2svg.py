#!/usr/bin/env python

import os
import subprocess
import os
import binascii
from plasTeX.Imagers import VectorImager
from pathlib import Path

class PDFSVG(VectorImager):
    """ Imager that uses pdf2svg """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdf2svg', 'pdfcrop --help']
    compiler = 'pdflatex'
    imagesFilename = 'tmp-images-uc.pdf'
    croppedImagesFilename = 'tmp-images.pdf' 

    def executeConverter(self, output):
        while Path(self.imagesFilename).exists():
            self.imagesFilename = binascii.b2a_hex(os.urandom(5)).decode("utf-8")+'-'+self.imagesFilename
        while Path(self.croppedImagesFilename).exists():
            self.croppedImagesFilename = binascii.b2a_hex(os.urandom(5)).decode("utf-8")+'-'+self.croppedImagesFilename

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

Imager = PDFSVG
