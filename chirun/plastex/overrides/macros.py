from plasTeX import Base, Command, Environment
from plasTeX.Base.TeX import Primitives

class ifpdflatex(Primitives.iffalse):
    """ An \if command whose "true" case is only applied when rendering the content in pdflatex.
        The "else" command is used when rendering HTML with plasTeX.

        Equivalent to \ifplastex with the cases swapped.
    """
    pass


############################
# Embedding external content
############################

class numbas(Command):
    """ Embed a Numbas exam.
    
        The required argument ``content`` is the URL of the exam.
    """
    args = 'content:str'


class vimeo(Command):
    """ Embed a Vimeo video.
    
        The required argument ``content`` is the video's ID.
    """
    args = 'content:str'


class youtube(Command):
    """ Embed a YouTube video.
    
        The required argument ``content`` is the video's ID.
    """
    args = '[ intro:str ] content:str'


class embed(Command):
    """ Embed something using the oEmbed protocol.

        The required argument ``content`` is the URL of the page to fetch the oEmbed data from.
    """
    args = 'content:str'

class iframe(Command):
    """ Embed another page in an <iframe> element.

        Options:
            * ``width``
            * ``height``
            * ``style``

        The required argument ``content`` is the URL of the page to load.
    """
    args = '[ options:dict ] content:str'


######################
# Runnable code editor
######################

class runnableCode(Base.verbatim):
    args = 'language:str'


#######
# knitr
#######

class kframe(Environment):
    """ kframe environment from knitr """
    blockType = True

    def invoke(self, tex):
        self.parse(tex)
        colors = self.ownerDocument.userdata.getPath('packages/color/colors')
        self.style['background-color'] = colors['shadecolor']

####################
# Collapsible blocks
####################

class collapseEnv(Environment):
    args = 'btnClass:str btnText:str parText'
    blockType = True


class collapse(Command):
    blockType = True
    args = 'btnClass:str btnText:str parText hintText'


class collapsehint(Command):
    blockType = True
    args = 'hintText'


class collapsesolution(Command):
    blockType = True
    args = 'hintText'


################
# Image alt text
################

class alttext(Command):
    """ Add alt text to an image.
    """

    args = 'text'

    def invoke(self, tex):
        Command.invoke(self, tex)
        doc = self.ownerDocument
        gfx = doc.userdata.getPath('packages/chirun/currentimage')
        if gfx is not None:
            gfx.altText = self.attributes['text']
        else:
            raise RuntimeError('Cannot find a graphics item to attach \\alttext{} to. Ensure \
the graphicx or tikz package is loaded and a graphics item is defined \
before invoking \\alttext{}.')
