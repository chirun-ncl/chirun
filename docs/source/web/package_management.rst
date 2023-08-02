.. _web-package-management:

#################
Managing packages
#################

The management page for a package shows links to configure or edit the package; links to view the output; and a log of times the package has been built.

The :guilabel:`Configure` link takes you to :ref:`the course configuration editor <package-config-editor>`.
Use this to change :ref:`package-level settings <global-settings>` and edit the structure of the package.
After you save the configuration, the package is automatically rebuilt.

The :guilabel:`View or edit files in this package` link takes you to the source file editor.
You can edit existing files or create new files.
The course is not automatically rebuilt after you make changes to source files: you must go back to the management page and click the :guilabel:`Build` button.

Click :guilabel:`Download the generated content as a .zip file` to get a copy of the output that you can upload to your own web space.

.. _package-management-url:

******************
The management URL
******************

Access to the package is granted only by knowing the address of its management page, so make sure to bookmark it.

The URL is shown at the top of the management page under the heading :guilabel:`Manage this package` so that you can copy it.

.. _package-config-editor:

*********
Configure
*********

Click :guilabel:`Configure` link to open the package configuration editor.

See the reference for :ref:`content item types <content-item-types>`.
The configuration editor shows the structure of the package, as defined in the file :file:`config.yml`.

On the left is a tree with the :ref:`package-level settings <global-settings>` at the top, and content items underneath.

You can reorder items by clicking the :guilabel:`Move this item` buttons after selecting an item, or using the keyboard by focusing the item in the structure tree and pressing :kbd:`Shift` and an arrow key.

The editor does not save automatically; once you have made changes you must click the :guilabel:`Save` button.
This will overwrite the package's :file:`config.yml` and the package will automatically be rebuilt.

Package settings
================

The :guilabel:`Package settings` button shows settings affecting the whole package, as described in :ref:`the package-level settings reference <global-settings>`.

Package metadata
----------------

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
-------------

Build PDFs?
    If ticked, then PDF versions of each item will be built, in addition to the HTML version.
    If not ticked, only HTML versions will be built.

Number of PDF runs
    The number of times to run the PDF compilation process.

    Only shown if :guilabel:`Build PDFs?` is ticked.

    LaTeX sometimes requires two runs in order to correctly pick up internal references.
    The default is 1.

URL to load MathJax
    Chirun uses MathJax to render mathematical notation in HTML versions of material.
    If left blank, the default URL will be used.


Item settings
=============

Click the :guilabel:`Add an item` button to add a new item to the package structure.

You will first be asked to select the type of the part, and then the item will be created.

You must enter a :guilabel:`Title` and choose a :guilabel:`Source` file or address for the item.

When selecting a source file, only files with a valid extension for the item type are shown.
For most item types, this is ``.tex`` or ``.md``.

There are other fields corresponding to the settings described in :ref:`the reference <content-item-types>`.

*******************
Delete this package
*******************

If you delete a package, its source files and any built output are deleted, permanently.

.. _package-file-viewer:

**********************************
View or edit files in this package
**********************************

The :guilabel:`View or edit files in this package` link takes you to view the files in the package.

Text files can be edited in this view, or replaced by selecting a file with the :guilabel:`Replace this file` field.

Image files can be viewed or replaced but not edited in this view.

To start a new text file, write its filename in the :guilabel:`New file` field.

The form to upload files allows you to select one or more files to be uploaded.
If you upload a :file:`.zip` file, the contents are extracted.


*****************
The build process
*****************

The system maintains a copy of the package's source files, and a copy of the built output.

A package is automatically built after it is uploaded, or when you save changes to the config using the :ref:`configuration editor <package-config-editor>`.

You can click :guilabel:`Build` to prompt the system to rebuild the package.
You should do this after uploading or changing any files using the :ref:`file viewer <package-file-viewer>`.

While a package is being built, you are shown the text output of the build process.

If the build process fails with an error, you should look through this text for a hint about what went wrong.
It's best to read from the bottom up: the most useful error message is normally towards the end.

.. note::
   At the moment, the public web frontend at lti.chirun.org.uk doesn't show the live build process.
   You'll have to reload the page until the build process has finished.

If the build process is successful, you're shown a link labelled :guilabel:`View the generated content`, which takes you back to the package management page.
