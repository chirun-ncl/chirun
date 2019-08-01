from plasTeX import Command, sourceChildren, Environment
from plasTeX.Base.LaTeX import Math

class numbas(Command):
    args = '[ intro:str ] content:str'

class vimeo(Command):
    args = '[ intro:str ] content:str'

class youtube(Command):
    args = '[ intro:str ] content:str'

class embed(Command):
    args = 'content:str'

class math(Math.math):
    @property
    def source(self):
        return '<script type="math/tex">{content}</script>'.format(content=sourceChildren(self).strip())

class cssclass(Command):
    args = '[ classes:str ] content:str'

class div(Environment):
    args = '[ classes:str ]'
