Installation Instructions
=========================

Prerequisites
-------------

First, prepare the environment by installing prerequisites required for Chirun to function.

Linux (Ubuntu 18.10+)
^^^^^^^^^^^^^^^^^^^^^

These instructions are written with Ubuntu in mind, but other Linux system package managers should be
able to be used, albeit with different package names.

 * Ensure Git, Python3 and virtualenv are installed::

       apt install python3 python3-virtualenv

 * Ensure a system TeX distribution is installed, such as TeX Live::

       apt install texlive-full

 * Install the packages pdf2svg, pdftoppm, pdftk and libyaml::

       apt install pdf2svg poppler-utils libyaml-dev pdftk-java

MacOS
^^^^^

* Install a system TeX distribution, such as MacTeX from https://tug.org/mactex/

* Install Homebrew by following the instructions at https://brew.sh

* Use the ``brew`` command to install pdf2svg, pdftoppm, pdftk and libyaml::

    brew install poppler
    brew install pdf2svg
    brew install libyaml
    brew install pdftk-java

* Install virtualenv by running::

    pip3 install virtualenv

* If you are not using the default Apple-provided build of Python 3 ( e.g. Python is installed under ``/Applications/Python 3.X``, where ``3.X`` is the version),
  ensure that the SSL CA certificates are installed by running::

    sudo /Applications/Python\ 3.X/Install\ Certificates.command

Windows
^^^^^^^

Chirun can be used by following the Linux instructions in `WSL <https://docs.microsoft.com/en-us/windows/wsl/install>`_.

Further Windows documentation will be added in future.

Quick Installation
------------------

Follow these instructions to install the Chirun Python package. If you plan to modify Chirun or
perform development work, follow the instructions in the next section instead.

 * Ensure you have installed the prerequisites shown in the previous section.

 * Create a Python3 virtualenv and activate it::

    virtualenv -p python3 chirun_env
    source ./chirun_env/bin/activate

 * Install the Chirun Python package::

    pip install git+https://github.com/chirun-ncl/chirun.git

The command ``chirun`` is now available for use whenever the virtualenv is active. You should
now continue to the next section and compile the sample course to ensure everything works.

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

Run the following command with the virtualenv active to upgrade the installed version of Chirun::

    pip install --upgrade git+https://github.com/chirun-ncl/chirun.git

.. note:: 

    You may need to run the above command with an extra ``--force-reinstall`` argument if the version
    number has not been changed between updates.

Development Installation
------------------------

You should only follow these instructions if you plan to modify Chirun or perform development work.

 * Create a Python3 virtualenv and activate it::

    virtualenv -p python3 chirun_env
    source ./chirun_env/bin/activate

 * Clone the Chrirun Python package repository::

    git clone https://github.com/chirun-ncl/chirun.git

 * Enter the chirun package directory, ``cd chirun``
 * Install all the requirements::

    pip install -r requirements.txt

 * Install the chirun tool into your environment::

    pip install -e .

The command ``chirun`` is now available for use. You should now compile the sample course and ensure everything works.

Development Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To upgrade the development installation pull the latest changes from this git repository and install any new requirements::

    cd chirun
    git pull
    pip install -r requirements.txt
