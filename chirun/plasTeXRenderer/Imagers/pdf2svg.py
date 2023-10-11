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
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        cmd = ['pdf2svg', name, path]
        subprocess.run(cmd)
        img = Image(path, self.ownerDocument.config['images'])
        self.staticimages[name] = img
        return img

    def executeConverter(self, outfile=None):
        if outfile is None:
            outfile = self.tmpFile.with_suffix('.pdf').name

        subprocess.call(["pdfcrop", outfile, self.tmpFile.with_suffix('.cropped.pdf').name], stdout=subprocess.DEVNULL)

        images = []
        for no, line in enumerate(open("images.csv")):
            filename = 'img%d.svg' % no
            page, output, scale_str = line.split(",")
            scale = float(scale_str.strip())
            images.append((filename, output.rstrip()))

            subprocess.run(['pdf2svg', self.tmpFile.with_suffix('.cropped.pdf').name, filename, str(page)], stdout=subprocess.DEVNULL, check=True)

            if scale != 1:
                tree = ET.parse(filename)
                root = tree.getroot()

                for attrib in ["width", "height"]:
                    m = length_re.match(root.attrib[attrib])
                    if m is None:
                        raise ValueError
                    root.attrib[attrib] = "{:.2f}{}".format(float(m.group(1)) * scale, m.group(2))

                tree.write(filename)

        return images

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
