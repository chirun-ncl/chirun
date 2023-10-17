from babel.support import Translations
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

Renderer = ChirunRenderer
