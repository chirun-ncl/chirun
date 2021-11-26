<img src="https://mas-coursebuild.ncl.ac.uk/lti/images/chirun_icon_512.png" width="100">

Chirun Builder produces flexible and accessible course notes, in a variety of formats, from LaTeX or Markdown source. It is aimed primarily at notes in the mathematical sciences.

This repository, `chirun`, is a python package providing the command line interface for building notes with Chirun Builder.

### How it works
A set of course notes are provided in either Markdown or LaTeX along with a configuration file `config.yml`. The `chirun` command then builds the requested outputs based on the contents of the configuration file.

* Markdown parsing is provided by [Python Markdown](https://github.com/Python-Markdown/markdown).
* LaTeX parsing is provided by [plasTeX](https://github.com/plastex/plastex).

### Demo

[Sample course](https://chirun-ncl.github.io/sample_course/SAM0000/2020/default/), and its [source code](https://github.com/chirun-ncl/sample_course).

### Prerequisites
#### Linux (Ubuntu 18.10+)
 * Ensure a system TeX distribution is installed, such as TeX Live (`apt install texlive-full`).
 * Install `pdf2svg`, `pdftoppm`, `pdftk` and `libyaml` using your standard package manager (`apt install pdf2svg poppler-utils libyaml-dev pdftk-java`).
 * Ensure the `virtualenv` python package is installed (`apt install python3-virtualenv`).
 
#### MacOS
* Install a system TeX distribution, such as MacTeX from https://tug.org/mactex/.
* Install Homebrew by following the instructions at https://brew.sh and once installed use the `brew` command to install `pdf2svg`, `pdftoppm`, `pdftk` and `libyaml`:
  - `brew install poppler`
  - `brew install pdf2svg`
  - `brew install libyaml`
  - `brew install pdftk-java`
* Install `virtualenv` by running `pip3 install virtualenv`.
* If you are not using the default Apple-provided build of Python 3 ( e.g. Python is installed under `/Applications/Python 3.X`, where `3.X` is the version),
  ensure that the SSL CA certificates are installed by running:
    - `sudo /Applications/Python\ 3.X/Install\ Certificates.command`

---

### Quick Installation
 * Create a Python3 virtualenv: `virtualenv -p python3 chirun_env` and activate it: `source ./chirun_env/bin/activate`
 * Install chirun: `pip install git+https://github.com/chirun-ncl/chirun.git`

The command `chirun` is now available for use. You should now compile the sample course and ensure everything works.

#### Upgrade Instructions
 * Run the following command with the virtualenv active to upgrade the installed version of `chirun`:
 * `pip install --upgrade git+https://github.com/chirun-ncl/chirun.git`
 * You may need to run the above command with an extra `--force-reinstall` argument if the version number has not been changed between updates.

---

### Development installation
 * Create a Python3 virtualenv: `virtualenv -p python3 chirun_env` and activate it: `source ./chirun_env/bin/activate`
 * Clone the repository: `git clone https://github.com/chirun-ncl/chirun.git`
 * `cd chirun`
 * Install all the requirements: `pip install -r requirements.txt`
 * Install the chirun tool into your environment: `pip install -e .`

The command `chirun` is now available for use. You should now compile the sample course and ensure everything works.

#### Development Upgrade Instructions
 * To upgrade the development installation pull the latest changes from this git repository and install any new requirements, e.g.
 * `cd chirun`
 * `git pull`
 * `pip install -r requirements.txt`
 
---

### Compile the Sample Course
 * Install the `chirun` package using the instructions above
 * Clone the sample course: `git clone https://github.com/chirun-ncl/sample_course.git`
 * Change into the directory you just cloned to and run `make` to build and view a local version of the sample course.
 * The finished website output will be in `./sample_course/build`

---
 
### Help! My LaTeX notes won't compile!

LaTeX is compiled using the plasTeX python package. While it supports a large array of TeX and LaTeX features, not all packages are compatible. Complex packages must be implemented in python independently.

If your notes are not compiling at all, the first thing to do is to take a look at which LaTeX packages you are using. Try removing one or more, simplifying your notes, until things start working. Complex packages that use PDF special commands are a common problem.

If your notes compile, but the output is broken, you should check indiviual mathematical equations in your notes. Chirun Builder renders mathematics on the web with MathJax, and not all features available in LaTeX work in MathJax out of the box.

In short you should start with short, simple LaTeX documents and slowly build up complexity once they are converting through Chirun Builder cleanly!

### Help! I get the error "AttributeError: module 'yaml' has no attribute 'CLoader'"

Reinstall pyyaml, ensuring that it is linked to the system `libyaml` by issuing the command: `pip --no-cache-dir install --verbose --force-reinstall -I pyyaml`

### Help! Running chirun throws an error related to certificate validation on macOS

Run `sudo /Applications/Python\ 3.X/Install\ Certificates.command` (where `3.X` is your version of Python) to install the appropriate SSL CA certificates. This allows the headless version of Chromium to successfully download.
