from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command, sourceArguments


def ProcessOptions(options, document):
    add_package_templates(document, package='cancel')


class cancel(Command):
    args = 'obj'

    @property
    def source(self):
        return r'\require{{cancel}}\cancel{obj}'.format(obj=sourceArguments(self).strip())
