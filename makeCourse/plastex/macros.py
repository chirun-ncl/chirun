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

class cssclass(Command):
    args = '[ classes:str ] content:str'

class iframe(Command):
    args = '[ options:dict ] content:str'

class div(Environment):
    args = '[ classes:str ]'

class eqref(Command):
    args = 'label:idref'

class rightline(Command):
    args = 'self'

class kframe(Environment):
    blockType = True
    def invoke(self, tex):
        a = self.parse(tex)
        colors = self.ownerDocument.userdata.getPath('packages/color/colors')
        self.style['background-color'] = colors['shadecolor']

class collapse(Command):
    blockType = True
    args = 'btnClass:str btnText:str parText hintText'

class collapsehint(Command):
    blockType = True
    args = 'hintText'

class collapsesolution(Command):
    blockType = True
    args = 'hintText'

class alttext(Command):
    args = 'text'
    def invoke(self, tex):
        Command.invoke(self,tex)
        doc = self.ownerDocument
        gfx = doc.userdata.getPath('packages/makecourse/currentimage')
        if gfx is not None:
            gfx.altText = self.attributes['text']
        else:
            raise RuntimeError('Cannot find a graphics item to attach \\alttext{} to. Ensure \
the graphicx or tikz package is loaded and a graphics item is defined \
before invoking \\alttext{}.')
