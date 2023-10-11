from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    add_package_templates(document, package='bbm')


class mathbbm(Command):
    args = 'obj'

    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())
