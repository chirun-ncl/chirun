from plasTeX.ConfigManager import MultiStringOption, StringOption, BooleanOption, IntegerOption
from plasTeX.DOM import Node

def add_html_config(config):
    section = config.addSection('html5')

    section['extra-css'] = MultiStringOption(
        """ Extra css files to use """,
        options='--extra-css',
        default='',
    )

    section['extra-js'] = MultiStringOption(
        """ Extra javascript files to use """,
        options='--extra-js',
        default='',
    )

    section['theme-css'] = StringOption(
        """ Theme css file""",
        options='--theme-css',
        default='green',
    )

    section['use-theme-css'] = BooleanOption(
        """ Use theme css """,
        options='--use-theme-css !--no-theme-css',
        default=True,
    )

    section['use-theme-js'] = BooleanOption(
        """ Use theme javascript """,
        options='--use-theme-js !--no-theme-js',
        default=True,
    )

    section['display-toc'] = BooleanOption(
        """ Display table of contents on each page """,
        options='--display-toc !--no-display-toc',
        default=True,
    )

    section['localtoc-level'] = IntegerOption(
        """ Create local toc above this level """,
        options='--localtoc-level',
        default=Node.DOCUMENT_LEVEL - 1,
    )

    section['breadcrumbs-level'] = IntegerOption(
        """ Create breadcrumbs from this level """,
        options='--breadcrumbs-level',
        default=-10,
    )

    section['use-mathjax'] = BooleanOption(
        """ Use mathjax """,
        options='--use-mathjax !--no-mathjax',
        default=True,
    )

    section['mathjax-url'] = StringOption(
        """ Url of the MathJax lib """,
        options='--mathjax-url',
        default='http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML',
    )

    section['mathjax-dollars'] = BooleanOption(
        """ Use single dollars as math delimiter for mathjax """,
        options='--dollars !--no-dollars',
        default=False,
    )

    section['filters'] = MultiStringOption(
        """Comma separated list of commands to invoke on each output page.""",
        options='--filters',
        default='',
    )
