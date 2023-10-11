"""
Implement the tikz package using the imager
"""
from chirun.plastex import VerbatimEnvironment
from plasTeX import Command


class tikzpicture(VerbatimEnvironment):
    altText = None

    def invoke(self, tex):
        gfx = VerbatimEnvironment.invoke(self, tex)
        self.ownerDocument.userdata.setPath('packages/chirun/currentimage', self)
        return gfx


class tikzcd(VerbatimEnvironment):
    pass


class usetikzlibrary(Command):
    args = "library"


class tikzset(Command):
    args = "library"
