Credits
$$$$$$$

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 18cf0af34c194590b3eb391c2ef94074

As an open-source project, StrictDoc is based on the work of many people and organizations:

- StrictDoc receives contributions from other developers.
- StrictDoc is built using other open-source software.
- StrictDoc uses free hosting and Continuous Integration services provided for open-source software.
- StrictDoc uses the commercial versions of JetBrains IDEs for free.

This page gives due credit to everyone who made StrictDoc possible.

Contributions to StrictDoc
==========================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - e6de83e242bc4aea96622a2e7585f135

The core team: @stanislaw and @mettta.

The following people and organizations have contributed to StrictDoc. The contributions are listed in the alphabetic order.

- @BenGardiner – Import Excel feature, improvements of HTML and RST export, Document Fragments feature.
- @GGBeer – Generating bibliography with BibTeX (ongoing), improvements of Excel export.
- @haxtibal – Significant improvements and bug fixes to several StrictDoc features.
- @lochsh – MathJax support.
- @Relasym – Important fixes of how the documents are re-generated (or not).
- @stumpyfr – Improvements of Excel export.

Companies:

- `BUGSENG <https://www.bugseng.com>`_ and @RobertoBagnara have contributed bug reports and feature suggestions.
- `Kontrol <https://www.kontrol.tech>`_ have sponsored the work related to the early implementation of the ReqIF import/export feature (@alex.d, @cbernt, @Relasym).

Single/smaller contributions can be also seen on the `StrictDoc's Insights/Contributors <https://github.com/strictdoc-project/strictdoc/graphs/contributors>`_ page.

Open source software
====================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 4428ac9ec3504dda9f1e1e845ffb3c75

StrictDoc is based on other open source components. Without this support, we would have never reached where we are today.

StrictDoc was heavily inspired by the `Doorstop <https://github.com/doorstop-dev/doorstop>`_ project. Without the strong example of Doorstop, StrictDoc would probably never exist.

StrictDoc uses `textX <https://github.com/textX/textX>`_ as an underlying parser for the SDoc text markup language.

StrictDoc uses `Sphinx <https://www.sphinx-doc.org/en/master/>`_ and `Docutils <https://docutils.sourceforge.io>`_ for generating SDoc documents to RST, HTML and PDF formats.

StrictDoc has a satellite project `reqif <https://github.com/strictdoc-project/reqif>`_ which is built on top of the `lxml <https://lxml.de>`_ parser. The ``reqif`` library allows StrictDoc to import and export documents from/to ReqIF format.

StrictDoc uses `FastAPI <https://github.com/tiangolo/fastapi>`_ and a combination of `Turbo.js <https://turbo.hotwired.dev>`_  and `Stimulus.js <https://stimulus.hotwired.dev>`_ for its Web-based graphical interface. This combination helps StrictDoc to stick with the `HTML over the wire approach <https://hotwired.dev>`_.

StrictDoc uses `Jinja <https://jinja.palletsprojects.com>`_ as a templating engine. Jinja is used for both static HTML and RST exports as well as in the Web-based GUI.

StrictDoc uses `Pygments <https://pygments.org>`_ to color-code the source files for the requirements-to-source-files traceability feature.

StrictDoc uses `Tree-sitter <https://tree-sitter.github.io/tree-sitter/>`_ to enable language-aware parsing of source files for the requirements-to-source-files traceability feature.

StrictDoc uses `XlsxWriter <https://xlsxwriter.readthedocs.io>`_ and `xlrd <https://xlrd.readthedocs.io/en/latest/>`_ for its Excel export/import features.

The credits also recursively go to the building blocks of each of the above projects because most of them have their own dependencies.

Refer to the `configuration file <https://github.com/strictdoc-project/strictdoc/blob/main/pyproject.toml>`_ for an up-to-date summary of StrictDoc's dependencies.

Hosting and Continuous Integration
==================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 5b702e6f9b714e458b059912ca8e196a

StrictDoc is hosted on `GitHub <https://github.com>`_ and uses `GitHub Actions <https://docs.github.com/en/actions>`_ to run all of its build, test and release tasks. As an open-source project, StrictDoc gets these services from GitHub for free.

StrictDoc's documentation is hosted on `Read the Docs <https://readthedocs.org>`_.

Free and commercial IDEs by JetBrains
=====================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - b4729e592d104fe3818c8949615ffef9

For Python development, the StrictDoc core team uses the community version of
`PyCharm <https://www.jetbrains.com/pycharm/>`_
from `JetBrains <https://www.jetbrains.com/>`_.

In 2022-2023, the `Licenses for Open Source Development - Community Support <https://www.jetbrains.com/community/opensource/#support>`_ from JetBrains were provided to the core team for free, based on the precondition that StrictDoc is developed as completely free software, without any monetization mechanisms.
