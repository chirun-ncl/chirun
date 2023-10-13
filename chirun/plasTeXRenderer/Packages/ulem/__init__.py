from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    add_package_templates(document, package='ulem')


class uline(Command):
    args = 'self'

class uuline(Command):
    args = 'self'


class uwave(Command):
    args = 'self'

    @property
    def source(self):
        return (r'\lower2pt\stackrel{{\large\smash{{{obj}}}}}{{\lower 3pt\sim}}'
                .format(obj=sourceArguments(self).strip()))

class sout(Command):
    args = 'self'

class xout(Command):
    args = 'self'

class dashuline(Command):
    args = 'self'

class dotuline(Command):
    args = 'self'
