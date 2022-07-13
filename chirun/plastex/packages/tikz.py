"""
Implement the tikz package using the imager
"""
from chirun.plastex import VerbatimEnvironment
from plasTeX import Command
from plasTeX.Packages import *


class tikzpicture(VerbatimEnvironment):
    altText = None

    def invoke(self, tex):
        gfx = super().invoke(tex)
        self.ownerDocument.userdata.setPath('packages/chirun/currentimage', self)
        return gfx
