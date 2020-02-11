from plasTeX import Command, sourceChildren, sourceArguments, Environment
from plasTeX.Base.LaTeX import Math, Lists
from plasTeX.Base.LaTeX.Arrays import Array
from plasTeX.Base.TeX import Primitives
from plasTeX.Tokenizer import Token, EscapeSequence, Other
from plasTeX.Logging import getLogger

log = getLogger()

class label(Command):
    args = "label:id"
    def invoke(self, tex):
        # Allow _ character in labels
        catcode = self.ownerDocument.context.whichCode('_')
        self.ownerDocument.context.catcode('_', Token.CC_LETTER)
        a = self.parse(tex)
        self.ownerDocument.context.catcode('_', catcode)

class mbox(Primitives.BoxCommand):
    args = 'self'
    class math(Math.MathEnvironment):
        @property
        def source(self):
            if self.hasChildNodes():
                return u'$%s$' % sourceChildren(self)
            return '$'

class math(Math.math):
    @property
    def source(self):
        return sourceChildren(self).strip()
Math.math = math

class displaymath(Math.displaymath):
    @property
    def source(self):
        return sourceChildren(self).strip()
Math.displaymath = displaymath

class MathEnvironment(Math.Environment):
    mathMode = True
    @property
    def source(self):
        if self.ref:
            return u"\\begin{{{0}}}{1}\\tag{{{2}}}\\end{{{0}}}".format(
                self.tagName,
                sourceChildren(self).strip(),
                self.ref)
        else:
            return u"\\begin{{{0}}}{1}\\end{{{0}}}".format(
                self.tagName,
                sourceChildren(self).strip())
Math.MathEnvironment = MathEnvironment

class equation(MathEnvironment):
    blockType = True
    counter = 'equation'
Math.equation = equation

class EqnarrayStar(Math.EqnarrayStar):
    class ArrayCell(Math.EqnarrayStar.ArrayCell):
        @property
        def source(self):
            return '\\displaystyle {content}'.format(content=sourceChildren(self, par=False).strip())
    class ArrayRow(Array.ArrayRow):
        @property
        def source(self):
            name = self.parentNode.nodeName or 'array'
            escape = '\\'
            s = []
            argSource = sourceArguments(self.parentNode)
            if not argSource: 
                argSource = ' '
            if self.ref:
                s.append(r"\tag{%s}"%self.ref)
            for cell in self:
                s.append(sourceChildren(cell, par=not(self.parentNode.mathMode)))
                if cell.endToken is not None:
                    s.append(cell.endToken.source)
            if self.endToken is not None:
                s.append(self.endToken.source)
            return ''.join(s)
Math.EqnarrayStar = EqnarrayStar

class eqnarray(EqnarrayStar):
    macroName = None
    counter = 'equation'

    class EndRow(Array.EndRow):
        """ End of a row """
        counter = 'equation'
        def invoke(self, tex):
            res = Array.EndRow.invoke(self, tex)
            res[1].ref = self.ref
            self.ownerDocument.context.currentlabel = res[1]
            return res

    def invoke(self, tex):
        res = EqnarrayStar.invoke(self, tex)
        if self.macroMode == self.MODE_END:
            return res
        res[1].ref = self.ref
        return res
Math.eqnarray = eqnarray

class ThinSpace(Command):
    macroName = '.'
    str = '\u2009'

class NegativeThinSpace(Command):
    macroName = '!'

class MediumSpace(Command):
    macroName = ':'
    str = '\u2004'

class ThickSpace(Command):
    macroName = ';'
    str = '\u2002'

class ThinSpace_(Command):
    macroName = '/'
    str = '\u2009'

class List(Lists.List):
    def digest(self, tokens):
        if self.macroMode != Environment.MODE_END:
        # Drop any whitespace before the first item
            for tok in tokens:
                if tok.isElementContentWhitespace:
                    continue
                elif tok.nodeName == 'itemsep':
                    tok.digest([])
                    continue
                elif tok.nodeName == 'setcounter':
                    tok.digest([])
                    continue
                if tok.nodeName != 'item':
                    log.warning('dropping non-item from beginning of list')
                    continue
                tokens.push(tok)
                break
        Environment.digest(self, tokens)
Lists.List = List

class description(List):
    pass

class trivlist(List):
    pass

class itemize(List):
    pass

class ConfigurableList(List):
    macroName = 'list'
    args = 'defaultlabel decls:nox'

class enumerate_(List):
    macroName = 'enumerate'
    args = '[ type:str ]'

    def invoke(self, tex):
        Lists.List.invoke(self,tex)
        if 'type' in self.attributes:
            self.listType = self.attributes['type']
        self.listDepth = Lists.List.depth
