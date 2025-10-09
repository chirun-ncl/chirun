import os
import re
import plasTeX
from plasTeX import Macro, Token, Command
from pathlib import Path
from plasTeX.Packages.graphicx import *  # noqa: F401, F403
import plasTeX.Packages.graphicx


class UnsupportedFiletypeException(Exception):
    pass


class includegraphics(plasTeX.Packages.graphicx.includegraphics):
    altText = None
    tex = None
    args = '* [ options:gfxdict ] file:str'

    def getImageSize(self, img):
        imgpath = Path(img)
        imgext = imgpath.suffix
        PILext = ['.png', '.jpg', '.jpeg', '.gif', '.eps', '.ps']
        PDFext = ['.pdf']

        if imgext in PILext:
            from PIL import Image
            w, h = Image.open(img).size
            return (w, h)
        elif imgext in PDFext:
            from pypdf import PdfReader
            pdfImage = PdfReader(img)
            box = pdfImage.getPage(0).mediaBox
            return (box.getWidth(), box.getHeight())
        else:
            raise UnsupportedFiletypeException("Reading the size of a {} file is not supported".format(imgext))

        return None

    def invoke(self, tex):
        res = Command.invoke(self, tex)

        f = self.attributes['file']
        ext = self.ownerDocument.userdata.getPath(
                    'packages/%s/extensions' % self.packageName,
                    ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.ps', '.eps'])
        ext = [''] + [e.lower() for e in ext]
        paths = self.ownerDocument.userdata.getPath('packages/%s/paths' % self.packageName, ['.'])
        img = None

        # Check for file using graphicspath
        for p in paths:
            for fp in Path(p).glob(f+'.*'):
                if fp.is_file() and fp.suffix.lower() in ext and fp.stem==Path(f).stem:
                    img = str(fp.resolve())
                    break

            if img is not None:
                break

        # Check for file using kpsewhich
        if img is None:
            for e in [''] + ext:
                try:
                    img = os.path.abspath(tex.kpsewhich(f + e))
                    break
                except (OSError, IOError):
                    pass

        options = self.attributes['options']

        if options is not None:
            altText = options.get('alt')
            if altText is not None:
                self.altText = altText

            scale = options.get('scale')
            if scale is not None and img is not None:
                scale = float(scale)
                w, h = self.getImageSize(img)
                self.style['width'] = '%spx' % (w * scale)
                self.style['height'] = '%spx' % (h * scale)

            height = options.get('height')
            if height is not None:
                self.style['height'] = height

            width = options.get('width')
            if width is not None:
                self.style['width'] = width

            def getdimension(s):
                m = re.match(r'^([\d\.]+)\s*([a-z]*)$', s)
                if m and '.' in m.group(1):
                    return float(m.group(1)), m.group(2)
                elif m:
                    return int(m.group(1)), m.group(2)

            keepaspectratio = options.get('keepaspectratio')
            if img is not None and keepaspectratio == 'true' and \
               height is not None and width is not None:
                w, h = self.getImageSize(img)

                height, hunit = getdimension(height)
                width, wunit = getdimension(width)

                scalex = float(width) / w
                scaley = float(height) / h

                if scaley > scalex:
                    height = h * scalex
                else:
                    width = w * scaley

                self.style['width'] = '%s%s' % (width, wunit)
                self.style['height'] = '%s%s' % (height, hunit)

        self.imageoverride = img
        self.ownerDocument.userdata.setPath('packages/chirun/currentimage', self)

        return res

    def castGfxDictionary(self, tokens, type=dict, **kwargs):
        delim = kwargs.get('delim')
        if delim is None:
            delim = ','
        dictarg = type()
        currentkey = []
        currentvalue = None
        while tokens:
            current = tokens.pop(0)

            if current.nodeType == Macro.ELEMENT_NODE:
                currentvalue.append(current)
                continue

            # Found grouping
            elif current.catcode == Token.CC_BGROUP:
                level = 1
                currentvalue.append(current)
                while tokens:
                    current = tokens.pop(0)
                    if current.catcode == Token.CC_BGROUP:
                        level += 1
                    elif current.catcode == Token.CC_EGROUP:
                        level -= 1
                        if not level:
                            break
                    currentvalue.append(current)
                currentvalue.append(current)
                continue

            # Found end-of-key delimiter
            if current == '=':
                currentvalue = []

            # Found end-of-value delimiter
            elif current == delim:
                # Handle this later
                pass

            # Extend key
            elif currentvalue is None:
                currentkey.append(current)

            # Extend value
            else:
                currentvalue.append(current)

            # Found end-of-value delimiter
            if current == delim or not tokens:
                currentkey = self.tex.normalize(currentkey)
                if currentkey == 'width' or currentkey == 'width':
                    currentvalue = self.tex.cast(currentvalue, 'dimen')
                else:
                    currentvalue = self.tex.cast(currentvalue, 'str')
                if currentvalue is None:
                    currentvalue = True
                dictarg[currentkey] = currentvalue
                currentkey = []
                currentvalue = None

        if currentkey:
            currentkey = self.tex.normalize(currentkey)
            if currentkey == 'width' or currentkey == 'width':
                currentvalue = self.tex.cast(currentvalue, 'dimen')
            else:
                currentvalue = self.tex.cast(currentvalue, 'str')
            if currentvalue is None:
                currentvalue = True
            dictarg[currentkey] = currentvalue

        return dictarg

    def preParse(self, tex):
        self.tex = tex
        tex.argtypes.update({'gfxdict': self.castGfxDictionary})
        return plasTeX.Packages.graphicx.includegraphics.preParse(self, tex)
