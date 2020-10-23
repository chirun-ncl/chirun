#!/usr/bin/env python

import os
import subprocess
from plasTeX.Imagers import VectorImager
from pathlib import Path

class PDFSVG(VectorImager):
    """ Imager that uses pdf2svg """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdf2svg', 'pdfcrop --help']
    compiler = 'pdflatex'

    def executeConverter(self, output):
        if Path('mc-tmp-images-uc.pdf').exists():
                raise Exception('Temporary pdf2svg imager file "mc-tmp-images-uc.pdf" already exists!')
        if Path('mc-tmp-images.pdf').exists():
                raise Exception('Temporary pdf2svg imager file "mc-tmp-images.pdf" already exists!')

        open('mc-tmp-images-uc.pdf', 'wb').write(output.read())
        subprocess.call(["pdfcrop", "mc-tmp-images-uc.pdf", "mc-tmp-images.pdf"], stdout=subprocess.PIPE)

        rc = 0
        page = 1
        while 1:
            filename = 'img%d.svg' % page
            rc = subprocess.call(['pdf2svg', 'mc-tmp-images.pdf', filename, str(page)], stdout=subprocess.PIPE)
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
