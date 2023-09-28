#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(name="chirun",
      description="Produce flexible and accessible course notes, in a variety of formats, using LaTeX or Markdown source",
      version="1.0.0",
      author="Digital Learning Team, School of Mathematics, Statistics & Physics, Newcastle University",
      author_email="msp.digital.learning@ncl.ac.uk",
      url="https://chirun.org.uk",
      packages=find_packages(),
      include_package_data=True,
      scripts=['chirun/makecourse', 'chirun/chirun'],
      install_requires = [
          'appdirs==1.4.4',
          'arrow==1.2.2',
          'beautifulsoup4==4.11.1',
          'funcsigs==1.0.2',
          'Jinja2==2.11.3',
          'jinja2-time==0.2.0',
          'Markdown==3.1.1',
          'markdown-figure==0.0.1',
          'MarkupSafe==1.1.1',
          'mock==4.0.3',
          'notedown==1.5.1',
          'olefile==0.46',
          'packaging==21.3',
          'pbr==5.9.0',
          'Pillow==9.2.0',
          'plasTeX==2.1',
          'py==1.11.0',
          'Pygments==2.11.0',
          'pymdown-extensions==6.0',
          'pyoembed==0.1.2',
          'pyparsing==3.0.9',
          'PyPDF2==2.5.0',
          'pyppeteer==1.0.2',
          'pytest==7.1.2',
          'python-dateutil==2.8.2',
          'PyYAML==6.0',
          'six==1.16.0',
          'typing_extensions==4.3.0',
          'Unidecode==1.3.4',
          'Babel==2.12.1',
      ]
)
