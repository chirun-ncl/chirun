# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'Chirun'
copyright = 'Digital Learning Unit, Newcastle University'
author = 'Digital Learning Unit, Newcastle University'

language = 'en'

release = '0.8.0'
version = '0.8.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_book_theme'

html_logo = '_static/images/chirun_logo.png'

html_theme_options = {
    'logo': {
        'text': 'Chirun documentation',
        'alt_text': 'Chirun documentation home',
    },
    'path_to_docs': 'chirun/docs',
    'repository_url': 'https://github.com/chirun-ncl/chirun',
    'repository_branch': 'master',
    'use_issues_button': True,
    'use_repository_button': True,
}

# -- Options for EPUB output
epub_show_urls = 'footnote'
