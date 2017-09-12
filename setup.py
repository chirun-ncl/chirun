#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

misc_files = ['misc/*']

setup(name="makeCourse",
      description="A framework designed to easily convert a set of latex or markdown formatted notes into a course website.",
      version="0.1",
      author="George Stagg",
      author_email="george.stagg@ncl.ac.uk",
      #url="",
      packages = [
         'makeCourse',
      ],
      package_data = {
         'makeCourse': misc_files,
      },
      scripts=['makeCourse/makecourse'],
      install_requires = [
         'appdirs>=1.4.3',
         'arrow>=0.10.0',
         'BeautifulSoup>=3.2.1',
         'beautifulsoup4>=4.6.0',
         'bs4>=0.0.1',
         'funcsigs>=1.0.2',
         'Jinja2>=2.9.6',
         'jinja2-time>=0.2.0',
         'MarkupSafe>=1.0',
         'mock>=2.0.0',
         'olefile>=0.44',
         'packaging>=16.8',
         'pbr>=2.0.0',
         'Pillow>=4.2.1',
         'py>=1.4.33',
         'pyparsing>=2.2.0',
         'pytest>=3.0.7',
         'python-dateutil>=2.6.0',
         'PyYAML>=3.12',
         'six>=1.10.0',
         'plasTeX'
      ],
      dependency_links = [
         'git+git@mas-gitlab.ncl.ac.uk:makecourse-tools/plastex.git@6a33df0f714d3121867fdbded4b99c4a0044e490#egg=plasTeX'
      ]
)
