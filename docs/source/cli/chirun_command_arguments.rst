######################
Command line arguments
######################

*****
Usage
*****

.. code-block::

    usage: chirun [-h] [-o BUILD_PATH] [-v] [-vv] [-d] [-a] [--config CONFIG_FILE] [-f SOURCE_FILE] [dir]


*********
Arguments
*********

.. list-table::
   :header-rows: 1
   :widths: 50 40 10 

   * - Argument
     - Description
     - Default Value

   * - ``dir``
     - Path to a chirun compatible source directory
     - Current directory

   * - ``-h``
     - Show a help message and exit
     - 

   * - ``-o BUILD_PATH``
     - Set a directory to put build files in
     - ``build``

   * - ``-v``
     - Verbose output
     - 

   * - ``-vv``
     - Very verbose output
     - 

   * - ``-d``
     - Delete auxiliary files
     - 

   * - ``-a``
     - Output using absolute file paths, relative to ``root_url``
     - 

   * - ``--config CONFIG_FILE``
     - Path to a config file
     - ``config.yml``

   * - ``-f SOURCE_FILE``
     - Compile a single source file without using a config file.
     - 
