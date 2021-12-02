Chirun LaTeX Package
=======================

When compiling LaTeX documents in Chirun, a LaTeX package is provided to provide some supporting functionality.

Using Chirun LaTeX Package
--------------------------

Use the ``chirun`` LaTeX package in your documents by adding the following line to you preamble:

.. code-block:: latex

    \usepackage{chirun}

Features
--------


Embed HTML
~~~~~~~~~~

.. code-block:: latex

    \begin{HTML}
        <div>
            <p>This raw HTML will be produced in the output directly</p>
        </div>
    \end{HTML}

The raw HTML will not appear in the LaTeX PDF output.

Embed Numbas Test
~~~~~~~~~~~~~~~~~

.. code-block:: latex

    \numbas[Test Yourself:]{https://numbas.mathcentre.ac.uk/[...]}

The Numbas test will appear embedded in the HTML web page. In the LaTeX PDF output, a link will be shown to the content.

Embed Youtube/Vimeo
~~~~~~~~~~~~~~~~~

.. code-block:: latex

    \youtube[YouTube:]{EdyociU35u8}
    \vimeo[Vimeo:]{8169375}

The video will appear embedded in the HTML web page. In the LaTeX PDF output, a link will be shown to the content.

Image Alt Text
~~~~~~~~~~~~~~

.. code-block:: latex

    \begin{figure}
        \includegraphics[width=0.8\textwidth]{images/hist.pdf}
        \caption{A histogram originally provided in .pdf format}
        \alttext{A plot titled "A histogram". The x axis is labelled "x-axis".
                The y axis is labelled "Frequency". The histogram shows a peak at
                a value of approximately 70.}
    \end{figure}

The content of the ``\altext{}`` command will be attached to the figure image as alt text in the HTML web page. The
LaTeX PDF output is unaffected.
