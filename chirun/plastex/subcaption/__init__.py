from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX import Command
from plasTeX.Base.LaTeX.Boxes import minipage
from plasTeX.Base.LaTeX.Floats import figure, table, Caption


def ProcessOptions(options, document):
    context = document.context
    tpl = PackageTemplateDir(renderers='html5', package='subcaption')
    context.newcounter('subfigure', resetby='figure', format='${thefigure}${subfigure.alph}')
    context.newcounter('subtable', resetby='table', format='${thetable}${subtable.alph}')
    document.addPackageResource([tpl])


class subref(Command):
    args = '* label:idref'


class subfigure(minipage):
    pass


class _subcaption(Caption):
    templateName = 'subcaption'

    @property
    def ref(self):
        return self.subref

    @ref.setter
    def ref(self, value):
        self.figref = value
        self.subref = self.ownerDocument.context.counters[self.counter].alph


class _figure(figure):
    macroName = "figure"
    counter = 'figure'

    class caption(Caption):
        counter = 'figure'

        def preParse(self, tex):
            doc = self.ownerDocument
            c = doc.context
            c.counters[self.counter].setcounter(c.counters[self.counter].value - 1)

    class subcaption(_subcaption):
        counter = 'subfigure'

    class subfigure(subfigure):
        class caption(_subcaption):
            counter = 'subfigure'


class subtable(minipage):
    pass


class _table(table):
    macroName = "table"
    counter = 'table'

    class caption(Caption):
        counter = 'table'

        def preParse(self, tex):
            doc = self.ownerDocument
            c = doc.context
            c.counters[self.counter].setcounter(c.counters[self.counter].value - 1)

    class subcaption(_subcaption):
        counter = 'subtable'

    class subtable(subtable):
        class caption(_subcaption):
            counter = 'subtable'


class captionsetup(Command):
    args = '[ type:str ] options:dict'
