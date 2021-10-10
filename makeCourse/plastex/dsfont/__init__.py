from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5', package='dsfont')
    document.addPackageResource([tpl])


class mathds(Command):
    args = 'obj'

    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())
