.. title:: Chirun Introduction

.. figure:: /_static/images/chirun_logo.png
   :width: 50%
   :align: center
   :alt: Chirun logo

   (ky-run)

.. note::

   The Chirun project is under active development and so the contents of this documentation
   are subject to change.

   As of February 2024, the Chirun LTI tool and web builder/editor are usable, but we are still working on writing documentation.

Chirun produces flexible and accessible course notes, in a variety of formats, from LaTeX or Markdown source.
It is aimed primarily at notes in the mathematical sciences.

Multiple outputs are supported automatically.
So, for example, the same source document can produce an HTML web page that can be easily viewed on desktop, mobile or tablet; slides that can be used to give a presentation or lecture; a PDF ready for printing; or a Jupyer notebook.

Chirun can be used to convert either a single input file at a time, or a collection of files combined as a package.
It generates static output which can be uploaded to a web server or learning management system for distribution to learners.

There are two parts to Chirun: the processing tool, and a web frontend.

The web frontend at `lti.chirun.org.uk <https://lti.chirun.org.uk>`__ is the usual point of entry for most authors.

Users with more particular requirements can use the command-line processing tool on its own.

.. toctree::
    :caption: Introduction
    :maxdepth: 1

    demo
    licensing

.. toctree::
    :caption: Information for Authors
    :maxdepth: 2

    getting_started/tutorial
    reference/index
    web/index
    cli/index


.. toctree::
    :caption: Development information

    dev/todo
    dev/support
