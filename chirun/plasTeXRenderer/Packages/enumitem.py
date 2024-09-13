from plasTeX import Command, encoding
from plasTeX.Base.LaTeX import Lists
from plasTeX.encoding import numToRoman, numToAlpha
import re

List = Lists.List

class enumerate_(Lists.enumerate_):
    macroName = 'enumerate'
    args = '[ options:dict:nox ]'
    refLabel = None

    class item(List.item):
        def invoke(self, tex):
            ret = List.item.invoke(self, tex)
            self.refLabel = enumerate_.refLabel
            return ret

        @property
        def ref(self):
            if self.refLabel:
                try:
                    position = int(self.origref.textContent)
                    alph = encoding.stringletters()[position - 1]
                    t = re.sub(r'_Alph_', alph.upper(), str(self.refLabel))
                    t = re.sub(r'_alph_', alph.lower(), t)
                    t = re.sub(r'_Roman_', numToRoman(position), t)
                    t = re.sub(r'_roman_', numToRoman(position).lower(), t)
                    t = re.sub(r'_arabic_', str(position), t)
                    return t
                except Exception:
                    pass
            return self.origref

        @ref.setter
        def ref(self, value):
            self.origref = value

    class arabicStar(Command):
        macroName = 'arabic'
        args = '*'

        def invoke(self, tex):
            self.parse(tex)
            return tex.textTokens('_arabic_')

    class romanStar(Command):
        macroName = 'roman'
        args = '*'

        def invoke(self, tex):
            self.parse(tex)
            return tex.textTokens('_roman_')

    class RomanStar(Command):
        macroName = 'Roman'
        args = '*'

        def invoke(self, tex):
            self.parse(tex)
            return tex.textTokens('_Roman_')

    class alphStar(Command):
        macroName = 'alph'
        args = '*'

        def invoke(self, tex):
            self.parse(tex)
            return tex.textTokens('_alph_')

    class AlphStar(Command):
        macroName = 'Alph'
        args = '*'

        def invoke(self, tex):
            self.parse(tex)
            return tex.textTokens('_Alph_')

    def invoke(self, tex):
        List.invoke(self, tex)
        enumerate_.refLabel = None
        self.listLabel = None
        self .listDepth = List.depth
        if 'options' in self.attributes:
            opt = self.attributes['options']
            if opt is not None:
                if 'label' in opt:
                    self.listLabel = opt['label']
                if 'ref' in opt:
                    enumerate_.refLabel = opt['ref']

    def term(self, position):
        alph = encoding.stringletters()[position - 1]
        if self.listLabel:
            t = re.sub(r'_Alph_', alph.upper(), str(self.listLabel))
            t = re.sub(r'_alph_', alph.lower(), t)
            t = re.sub(r'_roman_', numToRoman(position), t)
            t = re.sub(r'_Roman_', numToRoman(position).lower(), t)
            t = re.sub(r'_arabic_', str(position), t)
        elif self.listDepth == 2:
            t = '({})'.format(alph.lower())
        elif self.listDepth == 3:
            t = '{}.'.format(numToRoman(position).lower())
        elif self.listDepth == 4:
            t = '{}.'.format(alph.upper())
        else:
            t = '{}.'.format(position)
        return t

class itemize(Lists.itemize):
    args = '[ options:dict:nox ]'
