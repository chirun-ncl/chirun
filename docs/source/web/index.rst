The Chirun web frontend
=======================


.. note::
    This page is in progress.

The Chirun web frontend provides an interface to edit and build Chirun packages, as well as an LTI 1.3 tool for integrating Chirun material with learning management systems.


.. _web-public-build:

Unauthenticated use on the web
------------------------------

You can use the Chirun web frontend without creating an account.

On the index page, click :guilabel:`Create a new package`.

Upload your source file(s), and click :guilabel:`Create`.

You are shown the configuration form for your package.
If you uploaded a :file:`config.yml` file, the form is already filled in with the values from that file, otherwise it begins blank and you must fill out the package's structure.

Once you have saved the configuration, the package is built.
Click on :guilabel:`View the generated content` to go to the package's :ref:`management page <web-package-management>`.

Access to the package is granted only by knowing the address of this page, so make sure to bookmark it.
The URL is shown at the top of the management page so you can copy it.

.. _web-package-management:

Managing packages
-----------------

The management page for a package shows links to configure or edit the package; links to view the output; and a log of times the package has been built.

The :guilabel:`Configure` link takes you to the course configuration editor.
Use this to change :ref:`package-level settings <global-settings>` and edit the structure of the package.
After you save the configuration, the package is automatically rebuilt.

The :guilabel:`View or edit files in this package` link takes you to the source file editor.
You can edit existing files or create new files.
The course is not automatically rebuilt after you make changes to source files: you must go back to the management page and click the :guilabel:`Build` button.

Click :guilabel:`Download the generated content as a .zip file` to get a copy of the output that you can upload to your own web space.

Configure
#########

See the reference for :ref:`content item types <content-item-types>`.
The configuration editor shows the structure of the package.

On the left is a tree with the :ref:`package-level settings <global-settings>` at the top, and content items underneath.

Package settings
****************

Package metadata
^^^^^^^^^^^^^^^^

Title
    The title of the course.

Author
    The names of the person or people who wrote the course.

Institution
    The name of the institution the course belongs to.

Course code
    A short code for the course.

Year
    The year the course is delivered.

Language
    The language that the course material is written in.
    If the Chirun interface has been translated to this language, the rest of the interface will be presented in that language.
    See :ref:`theme-translations`.

Build options
^^^^^^^^^^^^^

Build PDFs?
    If ticked, then PDF versions of each item will be built, in addition to the HTML version.
    If not ticked, only HTML versions will be built.

Number of PDF runs
    The number of times to run the PDF compilation process.
    LaTeX sometimes requires two runs in order to correctly pick up internal references.
    The default is 1.

URL to load MathJax
    Chirun uses MathJax to render mathematical notation in HTML versions of material.
    If left blank, the default URL will be used.


Item settings
*************

For each item. 


Delete
######

Upload files
############

View or edit files in this package
##################################

The build process
-----------------

While a package is being built, you are shown the text output of the build process.

If the build process fails with an error, you should look through this text for a hint about what went wrong.
It's best to read from the bottom up: the most useful error message is normally towards the end.

.. note::
   At the moment, the public web frontend at lti.chirun.org.uk doesn't show the live build process.
   You'll have to reload the page until the build process has finished.

If the build process is successful, you're shown a link labelled :guilabel:`View the generated content`, which takes you back to the package management page.
