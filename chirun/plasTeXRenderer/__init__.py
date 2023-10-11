from pathlib import Path
from plasTeX.PackageResource import PackageTemplateDir

def add_package_templates(document, package):
    path = Path(__file__).parent / 'Renderers' / 'ChirunRenderer' / package
    tpl = PackageTemplateDir(renderers='html5', path=path)
    document.addPackageResource([tpl])
