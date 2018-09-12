## Introduction
The main makeCourse tool lives in this repository.

## Quick Installation
 * (Optional) Create a Python2 virtualenv: `virtualenv -p /usr/bin/python2.7 makecourse_env` and activate it: `source ./makecourse_env/bin/activate`
 * Install PIL: `pip2 install --no-index -f http://effbot.org/downloads/ -U PIL --trusted-host effbot.org`
 * Install makeCourse: `pip2 install git+https://mas-gitlab.ncl.ac.uk/makecourse-tools/makecourse.git` 
 * Install pdf2svg and pandoc using your standard package manager

## Install from source 
 * (Optional) Create a Python2 virtualenv: `virtualenv -p /usr/bin/python2.7 makecourse_env` and activate it: `source ./makecourse_env/bin/activate`
 * Clone the repo: `git clone git@mas-gitlab.ncl.ac.uk:makecourse-tools/makecourse.git`
 * Dive inside: `cd makecourse`
 * Install PIL: `pip2 install --no-index -f http://effbot.org/downloads/ -U PIL --trusted-host effbot.org`
 * Install all the other requirements: `pip2 install -r requirements.txt`
 * Install the makeCourse tool: `pip2 install -e .`
 * Install pdf2svg and pandoc using your standard package manager

## Compile the MAS0001 test course
 * Install makeCourse using the instructions above
 * Clone the source/configuration of one of the MAS modules from the `https://mas-gitlab.ncl.ac.uk/makecourse-tools/` group, e.g `MAS0001`
 * Run makeCourse on the directory you just cloned to: `makecourse -v MAS0001`. Here `-v` is used for verbose output
 * The output website will then be in `./MAS0001/build`
