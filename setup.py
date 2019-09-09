#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(name="makeCourse",
      description="A framework designed to easily convert a set of latex or markdown formatted notes into a course website.",
      version="0.2",
      author="George Stagg",
      author_email="george.stagg@ncl.ac.uk",
      url="https://mas-coursebuild.ncl.ac.uk",
      packages=find_packages(),
      include_package_data=True,
      scripts=['makeCourse/makecourse'],
      install_requires = [
         'appdirs>=1.4.3',
         'arrow>=0.10.0',
         'beautifulsoup4>=4.8.0',
         'bs4>=0.0.1',
         'funcsigs>=1.0.2',
         'Jinja2>=2.9.6',
         'jinja2-time>=0.2.0',
         'Markdown>=3.1.1',
         'MarkupSafe>=1.0',
         'markdown-figure>=0.0.1',
         'mdx-outline>=1.3.0',
         'mock>=2.0.0',
         'olefile>=0.44',
         'packaging>=16.8',
         'pbr>=2.0.0',
         'Pillow>=4.2.1',
         'py>=1.4.33',
         'Pygments>=2.4.2',
         'pymdown-extensions<=6.0',
         'pyoembed>=0.1.2',
         'pyparsing>=2.2.0',
         'pyppeteer>=0.0.25',
         'pytest>=3.0.7',
         'python-dateutil>=2.6.0',
         'PyYAML>=3.12',
         'six>=1.10.0',
         'plasTeX',
         'Unidecode>=1.0.22'
      ],
      dependency_links = [
         'git+ssh://git@mas-gitlab.ncl.ac.uk/makecourse-tools/plastex.git#egg=plasTeX'
      ]
)
