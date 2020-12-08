from plasTeX import VerbatimEnvironment
from plasTeX import Command

class tikzpicture(VerbatimEnvironment):
    altText = None
    def invoke(self, tex):
        gfx = VerbatimEnvironment.invoke(self,tex)
        self.ownerDocument.userdata.setPath('packages/makecourse/currentimage', self)
        return gfx

class usetikzlibrary(Command):
    args = "library"

class tikzset(Command):
    args = "library"
