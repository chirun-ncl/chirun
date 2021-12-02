``config.yml`` Properties
=========================

The following is a list of top level properties that can be set in ``config.yml`` when creating
a Chirun course package.

.. list-table::
   :header-rows: 1

   * - Argument
     - Description
   * - ``title``
     - The title used for the output package
   * - ``author``
     - The name(s) of the output package author(s)
   * - ``code``
     - An optional "course code" for the output package
   * - ``year``
     - An optional year for the output package
   * - ``structure``
     - An array of content items to be built
   * - ``themes``
     - An array of themes to be used
   * - ``build_pdf``
     - Should PDFs be built by default (where possible)?
   * - ``base_dir``
     - The base URL used when building packages with absolute file paths
   * - ``js``
     - An array of paths to JS files to include in HTML output
   * - ``css``
     - An array of paths to CSS files to include in HTML output

.. note::
   At the moment the :ref:`Chirun Public Content Builder` and :ref:`chirun_lti` use the ``code``
   property internally when building packages and so overrides any course code given in ``config.yml``.

   This is expected to change in a future version.
