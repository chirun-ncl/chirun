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
