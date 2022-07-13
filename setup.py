#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(name="chirun",
      description="Produce flexible and accessible course notes, in a variety of formats, using LaTeX or Markdown source",
      version="0.7.1",
      author="E-Learning Team, School of Mathematics, Statistics & Physics, Newcastle University",
      author_email="christopher.graham@ncl.ac.uk",
      url="https://mas-coursebuild.ncl.ac.uk",
      packages=find_packages(),
      include_package_data=True,
      scripts=['chirun/makecourse', 'chirun/chirun'],
      install_requires = [
          'appdirs==1.4.4',
          'beautifulsoup4==4.11.1',
          'Jinja2==3.1.2',
          'Markdown==3.3.7',
          'markdown-figure==0.0.1',
          'notedown==1.5.1',
          'Pillow==9.2.0',
          'plasTeX==2.1',
          'Pygments==2.12.0',
          'pymdown-extensions==9.5',
          'pyoembed==0.1.2',
          'PyPDF2==2.5.0',
          'pyppeteer==1.0.2',
          'PyYAML==6.0',
          'typing_extensions==4.3.0',
          'Unidecode==1.3.4',
      ]
)
