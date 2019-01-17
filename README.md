## Introduction
The main makeCourse tool lives in this repository.

## Quick Installation
 * Install pdf2svg and pandoc using your standard package manager (e.g. `apt install pdf2svg pandoc`)
 * (Optional) Create a Python3 virtualenv: `virtualenv -p python3 makecourse_env` and activate it: `source ./makecourse_env/bin/activate`
 * Install makeCourse: `pip install git+https://mas-gitlab.ncl.ac.uk/makecourse-tools/makecourse.git` 

The command `makecourse` is now available.

## Development installation
 * Install pdf2svg and pandoc using your standard package manager (e.g. `apt install pdf2svg pandoc`)
 * Create a Python3 virtualenv: `virtualenv -p python3 makecourse_env` and activate it: `source ./makecourse_env/bin/activate`
 * Clone the repository: `git clone git@mas-gitlab.ncl.ac.uk:makecourse-tools/makecourse.git`
 * Dive inside: `cd makecourse`
 * Install all the requirements: `pip install -r requirements.txt`
 * Install the makeCourse tool into your environment: `pip install -e .`

The command `makecourse` is now available.

## Compile the MAS0001 test course
 * Install makeCourse using the instructions above
 * Clone the source/configuration of the MAS0001 test course: `git clone git@mas-gitlab.ncl.ac.uk:makeCourse-tools/MAS0001.git`
 * Run makeCourse on the directory you just cloned to: `makecourse -v MAS0001`. Here `-v` is used for verbose output
 * The output website will then be in `./MAS0001/build`
