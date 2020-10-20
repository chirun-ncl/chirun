from plasTeX.Packages.beamer import *
import plasTeX.Packages.beamer

class frame(plasTeX.Packages.beamer.frame):
    blockType = True

class frameenv(plasTeX.Packages.beamer.frameenv):
    blockType = True
    def addToFrames(self):
        """ Add this frame to the frame collection """
        u = self.ownerDocument.userdata
        frames = u.get('frames')
        if frames is None:
            frames = []
            u['frames'] = frames
        self.subtitle = self.attributes['subtitle']
        frames.append(self)

class columns(plasTeX.Packages.beamer.columns):
    blockType = True

class column(plasTeX.Packages.beamer.column):
    args = '[ placement ] width:dimen'
    blockType = True

class columnenv(Environment):
    args = column.args
    blockType = True

class frametitle(plasTeX.Packages.beamer.frametitle):
    blockType = True

class framesubtitle(plasTeX.Packages.beamer.framesubtitle):
    blockType = True
