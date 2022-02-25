Content Item Types
==================

The Chirun configuration file ``config.yml`` contains an list of items to be compiled. The top
level array property ``structure`` holds the information, and each item in the list has an associated
``type`` (and other properties), described below.

With the major exceptions of the ``title``, ``source`` and ``content`` properties, most item properties
are optional and so can be omitted in ``config.yml``.

....

Chapter
----------

A ``chapter`` item should be used when including a short simple document, or when including a single chapter
of a longer document. The entire document is output as single web page as part of the Chirun output.

Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``title``
     - The content item's title.
     - None
   * - ``source``
     - The file name of the source for the item.
     - None
   * - ``sidebar``
     - Show the theme's sidebar including ToC?
     - ``True``
   * - ``topbar``
     - Show the theme's topbar at the top of the page?
     - ``True``
   * - ``footer``
     - Show the theme's footer at the bottom of the page?
     - ``True``
   * - ``buildPDF``
     - Build a PDF for this item?
     - ``True``
   * - ``js``
     - An array of paths to JS files to include in HTML output
     - ``[]``
   * - ``css``
     - An array of paths to CSS files to include in HTML output
     - ``[]``


Supported Source Formats
~~~~~~~~~~~~~~~~~~~~~~~~
 * LaTeX with :ref:`Chirun LaTeX Package`
 * Markdown with :ref:`Chirun Markdown Extensions`

Outputs
~~~~~~~
 * HTML web page
 * PDF document

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: chapter
        title: Some LaTeX notes
        source: latex_notes.tex
        sidebar: False

....

Part
----

A ``part`` item allows you to group items into a collection. The items contained in the part are built as normal, but
are grouped together in the output hierarchy. Chirun will render a part item as a list of links to the containing items,
labelled by the linked item titles. Part items can be nested.

An example use of the part type could be to combine several ``chapter`` items into an organised collection. Another use
could be to organise several items of content into weekly blocks.


Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``title``
     - The title for the part collection.
     - None
   * - ``content``
     - An array of items to be built as part of this collection.
     - None

Outputs
~~~~~~~
 * HTML web page

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: part
        title: Some Notes
        content:
          - type: chapter
            title: LaTeX Chapter 1
            source: latex_notes_1.tex
          - type: chapter
            title: LaTeX Chapter 2
            source: latex_notes_2.tex

....

Document
--------

A `document` item is similar to a :ref:`Chapter` item, but intended for longer documents or books.

A document item allows for content to be split at the chapter or section level, building up a hierarchy of part
items and chapter subitems automatically. Both the HTML and PDF outputs are split as part of this process.

.. note::
   
   Currently, the document item type only works with LaTeX source documents. For longer Markdown documents, split up your
   content into multiple files and build the structure manually using part and chapter item types.

Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``title``
     - The content item's title.
     - None
   * - ``source``
     - The file name of the source for the item.
     - None
   * - ``splitlevel``
     - At what :ref:`level <Split Levels>` should the document be split?
     - ``0``
   * - ``sidebar``
     - Show the theme's sidebar including ToC?
     - ``True``
   * - ``topbar``
     - Show the theme's topbar at the top of the page?
     - ``True``
   * - ``footer``
     - Show the theme's footer at the bottom of the page?
     - ``True``
   * - ``buildPDF``
     - Build a PDF for this item?
     - ``True``
   * - ``js``
     - An array of paths to JS files to include in HTML output
     - ``[]``
   * - ``css``
     - An array of paths to CSS files to include in HTML output
     - ``[]``

Split Levels
~~~~~~~~~~~~~

.. list-table:: 
   :header-rows: 1

   * - Description
     - Split level
   * - Entire Document (no splitting)
     - -2
   * - Part
     - -1
   * - Chapter
     - 0
   * - Section
     - 1
   * - Subsection
     - 2



Supported Source Formats
~~~~~~~~~~~~~~~~~~~~~~~~
 * LaTeX with :ref:`Chirun LaTeX Package`

Outputs
~~~~~~~
 * HTML web page
 * PDF document

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: document
        title: Some LaTeX Book
        source: latex_book.tex
        splitlevel: 0

....

Standalone
----------

A ``standalone`` item type is the same as a :ref:`Chapter` item type, but intended for when there is only a single piece of content being
built.

Content built with the standalone item type becomes the index page for the course, and no introduction page is generated.

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: standalone
        title: Some LaTeX Notes
        source: latex_notes.tex

....

Introduction
------------

An ``introduction`` item produces the index page for the course. The index page shows some basic information about the course, such as the
author, course title, year and code (if populated) course properties set in the ``config.yml`` file. In addition, the other content items
described in the ``structure`` property are linked to from this introduction page.

A source document can be optionally associated with the introduction item to display content as part of the introduction page. Alternatively,
text content can be set as properties on the introduction item directly.

If no introduction or standalone item is included in the course structure, a basic introduction item is automatically generated.

Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``source``
     - The source file name for optional content.
     - None
   * - ``location``
     - Display the ``source`` content above or below the content links?
     - ``below``
   * - ``leading_text``
     - Optional text shown under the title and author.
     - None


Supported Source Formats
~~~~~~~~~~~~~~~~~~~~~~~~
 * LaTeX with :ref:`Chirun LaTeX Package`
 * Markdown with :ref:`Chirun Markdown Extensions`

Outputs
~~~~~~~
 * HTML web page

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: introduction 
        leading_text: "This is a short paragraph that will be 
        inserted into the introduction page, just under the author and year."
      - type: chapter
        title: Some LaTeX notes
        source: latex_notes.tex

....

Slides
------

The ``slides`` item type is intended to be used for content primarily presented as a presentation and/or set of slides.
A slides item is built as a :ref:`Chapter`-style HTML web page, a slides pack for presenation, and a printable PDF output.

The precise output format for a slides item depends on the source format.

Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``title``
     - The content item's title.
     - None
   * - ``source``
     - The file name of the source for the item.
     - None
   * - ``js``
     - An array of paths to JS files to include in HTML output
     - ``[]``
   * - ``css``
     - An array of paths to CSS files to include in HTML output
     - ``[]``

Supported Source Formats
~~~~~~~~~~~~~~~~~~~~~~~~~

LaTeX with the Beamer Package
*****************************

LaTeX documents can be converted as a slides item type when using the LaTeX package Beamer.
Two output formats are produced,

 * A HTML web page, in the style of a :ref:`Chapter` item.
 * The PDF output, as produced by LaTeX, containing the slides that can be presented with a PDF viewer or printed.

An example of Beamer slides output can be found `here in the sample course <https://chirun-ncl.github.io/sample_course/slides/beamer_slides/>`_.
The PDF output is provided as a link in the sidebar  of the HTML webpage.

Markdown with Chirun Markdown Extensions
***********************************************

Slides written in Markdown using the :ref:`Chirun Markdown Extensions` produces three output formats,

 * A HTML web page, in the style of a :ref:`Chapter` item.
 * Web-based slides, using the `Reveal.js <https://revealjs.com>`_ presentation framework.
 * A printable PDF download showing the slides.

An example of Markdown slides can be found `here in the sample course <https://chirun-ncl.github.io/sample_course/markdown_slides/>`_.
Both the Reveal.js and PDF download are provided as links in the sidebar of the HTML page.


.. note::
    
   The source document for the above Markdown slides can be found on GitHub at
   https://raw.githubusercontent.com/chirun-ncl/sample_course/master/markdown/lecture.md

Slides items currently have the same properties as :ref:`Chapter` items.

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: slides
        title: Beamer Slides
        source: lecture1.tex
      - type: slides
        title: Markdown Slides
        source: lecture2.md

....

Notebook
--------

A `notebook` item is similar to a :ref:`Chapter` item, but intended for documents with many code blocks and authored
in a style that would fit well as a `Jupyer notebook <https://jupyter.org>`_.

The content is built in the style of a :ref:`Chapter` item, but with an additional download link provided to a Jupyter
notebook version of the same content. Code blocks become runnable cells in the notebook, while other content becomes
information-only cells.

.. note::
   
   Currently, the notebook item type only works with Markdown source documents.

Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``title``
     - The content item's title.
     - None
   * - ``source``
     - The file name of the source for the item.
     - None
   * - ``sidebar``
     - Show the theme's sidebar including ToC?
     - ``True``
   * - ``topbar``
     - Show the theme's topbar at the top of the page?
     - ``True``
   * - ``footer``
     - Show the theme's footer at the bottom of the page?
     - ``True``
   * - ``buildPDF``
     - Build a PDF for this item?
     - ``True``
   * - ``js``
     - An array of paths to JS files to include in HTML output
     - ``[]``
   * - ``css``
     - An array of paths to CSS files to include in HTML output
     - ``[]``


Supported Source Formats
~~~~~~~~~~~~~~~~~~~~~~~~
 * Markdown with :ref:`Chirun Markdown Extensions`

Outputs
~~~~~~~
 * HTML web page
 * Jupyter notebook

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: notebook
        title: Programming Handout
        source: handout.md

An example of the output from a notebook item can be found `here in the sample course <https://chirun-ncl.github.io/sample_course/other_content/jupyter_notebook_not/>`_.
Both the Jupyter notebook and PDF download are provided as links in the sidebar of the HTML page.


.. note::
    
   The source document for the above Markdown slides can be found on GitHub at
   https://raw.githubusercontent.com/chirun-ncl/sample_course/master/markdown/handout.md

....

URL
---

A ``url`` item type is used to link to external URLs or static documents. For example, data file could be distributed
verbatim by using the URL item type. URL item types are added to the introduction or part pages, but do not cause
any extra content pages to be built; the item is linked to directly.

External links must begin ``http://``, ``https://`` or ``ftp://``.

Internal static files should be placed in a directory ``static`` in the same directory as the ``config.yml`` file. The contents
of this directory will be automatically copied into the output directory by Chirun. Files in ``static`` can then be
referenced relatively for URL items.

Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``title``
     - The content item's title.
     - None
   * - ``source``
     - The URL to be linked to.
     - None

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: url
        title: The BBC website
        source: https://bbc.co.uk
      - type: url
        title: Some static content
        source: static/data/dataset.RData

....

HTML
----

A `html` item is similar to a :ref:`Chapter` item, but intended for including raw HTML as part of the Chirun output
in style consistent with the rest of the output pages.

Rendering is performed in the same way as for a chapter item, but rather than converting the document from its original
source. The raw html file provided as the ``source`` file is inserted into the produced HTML web page in the place where
processed document content would normally be placed.

.. note::
   
   A HTML item is not reproduced verbatim as part of the output, but is processed to form a page in the style of a
   a ``chapter`` item. To include a ``.html`` file verbatim with no modifications, create an internal static
   :ref:`URL` item instead. 

Item Properties
~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Property
     - Description
     - Default Value 
   * - ``title``
     - The content item's title.
     - None
   * - ``source``
     - The file name of the source for the item.
     - None
   * - ``sidebar``
     - Show the theme's sidebar including ToC?
     - ``True``
   * - ``topbar``
     - Show the theme's topbar at the top of the page?
     - ``True``
   * - ``footer``
     - Show the theme's footer at the bottom of the page?
     - ``True``
   * - ``js``
     - An array of paths to JS files to include in HTML output
     - ``[]``
   * - ``css``
     - An array of paths to CSS files to include in HTML output
     - ``[]``

Supported Source Formats
~~~~~~~~~~~~~~~~~~~~~~~~
 * HTML

Outputs
~~~~~~~
 * HTML web page

Example
~~~~~~~

.. code-block:: yaml

    structure:
      - type: html
        title: Include raw HTML
        source: files/raw/document.html
