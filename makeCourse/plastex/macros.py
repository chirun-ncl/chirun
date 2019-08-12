from plasTeX import Command, sourceChildren, Environment
from plasTeX.Base.LaTeX import Math
from plasTeX.Base.TeX import Primitives
from plasTeX.Tokenizer import Token, EscapeSequence, Other


class numbas(Command):
    args = '[ intro:str ] content:str'

class vimeo(Command):
    args = '[ intro:str ] content:str'

class youtube(Command):
    args = '[ intro:str ] content:str'

class embed(Command):
    args = 'content:str'

class cb_math(Math.math):
    @property
    def source(self):
        return sourceChildren(self).strip()

class displaymath(Math.displaymath):
    @property
    def source(self):
        return sourceChildren(self).strip()

class EqnarrayStar(Math.EqnarrayStar):
    class ArrayCell(Math.EqnarrayStar.ArrayCell):
        @property
        def source(self):
            return '\\displaystyle {content}'.format(content=sourceChildren(self, par=False).strip())

class MathShift(Primitives.MathShift):
    def invoke(self, tex):
        inEnv = type(self).inEnv
        current = self.ownerDocument.createElement('cb_math')
        for t in tex.itertokens():
            if t.catcode == Token.CC_MATHSHIFT:
                current = self.ownerDocument.createElement('displaymath')
            else:
                tex.pushToken(t)
            break
        if inEnv and inEnv[-1] is not None and type(inEnv[-1]) is type(current):
            inEnv.pop()
            current.macroMode = Command.MODE_END
            self.ownerDocument.context.pop(current)
            return [current]
        inEnv.append(current)
        self.ownerDocument.context.push(current)
        return [current]

class cssclass(Command):
    args = '[ classes:str ] content:str'

class div(Environment):
    args = '[ classes:str ]'
