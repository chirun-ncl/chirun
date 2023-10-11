from chirun.plasTeXRenderer import add_package_templates
from chirun.plastex.overrides.natbib import citealt
from plasTeX import Command, Environment, TheCounter
from plasTeX.Base.LaTeX.Footnotes import footnote
from plasTeX.Base.LaTeX import Sectioning


def ProcessOptions(options, document):
    # Extend the article documentclass
    from plasTeX.Packages import article
    article.ProcessOptions(options, document)

    # Set the numbering formatting for subsection titles
    document.context['thesection'].format = '${section.Roman}.'
    document.context['thesubsection'].format = '${subsection.Alph}.'
    document.context['thesubsubsection'].format = '${subsubsection.arabic}.'
    document.context['theparagraph'].format = '${paragraph.alph}.'
    document.context['bibliography'].counter = 'section'
    document.context['bibliography'].level = Command.SECTION_LEVEL

    # Automatically import natbib with options
    from chirun.plastex.overrides import natbib
    natbib.ProcessOptions({'numbers': True, 'sort&compress': True}, document)

    # Use the jinja templates in plastexRenderer/revtex4-2/
    add_package_templates(document, package='revtex4-2')


# Override default section numbering depth to match revTeX documentclass
class section(Sectioning.section):
    def invoke(self, tex):
        self.config['document']['sec-num-depth'] = 6
        return Sectioning.section.invoke(self, tex)


# Change the behaviour in the appendices
class appendix(Command):
    class thesection(TheCounter):
        format = 'Appendix ${section.Alph}:'

    class thesubsection(TheCounter):
        format = '${section.Alph}${subsection.arabic}'

    class theequation(TheCounter):
        format = '${section.Alph}${equation.arabic}'

    def invoke(self, tex):
        # Reset section counters to 0 for A, B, C 'Alph' numbering
        self.ownerDocument.context.counters['section'].setcounter(0)
        self.ownerDocument.context.counters['equation'].setcounter(0)
        # Change section and equation numbering in an appendix
        self.ownerDocument.context['thesection'] = type(self).thesection
        self.ownerDocument.context['thesubsection'] = type(self).thesubsection
        self.ownerDocument.context['theequation'] = type(self).theequation


# Reimplement several revtex package/documentclass macros in Python
# These are all macros that should not be rendered immediately, but as part of the maintitle template
# We handle that in the revTeX jinja templates included above with PackageTemplateDir
class thanks(footnote):
    def invoke(self, tex):
        footnote.invoke(self, tex)
        self.ownerDocument.userdata['thanks'] = self


class preprint(Command):
    args = 'self'


class abstract(Environment):
    def digest(self, tokens):
        res = Environment.digest(self, tokens)
        if self.macroMode == self.MODE_BEGIN:
            self.ownerDocument.userdata['abstract'] = self
        return res


# Find all authors given so far with no affiliation and associate them with this one
class affiliation(Command):
    args = 'self'

    def invoke(self, tex):
        output = Command.invoke(self, tex)
        userdata = self.ownerDocument.userdata

        if 'affiliations' not in userdata:
            userdata['affiliations'] = []
        if 'author' in userdata:
            known = [author for a in userdata['affiliations'] for author in a.authors]
            self.authors = [author for author in userdata['author'] if author not in known]
            userdata['affiliations'].append(self)
        return output


# And do the similar logic for collaborations
class collaboration(Command):
    args = 'self'

    def invoke(self, tex):
        output = Command.invoke(self, tex)
        userdata = self.ownerDocument.userdata

        if 'collaborations' not in userdata:
            userdata['collaborations'] = []
        if 'author' in userdata:
            self.author = userdata['author'][-1]
            userdata['collaborations'].append(self)
        return output


# In this macro add to altaffiliations userdata and footnotes userdata
# That way, we can render from altaffiliations as part of the main title template,
# and the affiliation will also be included as part of the footnotes
class altaffiliation(Command):
    args = '[ prefix ] self'

    def invoke(self, tex):
        output = Command.invoke(self, tex)
        userdata = self.ownerDocument.userdata

        if self.attributes['prefix'] is not None:
            self.attributes['self'] = self.attributes['prefix'] + self.attributes['self']

        if 'footnotes' not in userdata:
            userdata['footnotes'] = []
        if 'altaffiliations' not in userdata:
            userdata['altaffiliations'] = []
        if 'author' in userdata:
            self.author = userdata['author'][-1]
            userdata['altaffiliations'].append(self)
            userdata['footnotes'].append(self)
            self.mark = self
        return output


# Make the email and homepage macros work in the same way as altaffiliation
class email(altaffiliation):
    pass


class homepage(altaffiliation):
    pass


# Render come commands by absorbing them here and adding them to the jinja template
class LaTeXe(Command):
    pass


class acknowledgments(Environment):
    pass


# Handle citations by mimicing macros in the natbib package
class onlinecite(citealt):
    pass


# Next, implement some functions required when parsing the revTeX .bbl file
# The ":nox" in the argument lists here means "no expand", since we don't
# really need to understand what's in these arguments to do the job.
# For more information on macro arguments, see plastex's macro API documentation


# Take in two arguments, return the first one only
class firstoftwo(Command):
    args = 'one:nox two:nox'
    macroName = '@firstoftwo'

    def invoke(self, tex):
        Command.invoke(self, tex)
        return self.attributes['one']


# Take in two arguments, return the second one only
class secondoftwo(Command):
    args = 'one:nox two:nox'
    macroName = '@secondoftwo'

    def invoke(self, tex):
        Command.invoke(self, tex)
        return self.attributes['two']


# Parse but ignore the spacefactor macro
# Explicitly take a Number so that it absorbs tokens until \relax
class spacefactor(Command):
    args = 'space:Number'
