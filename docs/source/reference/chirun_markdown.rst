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

Use the usual markdown syntax to give the image's filename and alt text.

`Attribute Lists <https://python-markdown.github.io/extensions/attr_list/>`_ can be used to customise image style.

.. code-block:: markdown

   ![A plot of y=sin(x)](images/lecture_sine2.png){width="70%"}


***************
Markdown slides
***************

Slides can be written in Markdown and converted to a continuous HTML page, HTML slides and printable PDF by creating a :ref:`Slides <item-type-slides>` item type.

Individual slides should be separated by a line containing three dash characters, ``---``, and surrounded by at least one blank line on each side.

`An example of Markdown slides for Chirun can be found in the sample course <https://www.chirun.org.uk/demo/slides/markdown_slides/markdown_slides.slides.html>`__.

The source document for the above Markdown slides can be found on GitHub at
https://github.com/chirun-ncl/sample_course/blob/master/markdown/lecture.md.

***********************
Embedding other content
***********************

There are a few custom tags which you can use to embed content from external sources.

Numbas
======

A `Numbas <https://www.numbas.org.uk/>`__ exam can be embedded into a document with the ``<numbas-embed>`` tag:

.. code-block:: markdown

   <numbas-embed data-url="https://numbas.mathcentre.ac.uk/exam/1973/numbas-website-demo/embed/" data-id="numbas-demo"></numbas-embed>

The ``<numbas-embed>`` has two attributes:

.. list-table::
    :header-rows: 1

    * - Attribute
      - Description
    * - ``url``
      - The URL to load the Numbas exam from.
        You can use a Numbas exam in your own webspace, or load it directly from the Numbas editor.

        To do that, :guilabel:`Run` the exam in the editor, then click the :guilabel:`Share` button and use the URL it gives you.
    * - ``id``
      - An ID attribute for the resulting element in the page, in case you want to apply CSS styling or refer to it from JavaScript.

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
     - The ID of the YouTube video to load.
       This is the bit of the URL after ``?v=``.

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
     - The ID of the Vimeo video to load.
       This is the string of numbers at the end of the video's URL.

oEmbed
======

Chirun supports embedding content with providers that support `oEmbed <https://oembed.com>`_.

.. code-block:: markdown

   <oembed url="https://www.flickr.com/photos/16782093@N03/6200855102/"></oembed>

.. list-table::
   :header-rows: 1

   * - Attribute
     - Description
   * - ``url``
     - The URL of the oEmbed compatible content to be embedded.


***********
Code blocks
***********

Code blocks with syntax highlighting and output from programs can be included using `SuperFences <https://facelessuser.github.io/pymdown-extensions/extensions/superfences/>`_.

This example shows three different ways to include code blocks.
The first is a code block set to use Python syntax highlighting.
The second code block also displays Python code, but the user can edit it and there is a button that can be clicked to show the output from running the code.
The third shows how to format output from a command-line program.

.. code-block::

    Some static Python code:

    ```python
    print("Hello", "World")
    ```

    Some Python code that can be evaluated:

    ```runnable lang="python"
    x = 2
    if x > 0:
        print('it is true')
    ```

    Output from a program:

    ```output
    usage: git [--version] [--help] [-C <path>] [-c <name>=<value>]
               [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
               [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]
               [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
               [--super-prefix=<path>] [--config-env=<name>=<envvar>]
               <command> [<args>]
    ```
