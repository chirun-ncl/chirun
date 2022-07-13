from plasTeX import Command
from plasTeX.PackageResource import PackageTemplateDir


def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5', package='polynom')
    document.addPackageResource([tpl])


class polylongdiv(Command):
    args = 'a b'


class polylonggcd(Command):
    args = 'a b'
