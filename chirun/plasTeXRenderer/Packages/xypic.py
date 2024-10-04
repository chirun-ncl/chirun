from plasTeX.Base import Command
from plasTeX.Tokenizer import Token

class xymatrix(Command):
    args = 'picture'

    altText = None

    def parse(self, tex):
        self.argSource = ''
        while True:
            output, source = tex.readArgumentAndSource(parentNode=self)
            self.argSource += source
            if output is None or any(tok.catcode == Token.CC_BGROUP for tok in output):
                break

    def invoke(self, tex):
        gfx = super().invoke(tex)
        self.ownerDocument.userdata.setPath('packages/chirun/currentimage', self)
        return gfx
