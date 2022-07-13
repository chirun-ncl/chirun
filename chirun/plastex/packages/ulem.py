from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5', package='ulem')
    document.addPackageResource([tpl])


class uline(Command):
    args = 'obj'


class uwave(Command):
    args = 'obj'

    @property
    def source(self):
        return (r'\lower2pt\stackrel{{\large\smash{{{obj}}}}}{{\lower 3pt\sim}}'
                .format(obj=sourceArguments(self).strip()))
