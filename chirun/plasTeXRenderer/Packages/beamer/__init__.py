from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command, Environment
from plasTeX.TeX import TeX
from plasTeX.Base.LaTeX import Sectioning
import plasTeX.Packages.beamer


def ProcessOptions(options, document):
    context = document.context

    tex = TeX(ownerDocument=document)
    document.context.loadPackage(tex, 'graphicx.sty', {})

    # Lists
    context.newcounter('enumi')
    context.newcounter('enumii', resetby='enumi')
    context.newcounter('enumiii', resetby='enumii')
    context.newcounter('enumiv', resetby='enumiii')

    add_package_templates(document, package='beamer')


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


class insertsectionhead(Command):
    blockType = True


class insertsubsectionhead(Command):
    blockType = True


class insertsubsubsectionhead(Command):
    blockType = True


class thesection(Command):
    pass


class thesubsection(Command):
    pass


class sectionname(Command):
    pass


class subsectionname(Command):
    pass


class usebeamerfont(Command):
    args = 'name'


class usebeamercolor(Command):
    args = '[layer] name'


class section(Sectioning.StartSection):
    level = Command.SECTION_LEVEL
    counter = 'section'

    def invoke(self, tex):
        Sectioning.StartSection.invoke(self, tex)
        toks = self.ownerDocument.userdata.getPath('packages/beamer/atbeginsection')
        if toks is not None and self.attributes['*modifier*'] != '*':
            tex.pushTokens(toks)


class AtBeginSection(Command):
    args = '[ special ] text:nox'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata.setPath('packages/beamer/atbeginsection', self.attributes['text'])
