from chirun.plasTeXRenderer import add_package_templates
from plasTeX.Base.LaTeX import Floats


def ProcessOptions(options, document):
    add_package_templates(document, package='caption')


class Caption(Floats.Caption):
    args = '* [ toc ] self'


class figure(Floats.Float):
    class caption(Caption):
        counter = 'figure'
        templateName = 'nestedfigurecaption'
