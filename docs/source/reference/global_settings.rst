.. _global-settings:

######################
Package-level settings
######################

There are several package-level settings, giving metadata about the package, its contents, and some options controlling the build process.

Title (``title``)
    The title of the package.

Author (``author``)
    The name(s) of the package's author(s).

Institution (``institution``)
    The owning institution of the content, e.g. "University of Somewhere".

Course code (``code``)
    A code for the course or module that this material belongs to, e.g. "MAS0001".

Year (``year``)
    The year or date that the material is delivered.

Language (``locale``)
    The `ISO 639-1 <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`__ code for the primary language that the material is presented in.
    Once Chirun has been translated to other languages, this will determine the language used for text in the interface.

    **Default value**: ``en`` (English)

Content (``content``)
    A list of :ref:`content items <content-item-types>` forming the content of the package.

Base directory (``base_dir``)
    The base directory of the output.
    It only makes sense to change this if you're running the chirun command-line tool on your own computer.
    
    **Default value**: ``build`` (relative to :file:`config.yml`)

Static files directory (``static_dir``)
    The path to your package's static files, which will be copied into the output unchanged.

    **Default value**: ``static``

Root URL (``root_url``)
    The root URL of the output.

    **Default value**: ``base_dir``, followed by ``code`` and ``theme``, if they're set.

Build PDFs? (``build_pdf``)
    Should PDF files be created?
    Turn off if you are happy just to provide HTML output.
      
    **Default value**: ``True``

Number of PDF runs (``num_pdf_runs``)
    The number of times to run ``pdflatex`` on LaTeX documents.
    Documents with complicated reference structures might need more than one run.
    
    **Default value**: ``1``

Build zip of entire package? (``build_zip``)
    Should a ``.zip`` file of the output be built?
    If enabled, then a zip file is built containing a copy of the whole output.
    The zip file's name is by default the slug of the package's title, inside the output directory.
    If you're using the command-line tool, you can specify a filename with the ``--output-zip`` parameter.
      
    **Default value**: ``True``

Format version (``format_version``)
    The version number of the config format used.

    **Default value**: ``2``

URL to load MathJax from (``mathjax_url``)
    The URL to load MathJax from.
    This should be MathJax v3.
    
    **Default value**: ``'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'``

Themes (``themes``)
    An array of themes to use.
    At the moment there's only one theme; see `the config schema <https://www.chirun.org.uk/schema/>`__ for the structure of this property if you're developing a new theme.

    **Default value**: Just the default theme.
