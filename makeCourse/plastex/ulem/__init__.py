from plasTeX.PackageResource import (
	PackageResource, PackageCss, PackageJs, PackageTemplateDir)
from plasTeX import Command, Environment, sourceArguments

def ProcessOptions(options, document):
    tpl = PackageTemplateDir(renderers='html5',package='ulem')
    document.addPackageResource([tpl])

class uline(Command):
    args = 'obj'

class uwave(Command):
    args = 'obj'
    @property
    def source(self):
        return r'\stackrel{{{obj}}}{{\tiny\sim}}'.format(obj=sourceArguments(self).strip())

