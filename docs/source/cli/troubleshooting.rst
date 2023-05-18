Troubleshooting
===============

The Chirun project makes use of `GitHub Issues <https://github.com/chirun-ncl/chirun/issues>`_ for bug reports and discussing issues.
You can use the search function on the Chirun issues page to see if your problem has been seen before.

.. rubric:: Help! My LaTeX notes won't compile!

Chirun compiles LaTeX documents using the `plasTeX <https://github.com/plastex/plastex>`_ Python package.
While it supports a wide array of TeX and LaTeX features, not all LaTeX packages are compatible.
Complex packages or packages relying on special features of the PDF format must be re-implemented in the Python lanaguge, and this process has not been completed for many packages.

If your document fails to build, the first thing to do is to take a look at which LaTeX packages you are using.
Try removing packages one by one, or simplifying your notes, until things start working.

If your notes build, but parts of the output are broken, you should check indiviual mathematical equations in your document.
Chirun renders mathematics on the web with MathJax, and again not all of the features available in LaTeX work fully in MathJax out of the box.

In short, it is a good idea to start with short and simple LaTeX documents and slowly build up complexity once they are building successfully.

.. rubric:: Running ``chirun`` throws an error related to certificate validation on macOS

To fix this problem on macOS run the command:

.. code-block::

    sudo /Applications/Python\ 3.X/Install\ Certificates.command

(where ``3.X`` is your version of Python) to install the appropriate SSL CA certificates.
This change allows the headless version of Chromium to download successfully.
