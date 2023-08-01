.. _chirun-markdown-extensions:

##########################
Chirun Markdown Extensions
##########################

The flavour of Markdown used in Chirun is `Python Markdown <https://python-markdown.github.io>`_ with `PyMdown Extensions <https://facelessuser.github.io/pymdown-extensions/>`_ and some further Chirun Extensions.

Chirun-specific extensions are described below.


****************
Including images
****************

Include images by using the filename path relative to the source document.
Chirun will detect images included in this way and will copy them to the output directory automatically.
`Attribute Lists <https://python-markdown.github.io/extensions/attr_list/>`_ can be used to customise image style.

.. code-block:: markdown

   ![A plot of y=sin(x)](images/lecture_sine2.png){width="70%"}


***************
Markdown slides
***************

Slides can be written in Markdown and converted to a continuous HTML page, HTML slides and printable PDF by creating a :ref:`Slides <item-type-slides>` item type.

Individual slides should be separated by a line containing three dash characters, ``---``, and surrounded by at least one blank line on each side.

`An example of Markdown slides for Chirun can be found in the sample course <https://chirun-ncl.github.io/sample_course/markdown_slides/>`__.

The source document for the above Markdown slides can be found on GitHub at
https://raw.githubusercontent.com/chirun-ncl/sample_course/master/markdown/lecture.md

***********************
Embedding other content
***********************

.. todo::
    Is this up to date?


Numbas
======

A Numbas exam can be embedded into a document with the ``<embed-numbas>`` tag:

.. code-block:: markdown

   <embed-numbas data-url="https://numbas.mathcentre.ac.uk/exam/1973/numbas-website-demo/embed/"></embed-numbas>

YouTube
=======

A YouTube video be embedded into a document with the ``<youtube-embed>`` tag:

.. code-block:: markdown

   <youtube-embed data-id="EdyociU35u8"></youtube-embed>

.. list-table::
   :header-rows: 1

   * - Attribute
     - Description
   * - ``data-id``
     - The YouTube video ID

Vimeo
=====

A Vimeo video be embedded into a document with,

.. code-block:: markdown

   <vimeo-embed data-id="8169375"></vimeo-embed>

.. list-table::
   :header-rows: 1

   * - Attribute
     - Description
   * - ``data-id``
     - The Vimeo video ID

oEmbed
======

Chirun supports embedding content with providers that support `oEmbed <https://oembed.com>`_.

.. code-block:: markdown

   <oembed data-url="[...]"></oembed>

.. list-table::
   :header-rows: 1

   * - Attribute
     - Description
   * - ``data-url``
     - The URL of the oEmbed compatible content to be embedded


***********
Code blocks
***********

Code blocks with syntax highlighting can be included using `SuperFences <https://facelessuser.github.io/pymdown-extensions/extensions/superfences/>`_.

This example shows two different ways to include code blocks.
The first is a code block set to use Python syntax highlighting.
The second code block also displays Python code, but also includes a button that can be clicked to show the output from running the code.

.. todo::
    Is this up to date?

.. code-block::

    ### Print statements

    ```python
    print("Hello", "World")
    ```

    ### If statements

    ```runnable lang="python"
    x = 2
    if x > 0:
        print('it is true')
    ```

