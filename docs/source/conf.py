# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'Chirun'
copyright = 'Digital Learning Unit, Newcastle University'
author = 'Digital Learning Unit, Newcastle University'

release = '0.8.0'
version = '0.8.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

#html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'logo': 'images/chirun_logo.png',
    'github_button': True,
    'github_user': 'chirun-ncl',
    'github_repo': 'chirun',
    'show_powered_by': False,
}

# -- Options for EPUB output
epub_show_urls = 'footnote'
