from plasTeX import Command
from plasTeX.Base.TeX.Primitives import BoxCommand
from plasTeX.Logging import getLogger
log = getLogger()


class ThinSpace(Command):
    macroName = '.'
    str = '\u2009'


class NegativeThinSpace(Command):
    macroName = '!'


class MediumSpace(Command):
    macroName = ':'
    str = '\u2004'


class ThickSpace(Command):
    macroName = ';'
    str = '\u2002'


class ThinSpace_(Command):
    macroName = '/'
    str = '\u2009'


class underline(BoxCommand):
    pass
