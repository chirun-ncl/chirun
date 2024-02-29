.. _chirun-latex-package:

####################
Chirun LaTeX package
####################

When compiling LaTeX documents in Chirun, the ``chirun`` LaTeX package provides some supporting functionality.

******************************
Using the Chirun LaTeX package
******************************

Use the ``chirun`` LaTeX package in your documents by adding the following line to you preamble:

.. code-block:: latex

    \usepackage{chirun}

.. warning::

    Chirun requires and loads the ``hyperref`` package automatically.
    If the ``hyperref`` package is loaded for a second time it can lead to an error of the form,

    .. code-block::

        ! LaTeX Error: Option clash for package hyperref.

    One solution is to ensure that the ``hyperref`` package is loaded first:

    .. code-block:: latex

        \usepackage[colorlinks,linkcolor={blue}]{hyperref}
        \usepackage{chirun}

    An alternative solution is to load only the ``chirun`` package and pass any required options for ``hyperref``
    via the ``chirun`` package options:

    .. code-block:: latex

        \usepackage[hyperref={colorlinks,linkcolor={blue}}]{chirun}


********
Features
********

.. _ifplastex:

Different behaviour when rendering HTML or PDF
==============================================

Chirun uses plasTeX to render LaTeX documents in HTML format.

There are cases when you would like different behaviour depending on whether the document is being rendered with ``pdflatex`` or with plasTeX: there might be LaTeX code that only works in PDF output, or you might want to write raw HTML code for HTML output.
You can use the ``\ifplastex`` command to specify a block of code that should be used in plasTeX, and another block that should be used in ``pdflatex``.

Here's an example: in HTML, the ``\mylesson`` command just starts a new chapter; in PDF, it manipulates the section and chapter counters and specifies a different font and spacing for the lesson's header.

.. code-block:: latex

    \ifplastex
        \newcommand{\mylesson}[2]{
            \chapter{#1}
        }
    \else
        \newcommand{\mylesson}[2]{
        \refstepcounter{chapter}
         {\huge\sffamily\bfseries Lesson \thechapter\autodot~#1\strut}
        \vspace*{5cm}
        \setcounter{section}{0}
        }
    \fi

It's quite common to only need some commands for PDF output, for example using packages that plasTeX doesn't support, or changing page dimensions.
In this case, it's more convenient to use the ``\ifpdflatex`` command:

.. code-block:: latex

    \ifpdflatex
        \usepackage{cite}
        \setlength{\textwidth}{168mm}
    \fi

Image alt text
==============

All images should have accompanying alt text, describing the content of the image for users who can't see it.

Use the ``\alttext`` command inside a ``figure`` block to add alt text:

.. code-block:: latex

    \begin{figure}
        \includegraphics[width=0.8\textwidth]{images/hist.pdf}
        \caption{A histogram originally provided in .pdf format}
        \alttext{A plot titled "A histogram". The x axis is labelled "x-axis".
                The y axis is labelled "Frequency". The histogram shows a peak at
                a value of approximately 70.}
    \end{figure}

The content of the ``\alttext{}`` command will be attached to the figure image as alt text in the HTML web page.
The  to the contentLaTeX PDF output is unaffected.

Embed HTML
==========

You can produce a block of HTML with the ``HTML`` environment:

.. code-block:: latex

    \begin{HTML}
        <div>
            <p>This raw HTML will be produced in the output directly</p>
        </div>
    \end{HTML}

The raw HTML will not appear in the LaTeX PDF output.

Embed a Numbas test
===================

.. code-block:: latex

    \numbas[Test Yourself:]{https://numbas.mathcentre.ac.uk/[...]}

The Numbas test will appear embedded in the HTML web page.

In the LaTeX PDF output, a link to the test will be shown.

Embed Youtube/Vimeo
===================

.. code-block:: latex

    \youtube[YouTube:]{EdyociU35u8}
    \vimeo[Vimeo:]{8169375}

The video will appear embedded in the HTML web page.

In the LaTeX PDF output, a link to the content will be shown.

