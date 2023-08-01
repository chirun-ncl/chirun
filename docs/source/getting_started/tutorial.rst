.. _tutorial:

########
Tutorial
########

This tutorial will guide you through the process of creating a new Chirun package, and processing it with the web frontend.

We'll start by writing a short LaTeX file, called :file:`notes.tex`::

    \documentclass[a4paper]{report}
    \usepackage{chirun}

    \begin{document}
        This is my LaTeX document!
    \end{document}

Go to `the Chirun web frontend <https://lti.chirun.org.uk>`__, and click on :guilabel:`Create a new package`.

The first thing to do is to upload the source files you've got - in this case, just the above LaTeX file.

Drag :file:`notes.tex` on to the :guilabel:`Files` input, and click :guilabel:`Upload`.

You're then shown the configuration editor.
Chirun needs to know the structure of your course - one you've got several pieces of material, it needs to know how to group them and how they should each be presented.

The first screen of the editor, :guilabel:`Package settings`, contains settings that apply to the whole package.
Fill in a title for the package and your name.
You can leave the rest blank for now.

Then click :guilabel:`Add an item`.
The LaTeX file will be a chapter in the course: leave the :guilabel:`Type` field set to "Chapter", then click on the :guilabel:`Source` field and select :file:`notes.tex`.
Leave all the other settings as they are, and click the :guilabel:`Save` button at the top of the page.

.. note::

    It's our intention to automatically come up with a default configuration when you create a new package, for example adding an item for each :file:`.tex` or :file:`.md` file you upload.
    For now, you have to do it yourself!

The package will then be *built*: Chirun will process the source material and produce HTML and PDF versions of the notes we provided.

Once it's complete, click on :guilabel:`View the generated content`.

This takes you to the management page for your package.
Access to the package is granted only by knowing the address of this page, so bookmark it!
The URL is shown at the top of the management page so you can copy it.

Under :guilabel:`View this package's content`, click on the :guilabel:`Introduction` link to see the top level of the output.
There's not much on that page, just the title, your name, and a link to the notes chapter.

