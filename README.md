<img src="https://mas-coursebuild.ncl.ac.uk/lti/images/coursebuilder_icon_512.png" width="100">

Coursebuilder produces flexible and accessible course notes, in a variety of formats, from LaTeX or Markdown source. It is aimed primarily at notes in the mathematical sciences.

This repository, `makecourse`, is a python package providing the command line interface for building notes with CourseBuilder.

### How it works
A set of course notes are provided in either Markdown or LaTeX along with a configuration file `config.yml`. The `makecourse` command then builds the requested outputs based on the contents of the configuration file.

* Markdown parsing is provided by [Python Markdown](https://github.com/Python-Markdown/markdown).
* LaTeX parsing is provided by [plasTeX](https://github.com/plastex/plastex).

### Prerequisites
 * Ensure a system TeX distribution such as TeX Live or MacTeX is installed.
 * Install pdf2svg using your standard package manager (e.g. `apt install pdf2svg`)
 * Install libyaml using your standard package manager (e.g. `apt install libyaml-dev`)
 * Ensure the `virtualenv` python package is installed.

### Quick Installation
 * Create a Python3 virtualenv: `virtualenv -p python3 coursebuilder_env` and activate it: `source ./coursebuilder_env/bin/activate`
 * Install makeCourse: `pip install git+https://github.com/coursebuilder-ncl/makecourse.git`

The command `makecourse` is now available for use. You should now compile the sample course and ensure everything works.

### Development installation
 * Create a Python3 virtualenv: `virtualenv -p python3 coursebuilder_env` and activate it: `source ./coursebuilder_env/bin/activate`
 * Clone the repository: `git clone https://github.com/coursebuilder-ncl/makecourse.git`
 * `cd makecourse`
 * Install all the requirements: `pip install -r requirements.txt`
 * Install the makecourse tool into your environment: `pip install -e .`

The command `makecourse` is now available for use. You should now compile the sample course and ensure everything works.

### Compile the Sample Course
 * Install the `makecourse` package using the instructions above
 * Clone the sample course: `git clone https://github.com/coursebuilder-ncl/sample_course.git`
 * Change into the directory you just cloned to and run "make local" to build and view a local version of the sample course.
 * The finished website output will be in `./sample_course/build`
