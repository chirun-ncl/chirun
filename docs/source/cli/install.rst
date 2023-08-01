.. _install-chirun-python-package:

#########################
Installation Instructions
#########################

*************
Prerequisites
*************

First, prepare the environment by installing prerequisites required for Chirun to function.


Linux (Ubuntu 18.10+)
=====================

These instructions are written with Ubuntu in mind, but other Linux system package managers should be
able to be used, albeit with different package names.

 * Ensure Git, Python3 and virtualenv are installed::

       apt install python3 python3-virtualenv

 * Ensure a system TeX distribution is installed, such as TeX Live::

       apt install texlive-full

 * Install the packages pdf2svg, pdftoppm, pdftk and libyaml::

       apt install pdf2svg poppler-utils libyaml-dev pdftk-java

MacOS
=====

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
=======

Chirun can be used by following the Linux instructions in `WSL <https://docs.microsoft.com/en-us/windows/wsl/install>`_.

Further Windows documentation will be added in future.

******************
Quick Installation
******************

Follow these instructions to install the Chirun Python package. If you plan to modify Chirun or
perform development work, follow the instructions in the :ref:`Development Installation <development-installation>` section instead.

First, ensure you have installed the prerequisites shown in the previous section.

Next, create an environment for Chirun to be installed in, using either the virtualenv
or Conda instructions below.

Virtualenv
==========

 * Create a Python3 virtualenv environment and activate it::

    virtualenv -p python3 chirun_env
    source ./chirun_env/bin/activate

 * Install the Chirun Python package::

    pip install git+https://github.com/chirun-ncl/chirun.git

Conda
=====

If you are using Anaconda or the Conda Environment Manager, run the following commands to create a
new environment and install Chirun.

 * Create a Conda environment and activate it::

    conda create --name chirun
    conda activate chirun

 * Install ``pdf2svg`` in the environment::

    conda install pdf2svg

 * Install the Chirun Python package::

    pip install git+https://github.com/chirun-ncl/chirun.git --upgrade-strategy only-if-needed

The command ``chirun`` is now available for use whenever the new environment is active. You should
now continue to :ref:`compile the sample course <sample-course>` to ensure everything works.

********************
Upgrade Instructions
********************

Run the following command with the Chirun environment active to upgrade the installed version of Chirun::

    pip install --upgrade git+https://github.com/chirun-ncl/chirun.git

.. note::

    You may need to run the above command with an extra ``--force-reinstall`` argument if the version
    number has not been changed between updates.

.. note::

    Run the above command with an extra ``--upgrade-strategy only-if-needed`` argument if you are using Conda.



.. _development-installation:

************************
Development installation
************************

You should only follow these instructions if you plan to modify Chirun or perform development work.

 * Create a Python3 virtualenv and activate it::

    virtualenv -p python3 chirun_env
    source ./chirun_env/bin/activate

 * Clone the Chrirun Python package repository::

    git clone https://github.com/chirun-ncl/chirun.git

 * Enter the chirun package directory::

    cd chirun

 * Install all the requirements::

    pip install -r requirements.txt

 * Install the chirun tool into your environment::

    pip install -e .

The command ``chirun`` is now available for use. You should now compile the sample course and ensure everything works.

Development Upgrade Instructions
================================

To upgrade the development installation pull the latest changes from this git repository and install any new requirements::

    source ./chirun_env/bin/activate
    cd chirun
    git pull
    pip install -r requirements.txt
