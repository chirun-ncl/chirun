from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX import Command


def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5', package='appendixnumberbeamer')
    document.addPackageResource([tpl])


class appendix(Command):
    args = ''
