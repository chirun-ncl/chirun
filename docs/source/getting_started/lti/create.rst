Creating a Chirun Content Item in the VLE
------------------------------------------

Once the Chirun LTI Provider has been setup and registered with your VLE, you should be able to add a Chirun LTI item
to your course. The precise method to add a Chirun LTI item will vary based on the VLE, but the action should be labelled
similarly to:

    * Add activity or resource
    * Add external tool
    * Insert LTI item/link
    * LTI teaching tool

After a source file(s) has been uploaded by an instructor, students can select the new activity
listed in the VLE to access the HTML content output by Chirun.

Uploading Content
-----------------

The simplest way to use the Chirun LTI Provider is to convert a single document from LaTeX or Markdown source.
Chirun will convert the document into an accessible web page, and then display the web page to a learner when they click
on the LTI item in the VLE.

The process to upload your content to the Chirun LTI Provider is very similar to uploading content to the
:ref:`Chirun Public Content Builder`. The major difference is rather than providing a package to download, the LTI
Provider will automatically host your resulting package on the web, in a location accessible only to the learners registered
for the course.

Follow the instructions below to upload content,

  * Create a Chirun LTI activity and access the LTI item as an instructor to load the dashboard

  * When there is no content associated with the Chirun LTI item, the instructor dashboard will redirect to the Upload page

  * Click the button labelled "Choose Files" and select your LaTeX or Markdown files to be uploaded and converted

  * (Optional) Click Show/hide settings to tweak the build settings

  * Click the button labelled "Upload"

The following build settings are available:
 * The content item type can be changed (see :ref:`Content Item Types` for further information)
 * For longer ``.tex`` documents, optionally choose to split the document at certain levels
 * The content item's title can be customised
 * Showing a sidebar in the default theme can be turned on or off
 * Additionally building a PDF version of the document can be turned on of off

Build Log
---------

Once you have uploaded your content it will begin to be converted and you will be redirected to the build log page.
The output as Chirun runs and processes your document will be shown on screen.

The build log will help you debug the problem if anything goes wrong in the conversion process. For help and advice on
Chirun build errors, see the :ref:`Troubleshooting` section.

If the conversion is successful, the message ``Finished!`` will be displayed at the bottom of the build log.

Student Preview
---------------

After your content has been built successfully, you can preview the content as a student by selecting "View Content"
at the top of the instructor dashboard, then clicking "View as Student". The converted content will open in a new tab. If
your VLE supports masquerading as a learner, you can also open the Chirun activity from the VLE while the student role
is active.

The "View All Content" button is used to view all content, regardless of Chirun :ref:`Adaptive Release` settings.

Convert a Chirun Course Package
---------

The above section describes uploading a single document for conversion with Chirun. However, Chirun also
supports compiling multiple documents (forming a Chirun "course package"). The source files are compiled
into separate HTML pages and hyperlinked together.

Using this method the entire uploaded content, made up of multiple source files, can be accessed via
a single Chirun LTI item in your VLE.

Chirun course packages are controlled by a course configuration file named ``course.yml``.
To compile a Chirun course package, first compress all the source documents and a valid
``course.yml`` into a single ``.zip`` file. Then, follow the instructions in the previous
sections and upload the ``.zip`` file to the Chirun LTI Provider.

More information on building a valid Chirun ``course.yml`` file can be found in the
:ref:`Compile a Chirun Course Package` section.

The `.zip` file will be extracted and the configuration file will be automatically recognised
and used. The properties in the ``course.yml`` file will override the settings selected in
the "Show/hide settings" section.
