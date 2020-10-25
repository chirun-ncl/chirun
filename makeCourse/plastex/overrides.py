from plasTeX import Command, sourceChildren, sourceArguments, Environment, NewCommand
from plasTeX.Base.LaTeX import Math, Lists
from plasTeX.Base.LaTeX.Arrays import Array
from plasTeX.Base.TeX import Primitives
from plasTeX.Tokenizer import Token, Tokenizer, EscapeSequence, Other
from plasTeX.Logging import getLogger
from plasTeX.Context import Context

log = getLogger()

class label(Command):
    args = "label:id"
    def invoke(self, tex):
        # Allow _ character in labels
        catcode = self.ownerDocument.context.whichCode('_')
        self.ownerDocument.context.catcode('_', Token.CC_LETTER)
        a = self.parse(tex)
        self.ownerDocument.context.catcode('_', catcode)

# Overrive boxcommands inside MathJaX to avoid extra <script type="math/tex">
class BoxCommand(Primitives.BoxCommand):
    class math(Math.math):
        @property
        def source(self):
            if self.hasChildNodes():
                return u'\(%s\)' % sourceChildren(self)
            return '\('
class hbox(BoxCommand): pass
class vbox(BoxCommand): pass
class text(BoxCommand):
    args = 'self'
class mbox(BoxCommand):
    args = 'self'
class TextCommand(BoxCommand):
    pass

# Use <script type="math/tex"> to avoid problems with less than symbol in MathJax
class math(Math.math):
    @property
    def source(self):
        if self.hasChildNodes():
            return r'<script type="math/tex">{}</script>'.format(sourceChildren(self))
        return ''
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

class MathShift(Command):
    """
    The '$' character in TeX
    This macro detects whether this is a '$' or '$$' grouping.  If
    it is the former, a 'math' environment is invoked.  If it is
    the latter, a 'displaymath' environment is invoked.
    """
    macroName = 'active::$'
    inEnv = []

    def invoke(self, tex):
        r"""
        This gets a bit tricky because we need to keep track of both
        our beginning and ending.  We also have to take into
        account \mbox{}es.
        """
        inEnv = type(self).inEnv

        current = self.ownerDocument.createElement('math')
        for t in tex.itertokens():
            if t.catcode == Token.CC_MATHSHIFT:
                if inEnv and inEnv[-1] is not None and type(inEnv[-1]) is type(current):
                    # Don't switch to displaymath element if already inside a math element
                    tex.pushToken(t)
                else:
                    current = self.ownerDocument.createElement('displaymath')
            else:
                tex.pushToken(t)
            break

        # See if this is the end of the environment
        if inEnv and inEnv[-1] is not None and type(inEnv[-1]) is type(current):
            inEnv.pop()
            current.macroMode = Command.MODE_END
            self.ownerDocument.context.pop(current)
            return [current]

        inEnv.append(current)
        self.ownerDocument.context.push(current)

        return [current]
Primitives.MathShift = MathShift


def newcommand(self, name, nargs=0, definition=None, opt=None):
    if nargs is None:
        nargs = 0
    assert isinstance(nargs, int), 'nargs must be an integer'

    if isinstance(definition, str):
        definition = [x for x in Tokenizer(definition, self)]

    if isinstance(opt, str):
        opt = [x for x in Tokenizer(opt, self)]

    newclass = type(name, (NewCommand,),
                   {'nargs':nargs, 'opt':opt, 'definition':definition})

    self.addGlobal(name, newclass)
Context.newcommand = newcommand

def newenvironment(self, name, nargs=0, def_before=None, def_after=None, opt=None):
    if nargs is None:
        nargs = 0
    assert isinstance(nargs, int), 'nargs must be an integer'

    if def_before:
        def_before = list(Tokenizer(def_before, self))
    if def_after:
        def_after = list(Tokenizer(def_after, self))

    if isinstance(opt, str):
        opt = [x for x in Tokenizer(opt, self)]

    # Begin portion
    newclass = type(name, (NewCommand,),
                   {'nargs':nargs, 'opt':opt, 'definition':def_before})
    self.addGlobal(name, newclass)

    # End portion
    newclass = type('end' + name, (NewCommand,),
                   {'nargs':0, 'opt':None, 'definition':def_after})
    self.addGlobal('end' + name, newclass)
Context.newenvironment = newenvironment

class Roman(Command):
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(self.ownerDocument.context.counters[a['name']].Roman)
