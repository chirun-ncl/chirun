The structure of a Chirun package
=================================

A Chirun package's source code contains at the very least a file called :file:`config.yml` defining the package's structure and specifying global settings.
This file can be created by the web frontend, or you can write it yourself.

Source files for content items can appear anywhere in the same directory as :file:`config.yml` or in subdirectories.
All paths are relative to the directory containing :file:`config.yml`.

A special directory containing static files will be copied over exactly, with no modifications.
By default, this is a directory called :file:`static`, at the top of the package.
You can use a different path by changing the ``static_dir`` setting.

LaTeX files are processed both with ``pdflatex``, to produce PDFs, and ``plasTeX``, to produce web pages.
Both processors can handle inclusion of other files, so you can split a LaTeX document across several files, or make a library of macros to use in several items.

The core of a Chirun package is a hierarchy of :dfn:`content items`.
A content item is a chapter of text, a slides presentation, a code notebook, a static file or a link to an external resource.
See the documentation on :ref:`content item types <content-item-types>` for more information on what's possible.

There is a schema for the :file:`config.yml` file at `chirun.org.uk/schema <https://www.chirun.org.uk/schema>`_.

Refer to this schema if you edit :file:`config.yml` yourself; if you use the web frontend's configuration form it will ensure the file matches the schema for you.
