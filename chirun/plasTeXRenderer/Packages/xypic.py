from plasTeX.Base import Command

class xymatrix(Command):
    args = 'picture'

    altText = None

    def invoke(self, tex):
        gfx = super().invoke(tex)
        self.ownerDocument.userdata.setPath('packages/chirun/currentimage', self)
        return gfx
