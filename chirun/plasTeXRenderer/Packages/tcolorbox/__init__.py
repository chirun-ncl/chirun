from chirun.plasTeXRenderer import add_package_templates
import plasTeX.Packages.color
import plasTeX.Packages.xcolor
from plasTeX import Command, Environment, CSSStyles


def latex2htmlcolor(*args, **kwargs):
    return plasTeX.Packages.color.latex2htmlcolor(*args, named=self.ownerDocument.userdata.getPath('packages/color/colors'), **kwargs)

def ProcessOptions(options, document):
    add_package_templates(document, package='tcolorbox')

class tcolorbox(Environment):
    args = '[ options:dict ]'
    blockType = True
    boxName = None  # Custom boxes defined with ``\newtcolorbox`` set ``boxName``.
    boxOptions = {}

    def invoke(self, tex):
        self.title_style = CSSStyles()

        u = self.ownerDocument.userdata
        self.parser:plasTeX.Packages.xcolor.ColorParser = plasTeX.Packages.xcolor.ColorParser(
                u.getPath('packages/xcolor/colors'),
                u.getPath('packages/xcolor/target_model')) #copy of textcolor in xcolor.py to set up the parser correctly.

        res = Environment.invoke(self, tex)
        a = self.attributes
        options = {}
        options.update(self.boxOptions)
        extra_options = a.get('options')
        if extra_options:
            options.update(extra_options)

        colback = options.get('colback')
        if colback is not None:
            colback = self.parser.parseColor(colback)
            self.style['--colback'] = colback.html

        coltext = options.get('coltext')
        if coltext is not None:
            self.style['--colupper'] = self.style['--collower'] = self.parser.parseColor(coltext).html

        colupper = options.get('colupper')
        if colupper is not None:
            self.style['--colupper'] = self.parser.parseColor(colupper).html

        collower = options.get('collower')
        if collower is not None:
            self.style['--collower'] = self.parser.parseColor(collower).html

        colframe = options.get('colframe')
        if colframe is not None:
            self.style['--colframe'] = self.parser.parseColor(colframe).html

        boxrule = options.get('boxrule')
        if boxrule is not None:
            self.style['--boxrule'] = boxrule

        title = options.get('title')
        if title:
            self.title = title

        coltitle = options.get('coltitle')
        if coltitle is not None:
            self.title_style['color'] = self.parser.parseColor(coltitle).html

        return res


class newtcolorbox(Command):
    args = 'name:str options:dict'

    def invoke(self, tex):
        self.parse(tex)
        attrs = self.attributes
        name = attrs['name']
        options = attrs['options']

        # Begin portion
        newclass = type(name, (tcolorbox,), {'boxOptions': options, 'nodeName': 'tcolorbox', 'boxName': name, })
        self.ownerDocument.context.addGlobal(name, newclass)
