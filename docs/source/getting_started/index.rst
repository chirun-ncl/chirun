Getting Started
===============

Chirun converts documents from a LaTeX or Markdown source into an accessible HTML format.

Multiple outputs for the same content can be automatically built. So, for example,
a single source document can produce a HTML web page that can be easily viewed on desktop, mobile or tablet; slides that
can be used to give a presentation or lecture; a PDF ready for printing; a Jupyer notebook;
and more.

Chirun can be used to convert either a single input file at a time, or a collection of files combined as a Chirun "course package".

**Running Chirun**

There are multiple ways to use Chirun. Usually, you will only need to choose one of the three methods described below.
In each case, the output is a directory containing HTML, which can be uploaded to a web server or provided via
a VLE for distribution to learners.

* If your institution has already setup an instance of the :ref:`chirun_lti`, we recommend making use of that method, as it integrates
  directly with your institution's VLE.

* Those unfamiliar with the system or just wanting to convert a few independent documents should use the :ref:`Chirun Public Content Builder`.

* More advanced users or those wanting to author many documents in Chirun should choose to use the :ref:`Chirun Python package`.

.. toctree::
   :maxdepth: 2

   public
   cli/index.rst
   lti/index.rst
   troubleshooting
