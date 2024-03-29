from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    add_package_templates(document, package='dsfont')


class mathds(Command):
    args = 'self'

    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())
