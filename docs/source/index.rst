.. title:: Chirun Introduction

.. figure:: /_static/images/chirun_logo.png
   :width: 50%
   :align: center
   :alt: Chirun logo

   (ky-run)

.. note::

   The Chirun project is under active development and so the contents of this documentation
   is subject to change.


Chirun produces flexible and accessible course notes, in a variety of formats, from LaTeX or
Markdown source. It is aimed primarily at notes in the mathematical sciences.

Multiple outputs are supported automatically. So, for example, the same source document can
produce a HTML web page that can be easily viewed on desktop, mobile or tablet; slides that
can be used to give a presentation or lecture; a PDF ready for printing; a Jupyer notebook;
and more.

Chirun can be used to convert either a single input file at a time, or a collection of files
combined as a Chirun "course" package. It generates HTML output, which can be uploaded to a
web server or VLE for distribution to learners.

The `chirun` tool is provided as a Python package, and can be installed on a Linux, macOS or
Windows (via `WSL <https://docs.microsoft.com/en-us/windows/wsl/install>`_) system running
Python. The `chirun` tool provides a command line interface to convert course notes.

Alternatively, a free to use public Chirun builder is available at `https://mas-coursebuild.ncl.ac.uk/public/ <https://mas-coursebuild.ncl.ac.uk/public/>`_,
minimising the need to install software. The public builder produces zipped HTML packages
that will need to be hosted for the web by another service.

An open source Chirun LTI provider is also available. The LTI provider manages an interface
for uploading notes for conversion, distributing the resulting HTML package,
and providing secure access for learners.

The LTI provider is designed to integrate with your
institution's VLE, and so an instance must be setup on an appropriate Linux server and registered
to work with the VLE by your local IT system administrators.

.. toctree::
   :caption: Introduction
   :maxdepth: 2

   self
   demo
   licensing

.. toctree::
   :caption: Information for Authors
   :maxdepth: 2

   getting_started/index
   content_items
   reference/index

.. toctree::
   :caption: Information for Developers
   :maxdepth: 2

   extending/index
   themes

.. toctree::
   :caption: Information for Administrators
   :maxdepth: 2

   installing_chirun_lti
