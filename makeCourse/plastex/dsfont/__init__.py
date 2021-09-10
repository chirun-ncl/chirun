from plasTeX.PackageResource import (PackageResource, PackageCss, PackageJs, PackageTemplateDir)
from plasTeX import Command, Environment, sourceArguments

def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5',package='dsfont')
    document.addPackageResource([tpl])

class mathds(Command):
    args = 'obj'
    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())

