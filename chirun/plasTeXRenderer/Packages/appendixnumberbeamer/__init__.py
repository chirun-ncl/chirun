from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command


def ProcessOptions(options, document):
    add_package_templates(document, package='appendixnumberbeamer')


class appendix(Command):
    args = ''
