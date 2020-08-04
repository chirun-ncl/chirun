<img src="https://mas-coursebuild.ncl.ac.uk/lti/images/coursebuilder_icon_512.png" width="100">

Coursebuilder produces flexible and accessible course notes, in a variety of formats, from LaTeX or Markdown source. It is aimed primarily at notes in the mathematical sciences.

This repository, `makecourse`, is a python package providing the command line interface for building notes with CourseBuilder.

### How it works
A set of course notes are provided in either Markdown or LaTeX along with a configuration file `config.yml`. The `makecourse` command then builds the requested outputs based on the contents of the configuration file.

* Markdown parsing is provided by [Python Markdown](https://github.com/Python-Markdown/markdown).
* LaTeX parsing is provided by [plasTeX](https://github.com/plastex/plastex).

### Demo

[Sample course](https://coursebuilder-ncl.github.io/sample_course/SAM0000/2020/default/), and its [source code](https://github.com/coursebuilder-ncl/sample_course).

### Prerequisites
#### Linux (Ubuntu 16.04+)
 * Ensure a system TeX distribution is installed, such as TeX Live (`apt install texlive-full`).
 * Install `pdf2svg`, `pdftoppm` and `libyaml` using your standard package manager (`apt install pdf2svg poppler-utils libyaml-dev`).
 * Ensure the `virtualenv` python package is installed (`apt install python3-virtualenv`).
 
#### MacOS
* Install a system TeX distribution, such as MacTeX from https://tug.org/mactex/.
* Install Homebrew by following the instructions at https://brew.sh and once installed use the `brew` command to install `pdf2svg`, `pdftoppm` and `libyaml`:
  - `brew install poppler`
  - `brew install pdf2svg`
  - `brew install libyaml`
* Install `virtualenv` by running `pip3 install virtualenv`.

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
 * Change into the directory you just cloned to and run `make local` to build and view a local version of the sample course.
 * The finished website output will be in `./sample_course/build`
 
### Help! My LaTeX notes won't compile!

LaTeX is compiled using the plasTeX python package. While it supports a large array of TeX and LaTeX features, not all packages are compatible. Complex packages must be implemented in python independently.

If your notes are not compiling at all, the first thing to do is to take a look at which LaTeX packages you are using. Try removing one or more, simplifying your notes, until things start working. Complex packages that use PDF special commands are a common problem.

If your notes compile, but the output is broken, you should check indiviual mathematical equations in your notes. Coursebuilder renders mathematics on the web with MathJax, and not all features available in LaTeX work in MathJax out of the box.

In short you should start with short, simple LaTeX documents and slowly build up complexity once they are converting through CourseBuilder cleanly!

### Help! I get the error "AttributeError: module 'yaml' has no attribute 'CLoader'"

Reinstall pyyaml, ensuring that it is linked to the system `libyaml` by issuing the command: `pip --no-cache-dir install --verbose --force-reinstall -I pyyaml`
