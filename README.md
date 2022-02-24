<img src="https://mas-coursebuild.ncl.ac.uk/lti/images/chirun_logo_512.png" height="100">

Chirun produces flexible and accessible course notes, in a variety of formats, from LaTeX or Markdown source. It is aimed primarily at notes in the mathematical sciences.

This repository, `chirun`, is the source code of the Chirun Python package, providing the command line interface for building content.


## Documentation

The Chirun documentation, including information about the [Chirun Public Content Builder](https://mas-coursebuild.ncl.ac.uk/public/) and
[Chirun LTI Provider](https://github.com/chirun-ncl/chirun-lti/) can be found at,

https://chirun.readthedocs.io/en/latest/


### How it works
A set of course notes are provided in either Markdown or LaTeX along with a configuration file `config.yml`. The `chirun` command then builds the requested outputs based on the contents of the configuration file.

* Markdown parsing is provided by [Python Markdown](https://github.com/Python-Markdown/markdown).
* LaTeX parsing is provided by [plasTeX](https://github.com/plastex/plastex).

---

### Installation

Installation instructions for Linux and macOS can be found [in the Chirun documentation](https://chirun.readthedocs.io/en/latest/getting_started/cli/install.html#installation-instructions).

Windows can be used via [WSL](https://docs.microsoft.com/en-us/windows/wsl/install) and following the Linux installation instructions.

#### Upgrading from `makecourse`
The project has recently been renamed from "makecourse" to "chirun". To upgrade, first remove the older `makecourse` package with,

```
pip uninstall makecourse
```

Then follow the installation or upgrade instructions above.
 
---

### Demo

[Sample course](https://chirun-ncl.github.io/sample_course/), and its [source code](https://github.com/chirun-ncl/sample_course).

### Compile the Sample Course
 * Install the `chirun` package using the instructions above
 * Clone the sample course: `git clone https://github.com/chirun-ncl/sample_course.git`
 * Change into the directory you just cloned to and run `make` to build and view a local version of the sample course.
 * The finished website output will be in `./sample_course/build`

---
