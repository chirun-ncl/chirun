Chirun Markdown Extensions
==========================

The flavour of Markdown used in Chirun is `Python Markdown <https://python-markdown.github.io>`_
with `PyMdown Extensions <https://facelessuser.github.io/pymdown-extensions/>`_ and some
further Chirun Extensions.

Chirun specific extensions are described below.


Sectioning
----------

Documents are automatically wrapped into logical sections based on headings. This allows styles
to be applied to blocks of content by using `Attribute Lists <https://python-markdown.github.io/extensions/attr_list/>`_.
A logical section is automatically ended by a new heading of equal or lower level.

.. code-block:: markdown

    # H1 level section
    Here is some text.

    ## H2 level section {: #someid .someclass style='background-color:#111; color: #EEE;'}
    Here is some more text.

    # Another H1 section
    Finally, some ending text.

A logical section can also be forcefully ended in the following way,

.. code-block:: markdown

    ## H2 level section {: #someid .someclass style='background-color:#111; color: #EEE;'}
    Here is some more text.
    ## ---

    This text will be outside of the above logical section.

.. note::

   The default theme includes the classes ``.exercise`` and ``.interlude`` that can be used in this way.


Including Images
----------------

Include images by using the filename path relative to the source document. Chirun will detect images included in this way and
will copy them to the output directory automatically. `Attribute Lists <https://python-markdown.github.io/extensions/attr_list/>`_
can be used to customise image style.

.. code-block:: markdown

   ![A plot of y=sin(x)](images/lecture_sine2.png){width="70%"}


Markdown Slides
---------------

Slides can be written in Markdown and converted to a HTML page, reveal.js slides and printable PDF by creating a :ref:`Slides` item
type.

.. note::

    Be aware that the Markdown used by Chirun is slightly different to the Markdown used when using reveal.js's ``data-markdown``
    attribute. You need to use the Markdown variant described here.

An example of Markdown slides for Chirun can be found `here in the sample course <https://chirun-ncl.github.io/sample_course/markdown_slides/>`_.

The source document for the above Markdown slides can be found on GitHub at
https://raw.githubusercontent.com/chirun-ncl/sample_course/master/markdown/lecture.md

Slide Separator
~~~~~~~~~~~~~~~

Separate slides in Chirun Markdown by inserting a line containing nothing but (at least) 3 dashes, surrounded by a
blank line above and below::
 
    ---

The slide separator renders as a horizontal rule in the HTML web page version of the content.

Pause/Fragments
~~~~~~~~~~~~~~~

Insert a pause (a fragment, in reveal.js language) by inserting a line containing nothing but 3 dots separated by spaces,
surrounded by a blank line above and below::

    . . .

A pause is not rendered in the HTML web page version of the content.

Other Reveal.js Features
~~~~~~~~~~~~~~~~~~~~~~~~

Other reveal.js features can be enabled using `Attribute Lists <https://python-markdown.github.io/extensions/attr_list/>`_
to add the required data attributes to sections or individual items. For example::
 
    ## This slide will have a background color {data-background-color="aquamarine"}
    * Item 1
    * Item 2

    . . .

    * Item 3

    ---


Embedding Other Content
-----------------------

Numbas
~~~~~~

A Numbas exam can be embedded into a document with,

.. code-block:: markdown

   <numbas-embed data-url="https://numbas.mathcentre.ac.uk/[...]" data-id="exercise-1" data-cta="Show Exercise"></numbas-embed>

.. list-table::
   :header-rows: 1

   * - Attribute
     - Description
   * - ``data-url``
     - The URL to for the embeddable Numbas test
   * - ``data-id``
     - Some unique identifier for this test
   * - ``data-cta``
     - (Optional) Text to show on the button to load the test. Default: "Test Yourself"

YouTube
~~~~~~~

A YouTube video be embedded into a document with,

.. code-block:: markdown

   <youtube-embed data-id="EdyociU35u8"></youtube-embed>

.. list-table::
   :header-rows: 1

   * - Attribute
     - Description
   * - ``data-id``
     - The YouTube video ID

Vimeo
~~~~~~~

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
~~~~~~~

Chirun supports embedding content with providers that support `oEmbed <https://oembed.com>`_.

.. code-block:: markdown

   <oembed data-url="[...]"></oembed>

.. list-table::
   :header-rows: 1

   * - Attribute
     - Description
   * - ``data-url``
     - The URL of the oEmbed compatible content to be embedded


Code Blocks
-----------

Code blocks with syntax highlighting can be included using `SuperFences <https://facelessuser.github.io/pymdown-extensions/extensions/superfences/>`_.

This example shows two different ways to include code blocks. The first is a code block set to use Python syntax highlighting.
The second code block also displays Python code, but also includes a button that can be clicked to show the output from running the code.

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

