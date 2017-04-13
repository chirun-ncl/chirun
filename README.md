## Introduction
The main makecourse tool lives in this repository. The idea will hopefully be to clone this repo, set up a virtualenv based on the requirements, and finally have a script that takes a directory as input and produces a nice website as output.

## Installation
 * Clone the repo and all the submodules: git clone --recursive git@mas-gitlab.ncl.ac.uk:makecourse-tools/makecourse.git
 * (Optional) Create a Python2 virtualenv: virtualenv -p /usr/bin/python2.7 .makecourse_env
 * Install the requirements: pip2 install -r requirements.txt
 * (Optional) Install PIL: pip install --no-index -f http://effbot.org/downloads/ -U PIL --trusted-host effbot.org

## Compile the MAS0001 test course
 * cd to the makecourse directory
 * run: HTML5TEMPLATES="$(pwd)/mas0001/" plastex --dir=mas0001/build/ --renderer=HTML5ncl --dollars --theme mas0001 mas0001/mas0001.tex
 * The output html lives in ./mas0001/build

## Define a course
Not 100% on how this will work yet. Platex supports loading custom themes so I have put a custom theme in the mas0001/Themes directory. I made a file .makecourse-config.yml that will hopefully control everything - but for now does nothing. When it works, the platex command (or pandoc command for markdown) will be build automatically so all you'd have to do is: make mas0001
