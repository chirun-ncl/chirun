## Introduction
The main makecourse tool lives in this repository. The idea will hopefully be to clone this repo, set up a virtualenv based on the requirements, and finally have a script that takes a directory as input and produces a nice website as output (perhaps in /path/to/input/build/).

## Installation
Clone the repo: git clone ...
(Optional)Create a Python2 virtualenv: virtualenv -p /usr/bin/python2.7 .makecourse_env
Install the requirements: pip2 install -r requirements.txt

## Define a course
Not 100% on how this will work yet. Perhaps a file called course.yml that has a list of git repos for each section. Each course should be able to define it's own themes too. Platex supports loading themes from cwd so this should be okay.
