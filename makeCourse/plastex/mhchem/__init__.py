from plasTeX import Command, Environment, sourceChildren
from plasTeX.Base.LaTeX import Math
from plasTeX.Base.TeX.Primitives import BoxCommand
# mhchem package - mostly handled by mathjax

# Overrive boxcommands inside MathJaX to avoid extra <script type="math/tex">
class MHBoxCommand(BoxCommand):
    class math(Math.math):
        @property
        def source(self):
            if self.hasChildNodes():
                return u'$%s$' % sourceChildren(self)
            return '$'

class ce(MHBoxCommand):
    args = 'self'

class pu(MHBoxCommand):
    args = 'self'
