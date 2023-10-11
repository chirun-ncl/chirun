from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    add_package_templates(document, package='ulem')


class uline(Command):
    args = 'obj'


class uwave(Command):
    args = 'obj'

    @property
    def source(self):
        return (r'\lower2pt\stackrel{{\large\smash{{{obj}}}}}{{\lower 3pt\sim}}'
                .format(obj=sourceArguments(self).strip()))
