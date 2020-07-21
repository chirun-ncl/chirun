import plasTeX
from plasTeX import Command

class includegraphics(plasTeX.Packages.graphicx.includegraphics):
    altText = None

    def invoke(self, tex):
        plasTeX.Packages.graphicx.includegraphics.invoke(self,tex)
        self.ownerDocument.userdata.setPath('packages/makecourse/currentimage', self)

class alt(Command):
    args = 'text'
    def invoke(self, tex):
        Command.invoke(self,tex)
        doc = self.ownerDocument
        gfx = doc.userdata.getPath('packages/makecourse/currentimage')
        gfx.altText = self.attributes['text']
