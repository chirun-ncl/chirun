from plasTeX.PackageResource import (
        PackageResource, PackageCss, PackageJs, PackageTemplateDir)
from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Lists import List

from makeCourse.plastex.color import latex2htmlcolor

def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5',package='tcolorbox')
    document.addPackageResource([tpl])

class tcolorbox(Environment):
    args = '[ options:dict ]'
    blockType = True

    def invoke(self,tex):
        res = Environment.invoke(self,tex)
        if self.attributes.get('options'):
            if self.attributes['options'].get('colback'):
                self.attributes['colback'] = latex2htmlcolor(self.attributes['options']['colback'],
                        named=self.ownerDocument.userdata.getPath('packages/color/colors'))
        return res