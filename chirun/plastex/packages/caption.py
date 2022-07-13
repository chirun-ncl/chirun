from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX.Base.LaTeX import Floats


def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5', package='caption')
    document.addPackageResource([tpl])


class Caption(Floats.Caption):
    args = '* [ toc ] self'


class figure(Floats.Float):
    class caption(Caption):
        counter = 'figure'
        templateName = 'nestedfigurecaption'
