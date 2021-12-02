Compile a Chirun Course Package
===============================

Chirun supports compiling multiple documents (forming a Chirun "course package") 
into a single output website. The source files are compiled into separate HTML pages
and hyperlinked together.

Compiling a course package is very similar to the building a stanalone item. The file ``config.yml``
controls the structure and appearance of the Chirun course items.

Create ``config.yml`` with multiple items
---------------------------------------------

Extra documents can be included by populating the ``structure`` section of the ``config.yml`` file.

As an example, the following configuration file instructs Chirun to build two items of type ``chapter``.
An index page hyperlinking the items together will be included as part of the HTML output.

.. code-block:: yaml

    author: 'Ann Example'
    title: 'Example Course'
    structure: 
      - type: chapter
        source: item_one.tex
        title: 'Item One'
      - type: chapter
        source: item_two.tex
        title: 'Item Two'
    build_pdf: True

Save the above example in a file named ``config.yml``. Then, in the same directory, add two documents to
be included as part of the output produced Chirun. Finally, update the document titles and source filenames in
``config.yml`` to match your documents and the course package is ready to be built using Chirun. 

The Sample Course
-----------------

A full sample course is provided as a demonstration of how to build a Chirun course package and populate the
``config.yml`` file with items of various types. The following instructions describe how to obtain and build the sample course.

 * Use git to obtain a copy of the sample course package::

    git clone https://github.com/chirun-ncl/sample_course.git
 
 * Change into the directory and run ``chirun`` to build the sample course.

 * The HTML output will be in the ``build`` directory.

