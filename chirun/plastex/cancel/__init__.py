from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5', package='cancel')
    document.addPackageResource([tpl])


class cancel(Command):
    args = 'obj'

    @property
    def source(self):
        return r'\require{{cancel}}\cancel{obj}'.format(obj=sourceArguments(self).strip())
