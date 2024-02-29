.. _supported-latex-packages:

###################
LaTeX compatibility
###################

Chirun uses `plasTeX <http://plastex.github.io/plastex/>`__ to render LaTeX documents in HTML format.
It re-implements some LaTeX packages in order to produce more structured output, while it can use the original LaTeX implementation of some other packages without changes.
Because plasTeX doesn't work in exactly the same way as normal LaTeX, some LaTeX packages don't work as intended, and produce bad output or lead to unrecoverable errors.

plasTeX's default behaviour on encountering a macro that it doesn't know is to ignore the macro name and interpret the argument(s) as normal.
This can lead to unexpected behaviour, with arguments to commands appearing as plain text in the output.
The build log will contain a warning of the form ``WARNING: unrecognized command/environment: mycommand``.

Chirun's HTML output uses MathJax to render mathematical notation.
MathJax has its own set of supported commands: see the `TeX and LaTeX support section of the MathJax documentation <https://docs.mathjax.org/en/latest/input/tex/index.html>`__.
Chirun can expand some math-mode commands before they are processed by MathJax, but in other cases it has to leave the rendering entirely up to MathJax.

================================================
Tips for making LaTeX documents work with Chirun
================================================

Try to use only the packages you need: many authors have accumulated a very long document preamble, most of which isn't actually needed.

Commands which change the layout of the page or font sizes and styles will not have any effect in HTML output; if these cause a problem, put them inside an :ref:`ifpdflatex <ifplastex>` block.

If a document fails to compile, try moving some of your ``\usepackage`` commands into an ``\ifpdflatex`` block, so they're only loaded when making the PDF output.

Once you've identified a package or command that causes problems with plasTeX, if you really need it in the HTML output, please :ref:`tell us about it <reporting-bugs>`.

==================
Supported packages
==================

This section lists packages that we know about, and the level of support.

.. list-table::
    :header-rows: 1

    * - Package
      - Support

    * - ``abstract``
      - Not supported.

        When used, an unwanted ``#1`` appears at the top of the HTML output.

    * - ``amsbsy``
      - Stub package: commands are handled by MathJax.

    * - ``amscd``
      - Stub package.

        Diagrams are rendered as SVG images using pdf latex.

    * - ``amsthm``
      - Re-implemented by plasTeX.

    * - ``a4``
      - Re-implemented by plasTeX.

    * - ``a4wide``
      - Re-implemented by plasTeX.

    * - ``afterpage``
      - Re-implemented by plasTeX.

    * - ``alltt``
      - Re-implemented by plasTeX.

    * - ``amsart``
      - Re-implemented by plasTeX.

    * - ``amsbook``
      - Re-implemented by plasTeX.

    * - ``amsfonts``
      - Re-implemented by plasTeX.

    * - ``amsmath``
      - Re-implemented by plasTeX.

    * - ``amssymb``
      - Re-implemented by plasTeX.

    * - ``appendixnumberbeamer``
      - Stub package: doesn't do anything.

    * - ``article``
      - Re-implemented by plasTeX.

    * - ``babel``
      - Re-implemented by plasTeX.

    * - ``bbding``
      - Re-implemented by plasTeX.

    * - ``bbold``
      - Re-implemented by plasTeX.

    * - ``bbm``
      - Re-implemented by Chirun.

        The command ``\mathbbm`` is rewritten as ``\mathbb``.

    * - ``beamer``
      - Re-implemented by plasTeX.

        Beamer is a very large package and Chirun's support is rather basic.
        The document-style HTML output is usually usable, but the HTML slides format still needs a lot of work.

    * - ``beamerthemesplit``
      - Re-implemented by plasTeX.

    * - ``bm``
      - Stub package: commands are handled by MathJax.

    * - ``book``
      - Re-implemented by plasTeX.

    * - ``booktabs``
      - Re-implemented by plasTeX.

    * - ``cancel``
      - Stub package: commands are handled by MathJax.

    * - ``cantarell``
      - Not supported.

        This package provides a font, and plasTeX seems to hang while reading it.

    * - ``caption``
      - Re-implemented by Chirun.

        The options are ignored in HTML output, and only the ``\caption`` command is implemented.

    * - ``ccaption``
      - Re-implemented by plasTeX.

    * - ``changebar``
      - Re-implemented by plasTeX.

    * - ``CJK``
      - Re-implemented by plasTeX.

    * - ``CJKutf8``
      - Re-implemented by plasTeX.

    * - ``cleveref``
      - Re-implemented by plasTeX.

    * - ``color``
      - Re-implemented by plasTeX.

    * - ``comment``
      - Re-implemented by plasTeX.

    * - ``debugplastex``
      - Re-implemented by plasTeX.

    * - ``dsfont``
      - Re-implemented by Chirun.

        The command ``\mathds`` is rewritten as ``\mathbb``.

    * - ``embed``
      - Re-implemented by plasTeX.

    * - ``endfloat``
      - Re-implemented by plasTeX.

    * - ``enumerate``
      - Re-implemented by plasTeX.

    * - ``enumitem``
      - Re-implemented by Chirun.

    * - ``epsf``
      - Re-implemented by plasTeX.

    * - ``eso-pic``
      - Re-implemented by plasTeX.

    * - ``fancybox``
      - Re-implemented by plasTeX.

    * - ``fancyhdr``
      - Re-implemented by plasTeX.

    * - ``fancyvrb``
      - Re-implemented by plasTeX.

    * - ``fleqn``
      - Re-implemented by plasTeX.

    * - ``float``
      - Re-implemented by plasTeX.

    * - ``fontenc``
      - Re-implemented by plasTeX.

    * - ``forest``
      - Re-implemented by plasTeX.

    * - ``framed``
      - Re-implemented by Chirun.

        The following environments are supported: ``framed``, ``oframed``, ``shaded``, ``shaded*``, ``snugshade``, ``snugshade*``, ``leftbar``.

    * - ``geometry``
      - Re-implemented by plasTeX.

    * - ``graphics``
      - Re-implemented by plasTeX.

    * - ``graphicx``
      - Re-implemented by plasTeX.

    * - ``html``
      - Re-implemented by plasTeX.

    * - ``hyperref``
      - Re-implemented by plasTeX.

    * - ``ifpdf``
      - Re-implemented by plasTeX.

    * - ``iftex``
      - Re-implemented by plasTeX.

    * - ``ifthen``
      - Re-implemented by plasTeX.

    * - ``imakeidx``
      - Re-implemented by plasTeX.

    * - ``inputenc``
      - Re-implemented by plasTeX.

    * - ``isodate``
      - Not supported.

        See https://github.com/plastex/plastex/issues/362.

    * - ``jss``
      - Re-implemented by plasTeX.

    * - ``keyval``
      - Re-implemented by plasTeX.

    * - ``kvoptions``
      - Stub package: does nothing.

    * - ``lipsum``
      - Re-implemented by plasTeX.

    * - ``listings``
      - Re-implemented by plasTeX.

    * - ``lmodern``
      - Re-implemented by plasTeX.

    * - ``longtable``
      - Re-implemented by plasTeX.

    * - ``lscape``
      - Stub package.

        The ``\lscape`` environment is recognised but does nothing.

    * - ``makeidx``
      - Re-implemented by plasTeX.

    * - ``marginnote``
      - Re-implemented by plasTeX.

    * - ``mathtime``
      - Re-implemented by plasTeX.

    * - ``mathtools``
      - Re-implemented by plasTeX.

    * - ``memoir``
      - Re-implemented by plasTeX.

    * - ``mhchem``
      - Stub package: commands are handled by MathJax.

    * - ``microtype``
      - Re-implemented by plasTeX.

    * - ``minitoc``
      - Re-implemented by plasTeX.

    * - ``multicol``
      - Re-implemented by plasTeX.

    * - ``nameref``
      - Re-implemented by plasTeX.

    * - ``natbib``
      - Re-implemented by plasTeX.

    * - ``pgfplots``
      - Re-implemented by plasTeX.

    * - ``placeins``
      - Stub package: the `\FloatBarrier` command is accepted but ignored.

    * - ``polynom``
      - Re-implemented by Chirun.

        ``\polylongdiv`` and ``\polylonggcd`` are rendered as SVG images using pdflatex.

    * - ``pslatex``
      - Re-implemented by plasTeX.

    * - ``pspicture``
      - Re-implemented by plasTeX.

    * - ``pst-coil``
      - Re-implemented by plasTeX.

    * - ``pstricks``
      - Re-implemented by plasTeX.

    * - ``qrcode``
      - Re-implemented by Chirun.

        Only the ``nolinks`` package option is used.
        Only the following options for the ``\qrcode`` command are recognised: ``hyperlink``, ``link``, ``height``.

    * - ``quotchap``
      - Re-implemented by plasTeX.

    * - ``report``
      - Re-implemented by plasTeX.

    * - ``revtex4-2``
      - Re-implemented by Chirun.

    * - ``rotating``
      - Re-implemented by plasTeX.

    * - ``sectsty``
      - Not supported.

        Messes up section formatting in HTML even if none of its macros are used.

    * - ``setspace``
      - Re-implemented by plasTeX.

    * - ``shortvrb``
      - Re-implemented by plasTeX.

    * - ``splitbib``
      - Re-implemented by plasTeX.

    * - ``subcaption``
      - Re-implemented by Chirun.

    * - ``subfig``
      - Re-implemented by plasTeX.

    * - ``subfigure``
      - Re-implemented by plasTeX.

    * - ``tabularx``
      - Re-implemented by plasTeX.

    * - ``tabulary``
      - Re-implemented by plasTeX.

    * - ``tcolorbox``
      - Re-implemented by Chirun.

        Only the ``\tcolorbox`` and ``\newtcolorbox`` commands are recognised.
        The following options are recognised: ``colback``, ``colframe``, ``boxrule``, ``title``, ``coltitle``.

    * - ``textcomp``
      - Re-implemented by plasTeX.

    * - ``textpos``
      - Re-implemented by plasTeX.

    * - ``tikz-3dplot``
      - Stub package: diagrams are rendered as SVG images using pdflatex.

    * - ``tikz-cd``
      - Re-implemented by plasTeX.

    * - ``tikz``
      - Re-implemented by plasTeX.

    * - ``times``
      - Re-implemented by plasTeX.

    * - ``tocbibind``
      - Re-implemented by plasTeX.

    * - ``todonotes``
      - Re-implemented by plasTeX.

    * - ``type1cm``
      - Re-implemented by plasTeX.

    * - ``ucs``
      - Re-implemented by plasTeX.

    * - ``ulem``
      - Re-implemented by Chirun.

    * - ``unicode-math``
      - Re-implemented by plasTeX.

    * - ``url``
      - Re-implemented by plasTeX.

    * - ``verbatim``
      - Re-implemented by plasTeX.

    * - ``verse``
      - Re-implemented by plasTeX.

    * - ``wasysym``
      - Re-implemented by plasTeX.

    * - ``wrapfig``
      - Re-implemented by plasTeX.

    * - ``xcolor``
      - Re-implemented by plasTeX.

    * - ``xr-hyper``
      - Re-implemented by plasTeX.

    * - ``xr``
      - Re-implemented by plasTeX.

    * - ``xspace``
      - Stub package: doesn't do anything.

    * - ``xy``
      - Re-implemented by plasTeX.
