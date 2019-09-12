from plasTeX.PackageResource import (
	PackageResource, PackageCss, PackageJs, PackageTemplateDir)
from plasTeX import Command, Environment

def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5',package='ulem')
    document.addPackageResource([tpl])

class uline(Command):
    args = 's:str'
