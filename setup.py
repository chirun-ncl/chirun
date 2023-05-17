#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(name="chirun",
      description="Produce flexible and accessible course notes, in a variety of formats, using LaTeX or Markdown source",
      version="0.8.0",
      author="Digital Learning Unit, School of Mathematics, Statistics & Physics, Newcastle University",
      author_email="msp.digital.learning@ncl.ac.uk",
      url="https://chirun.org.uk",
      packages=find_packages(),
      include_package_data=True,
      scripts=['chirun/makecourse', 'chirun/chirun'],
      install_requires = [
          'Babel==2.12.1',
          'beautifulsoup4==4.11.1',
          'Jinja2==3.1.2',
          'Markdown==3.4.3',
          'markdown-figure==0.0.1',
          'notedown==1.5.1',
          'Pillow==9.5.0',
          'plasTeX==2.1',
          'Pygments==2.15.1',
          'pymdown-extensions==10.0.1',
          'pyoembed==0.1.2',
          'PyPDF2==3.0.1',
          'pyppeteer==1.0.2',
          'PyYAML==6.0',
      ]
)
