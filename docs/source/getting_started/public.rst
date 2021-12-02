Chirun Public Content Builder
=================================

A free to use public Chirun package and document builder is available at https://mas-coursebuild.ncl.ac.uk/public/,
removing the requirement to install the Chirun software and its prerequisites to your local machine.

.. warning::
   The public builder produces zipped HTML packages that must be downloaded and hosted for the web by some
   other service. The converted notes expire from the public builder servers after a short while.

Convert a Standalone Document
-----------------------------

The Chirun public builder can be used to convert a single document from LaTeX or Markdown source into an
accessible web-based HTML package. The process is as follows:

 * Visit https://mas-coursebuild.ncl.ac.uk/public/

 * Click the button labelled "Choose Files" and select your LaTeX or Markdown files to be uploaded and converted

 * (Optional) Click Show/hide settings to tweak the build settings

 * Click the button labelled "Upload"

Your document will be converted and the build log showing the output from the Chirun tool will be shown on screen.
This output will be useful to help debug if anything goes wrong in the conversion process. For help and advice on
Chirun build errors, see the :ref:`Troubleshooting` section.

If the conversion is successful, the message ``Finished!`` will be displayed at the bottom of the build log and
the Download Output Package section will be displayed. Two new buttons are presented, 

 * Clicking "Preview Content" will open your converted document in a new tab. This form of the output is indended
   only as a preview and will expire after a short while.

 * Clicking "Download Package" will download the converted HTML output as a ``.zip`` file, ready to be distributed
   to learners, for example by extracting and uploading the content to a web hosting service.

Tweaking the Build Settings
---------------------------

When uploading a single document to the public builder, the build settings that would normally be controlled by
populating a Chirun ``config.yml`` file can instead be tweaked as part of the upload form.

The following settings are available:
 * The item type can be changed (see :ref:`Content Item Types` for further information)
 * For longer ``.tex`` documents the content can be automatically split on chapter or section
 * The item title can be customised
 * Showing a sidebar in the default theme can be enabled or disabled
 * Building a PDF version of the document can be turned on of off

.. note::
   Multiple source files can be selected for upload. Alternatively, source files can be compressed
   into a ``.zip`` file before uploading.


Build Chirun Course Packages
----------------------------

Chirun supports compiling multiple documents (forming a Chirun "course package") 
into a single output website. The source files are compiled into separate HTML pages
and hyperlinked together.

Chirun course packages are controlled by a course configuration file named ``course.yml``.
To compile a Chirun course package, first compress all the source documents and a valid
``course.yml`` into a single ``.zip`` file. Then, follow the instructions in the previous
section and upload the ``.zip`` file to the public builder.

More information on building a valid Chirun ``course.yml`` file can be found in the
:ref:`Compile a Chirun Course Package` section.

The `.zip` file will be extracted and the configuration file will be automatically recognised
and used. The properties in the ``course.yml`` file will override the settings selected in
the "Show/hide settings" section.


Compile the Sample Course
-------------------------

The Chirun sample course can be compiled with the public builder and is a good place to start if you'd prefer to
modify a working template rather than start from scratch.

 * The sample course is available on GitHub. First, either download the sample course files or clone the repository using git::

      git clone https://github.com/chirun-ncl/sample_course.git

 * Once you have the source files, enter the ``sample_course`` directory.

 * If you'd like to edit the sample course files to make some changes, do so now.

 * Compress the contents of the ``sample_course`` directory into a ``.zip`` file ready to upload to the public builder.
 
 * Follow the instructions in the section :ref:`Convert a Standalone Document`, but upload the compressed ``.zip`` file
   for conversion. All other instructions remain the same.

.. note::

    * Ensure that your ``config.yml`` file is at the `root` of the ``.zip`` package uploaded to the Chirun public builder.
    * You should not use the "Show/hide settings" section, as the settings there are overridden by the ``config.yml``
      file in the sample course.

