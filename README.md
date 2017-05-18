## Introduction
The main makeCourse tool lives in this repository.

## Quick Installation
 * (Optional) Create a Python2 virtualenv: `virtualenv -p /usr/bin/python2.7 makecourse_env` and activate it: `source ./makecourse_env/bin/activate`
 * Install PIL: `pip2 install --no-index -f http://effbot.org/downloads/ -U PIL --trusted-host effbot.org`
 * Install makeCourse: `pip2 install git+https://mas-gitlab.ncl.ac.uk/makecourse-tools/makecourse.git` 

## Install from source 
 * (Optional) Create a Python2 virtualenv: `virtualenv -p /usr/bin/python2.7 makecourse_env` and activate it: `source ./makecourse_env/bin/activate`
 * Clone the repo: `git clone git@mas-gitlab.ncl.ac.uk:makecourse-tools/makecourse.git`
 * Dive inside: `cd makecourse`
 * Install PIL: `pip2 install --no-index -f http://effbot.org/downloads/ -U PIL --trusted-host effbot.org`
 * Install all the other requirements: `pip2 install -r requirements.txt`
 * Install the makeCourse tool: `pip2 install -e .`

## Compile the MAS0001 test course
 * cd somewhere reasonable and get the MAS0001 test course: `git clone --recursive git@mas-gitlab.ncl.ac.uk:makecourse-tools/mas0001/mas0001.git`
 * Run makeCourse: `makecourse -v mas0001`. Here `-v` is used for verbose output.
 * The output html lives in `./mas0001/build`
