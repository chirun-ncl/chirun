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
                u.getPath('packages/xcolor/target_model'))

        res = Environment.invoke(self, tex)
        a = self.attributes
        options = {}
        options.update(self.boxOptions)
        extra_options = a.get('options')
        if extra_options:
            options.update(extra_options)

        colback = options.get('colback')
        if colback is not None:
            self.style['background-color'] = self.parser.parseColor(colback).html

        colframe = options.get('colframe')
        if colframe is not None:
            self.style['border-color'] = self.parser.parseColor(colframe).html

        boxrule = options.get('boxrule')
        if boxrule is not None:
            self.style['border-width'] = boxrule

        title = options.get('title')
        if title:
            self.title = title

        coltitle = options.get('coltitle')
        if coltitle is not None:
            self.title_style['color'] = coltitle

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
