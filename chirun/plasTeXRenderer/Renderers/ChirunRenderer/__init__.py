from babel.support import Translations
import collections.abc
from jinja2 import Environment, contextfunction
from pathlib import Path
import pdb
from plasTeX.DOM import Node
from plasTeX.Renderers.HTML5 import Renderer as _Renderer
from plasTeX.Renderers import Renderer as BaseRenderer, Renderable as BaseRenderable
from plasTeX.Logging import getLogger

log = getLogger()


@contextfunction
def debug(context):
    pdb.set_trace()


jinja_env = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    extensions=['jinja2.ext.i18n',]
)
jinja_env.globals['debug'] = debug


def jinja2template(s, encoding='utf8'):
    def renderjinja2(obj, s=s):
        tvars = {'here': obj,
                 'obj': obj,
                 'container': obj.parentNode,
                 'config': obj.ownerDocument.config,
                 'context': obj.ownerDocument.context,
                 'templates': obj.renderer}

        tpl = jinja_env.from_string(s)
        return tpl.render(tvars)

    return renderjinja2


class Renderable(BaseRenderable):
    @property
    def vectorImage(self):
        name = getattr(self, 'imageoverride', None)
        if name is not None:
            r = Node.renderer
            if Path(name).suffix not in r.vectorImageTypes:
                return Node.renderer.imager.getImage(self)

        image = Node.renderer.vectorImager.getImage(self)
        return image


class ChirunRenderer(_Renderer):
    """Modified HTML5 renderer for Chirun."""

    imageTypes = ['.svg', '.png', '.jpg', '.jpeg', '.gif']
    vectorImageTypes = ['.svg', '.pdf']

    renderableClass = Renderable
    postProcessFile = None

    def __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)

        # Use the customised jinja2 engine to add translations.
        self.loadedTheme = None
        self.engines = {}
        self.registerEngine('jinja2', None, '.jinja2', jinja2template)

    def loadTemplates(self, document):
        try:
            with open(document.userdata['translations_path'], 'rb') as translations_file:
                jinja_env.install_gettext_translations(Translations(translations_file), newstyle=True)
        except (FileNotFoundError, KeyError):
            jinja_env.install_null_translations(newstyle=True)

        super().loadTemplates(document)

    def cleanup(self, document, files, postProcess=None):
        """
        Cleanup method called at the end of rendering.
        Copied from plasTeX's `Renderer.cleanup`, but it gets the postProcess function from an attribute of the object, because the PageTemplate renderer doesn't pass it through.
        """
        if self.processFileContent is Renderer.processFileContent:
            return

        encoding = document.config['files']['output-encoding']
        errs = self.encodingErrors
        for f in files:
            try:
                with open(f, 'r', encoding=encoding, errors=errs) as fd:
                    s = fd.read()

            except IOError as msg:
                log.error(msg)
                continue

            postProcess = postProcess if postProcess is not None else self.postProcessFile
            s = self.processFileContent(document, s)
            if isinstance(postProcess, collections.abc.Callable):
                s = postProcess(document, s, f)

            with open(f, 'w', encoding=encoding) as fd:
                fd.write(''.join(s))


Renderer = ChirunRenderer
