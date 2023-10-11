from chirun.plasTeXRenderer import add_package_templates
from plasTeX import Command


def ProcessOptions(options, document):
    add_package_templates(document, package='polynom')


class polylongdiv(Command):
    args = 'a b'


class polylonggcd(Command):
    args = 'a b'
