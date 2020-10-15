import os,re
import plasTeX
from plasTeX import Macro,Token,Command
from plasTeX.Packages.graphicx import *
import plasTeX.Packages.graphicx

class includegraphics(plasTeX.Packages.graphicx.includegraphics):
    altText = None
    tex = None
    args = '* [ options:gfxdict ] file:str'

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

    def invoke(self, tex):
        plasTeX.Packages.graphicx.includegraphics.invoke(self,tex)
        self.ownerDocument.userdata.setPath('packages/makecourse/currentimage', self)

