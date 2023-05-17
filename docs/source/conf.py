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
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

def setup(app):
    app.add_css_file('chirun-style.css')

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_book_theme'

html_static_path = ['_static']

html_theme_options = {
    'use_fullscreen_button': False,
    'use_issues_button': False,
    'repository_url': 'https://github.com/numbas/editor',
    'repository_branch': 'master',
    'use_repository_button': True,
    'use_edit_page_button': True,
    'path_to_docs': 'docs/source/',
}


# -- Options for EPUB output
epub_show_urls = 'footnote'
