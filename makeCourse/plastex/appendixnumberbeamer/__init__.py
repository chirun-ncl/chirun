from plasTeX.PackageResource import (PackageResource, PackageCss, PackageJs, PackageTemplateDir)
from plasTeX import Command, Environment, sourceArguments

def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5',package='appendixnumberbeamer')
    document.addPackageResource([tpl])

class appendix(Command):
    args = ''
