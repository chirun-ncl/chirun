from plasTeX.PackageResource import (PackageResource, PackageCss, PackageJs, PackageTemplateDir)
from plasTeX import Command, Environment, sourceArguments
from plasTeX.Base.LaTeX import Math, Lists, Floats

def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5',package='caption')
    document.addPackageResource([tpl])

class Caption(Floats.Caption):
    args = '* [ toc ] self'

class figure(Floats.Float):
    class caption(Caption):
        counter = 'figure'
        templateName = 'nestedfigurecaption'
