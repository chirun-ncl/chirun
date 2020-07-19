"""
Implement the tikz package for html output.
The original tikz and latex do most of the work and then pdf2svg (or similar
software) turns it into a svg image.
Needs Beautiful Soup, Jinja2, and pdf2svg or similar
"""

import os
import string
import subprocess
import shutil
import tempfile
from plasTeX import Environment, NoCharSubEnvironment, Macro, sourceChildren
from plasTeX.PackageResource import PackageResource

from plasTeX.Logging import getLogger
log = getLogger()

try:
    from jinja2 import Template
except ImportError:
    log.warning('Cannot find jinja2 lib. Cannot use tikz.')

try:
    from bs4 import BeautifulSoup
except ImportError:
    log.warning('Cannot find BeautifulSoup lib. Cannot use tikz.')


class tikzpicture(NoCharSubEnvironment):
    """
    A tikz picture whose content will be converted in the processFileContent callback.
    """
    class matrix(Environment):
        """
        Avoids conflict with amsmath matrix thanks to the context stack
        mechanism.
        """

    class textwidth(Macro):
        """ Only avoids unrecognized command warning. """

    class draw(Macro):
        """ Only avoids unrecognized command warning. """

    class fill(Macro):
        """ Only avoids unrecognized command warning. """

    class filldraw(Macro):
        """ Only avoids unrecognized command warning. """

    class node(Macro):
        """ Only avoids unrecognized command warning. """

    class path(Macro):
        """ Only avoids unrecognized command warning. """

    class clip(Macro):
        """ Only avoids unrecognized command warning. """

    class axis(Environment):
        """ Only avoids unrecognized command warning. """

    class groupplot(Environment):
        """ Only avoids unrecognized command warning. """

    class scope(Environment):
        """ Only avoids unrecognized command warning. """
        args='*'

    class MathEnvironment(Environment):
        mathMode = True

    class math(MathEnvironment):
        @property
        def source(self):
            if self.hasChildNodes():
                return u'$%s$' % sourceChildren(self)
            return '$'

def tikzConvert(document, content, envname, placeholder):
    cwd = os.getcwd()
    tmp_dir = document.userdata[envname]['tmp_dir']
    outdir = document.config['files']['directory']
    outdir = string.Template(outdir).substitute(
            {'jobname': document.userdata.get('jobname', '')})
    target_dir = os.path.join(cwd, 'images')
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    template = document.userdata[envname]['template']
    compiler = document.userdata[envname]['compiler']
    pdf2svg = document.userdata[envname]['pdf2svg']
    os.chdir(tmp_dir)
    soup = BeautifulSoup(content, "html.parser")
    encoding = soup.original_encoding

    envs = soup.findAll(envname)
    for env in envs:
        object_id = env.attrs['id']
        basepath = os.path.join(tmp_dir, object_id)
        texpath = basepath + '.tex'
        pdfpath = basepath + '.pdf'
        svgpath =  basepath + '.svg'

        context = { 'tikzpicture': env.text.strip() }
        template.stream(**context).dump(texpath, encoding)

        subprocess.call([compiler, texpath])
        subprocess.call([pdf2svg, pdfpath, svgpath])
        destination = os.path.join(target_dir, object_id+'.svg')
        if os.path.isfile(destination):
            os.remove(destination)
        shutil.move(svgpath, target_dir)

        obj = soup.new_tag(
                'object', 
                type='image/svg+xml',
                data='images/' + object_id + '.svg')
        obj.string = document.context.terms.get(
                placeholder,
                placeholder) + '\n' + env.text.strip()
        obj.attrs['class'] = envname
        div = soup.new_tag('div')
        div.attrs['class'] = envname
        div.insert(1, obj)

        env.replace_with(div)
    os.chdir(cwd)
    try:
        # python2
        result = unicode(soup)
    except NameError:
        # python3
        result = str(soup)
    return result

def ProcessOptions(options, document):
    """This is called when the package is loaded."""
    
    try:
        with open(document.userdata['tikz-template'], "r") as file:
            template = file.read()
    except:
        log.info('Using default TikZ template.')
        template = u"\\documentclass{standalone}\n\\usepackage{tikz}" + \
                   u"\\begin{document}{{ tikzpicture }}\\end{document}"
    document.userdata['tikzpicture'] = {
            'template': Template(template),
            'tmp_dir': tempfile.mkdtemp(),
            'compiler': document.config['html5']['tikz-compiler'],
            'pdf2svg': document.config['html5']['tikz-converter'],
            }

    def convert(document, content):
        return tikzConvert(document, content, 'tikzpicture', 'TikZ picture')

    cb = PackageResource(
            renderers='html5',
            key='processFileContents',
            data=convert) 
    document.addPackageResource(cb)
