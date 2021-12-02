Convert a Standalone Document
=============================

Chirun can be used to convert a single document in LaTeX or Markdown format as a `standalone` item.
The conversion process has two steps,

    1. Create a Chirun configuration file
    2. Compile the document using the Chirun CLI tool

Create the ``config.yml`` file
------------------------------

Take the following template and save it as ``config.yml`` in the same directory as your document source.

.. code-block:: yaml

    author: 'Ann Example'
    structure: 
      - type: standalone
        topbar: False
        source: source_file.tex
        title: 'Example Document'
    build_pdf: true

.. note::

    Don't forget to replace the author's name, document title, and the source filename for the document, ``source_file.tex``.

Run the Chirun CLI tool
------------------------

Once your ``config.yml`` file has been created, run Chirun to convert your document into accessible HTML format::

    chirun

Once the job is complete, the HTML output can be found in the ``build`` directory. Open the file ``build/index.html`` to view the results.

.. warning::

    If you see the error message ``FileNotFoundError: [Errno 2] No such file or directory``
    ensure that the file ``source_file.tex`` exists, or the source property in ``config.yml`` is updated to
    match your document's source filename.

Distribution
------------

The contents of the ``build`` directory can be uploaded to a web space or your VLE to distribute to learners.
