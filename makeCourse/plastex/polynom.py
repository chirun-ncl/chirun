from plasTeX import Environment, Command
from plasTeX.PackageResource import PackageResource, PackageCss, PackageJs, PackageTemplateDir

def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5',package='polynom')
    document.addPackageResource([tpl])

class polylongdiv(Command):
    args = 'a b'

class polylonggcd(Command):
    args = 'a b'
