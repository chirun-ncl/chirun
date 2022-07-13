from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX import Environment

from chirun.plastex.packages.color import latex2htmlcolor


def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5', package='tcolorbox')
    document.addPackageResource([tpl])


class tcolorbox(Environment):
    args = '[ options:dict ]'
    blockType = True

    def invoke(self, tex):
        res = Environment.invoke(self, tex)
        a = self.attributes
        if a.get('options'):
            if a['options'].get('colback'):
                a['colback'] = latex2htmlcolor(a['options']['colback'],
                                               named=self.ownerDocument.userdata.getPath('packages/color/colors'))
        return res
