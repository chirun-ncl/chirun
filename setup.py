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
)
