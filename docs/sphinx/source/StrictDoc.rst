Introduction
============

StrictDoc is software for writing technical requirements and specifications.

Summary of StrictDoc features:

- The documentation files are stored as human-readable text files.
- A simple domain-specific language DSL is used for writing the documents. The
  text format for encoding this language is called SDoc (strict-doc).
- StrictDoc reads `*.sdoc` files and builds an in-memory representation of the
  document tree.
- From this in-memory representation, StrictDoc can generate the documentation
  into a number of formats including HTML, RST, PDF, Excel.
- The focus of the tool is modeling requirements and specifications documents.
  Such documents consist of multiple statements like "system X shall do Y"
  called requirements.
- The requirements can be linked together to form the relationships, such as
  "parent-child", and from these connections, many useful features, such as
  `Requirements Traceability <https://en.wikipedia.org/wiki/Requirements_traceability>`_
  and Documentation Coverage, can be derived.

**Warning:** The StrictDoc project is still under construction. See the Roadmap
section to get an idea of the overall project direction.

Examples
========

"Hello World" example of the text language:

.. code-block:: text

    [DOCUMENT]
    NAME: StrictDoc

    [REQUIREMENT]
    UID: SDOC-HIGH-REQS-MANAGEMENT
    TITLE: Requirements management
    STATEMENT: StrictDoc shall enable requirements management.

For a more comprehensive example check the source file of this documentation
which is written using StrictDoc:
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/master/docs/strictdoc.sdoc>`_.

- `StrictDoc HTML export <https://strictdoc.readthedocs.io/en/latest/strictdoc-html>`_
- `StrictDoc HTML export using Sphinx <https://strictdoc.readthedocs.io/en/latest>`_
- `StrictDoc PDF export using Sphinx <https://strictdoc.readthedocs.io/_/downloads/en/latest/pdf/>`_

Getting started
===============

Requirements
------------

- Python 3.6+
- macOS, Linux or Windows

Installing StrictDoc as a Pip package
-------------------------------------

.. code-block:: text

    pip install strictdoc

Installing StrictDoc from GitHub (development)
----------------------------------------------

`Poetry <https://python-poetry.org>`_ has to be installed first.

.. code-block:: text

    git clone git@github.com:stanislaw/strictdoc.git && cd strictdoc
    poetry install
    poetry run strictdoc
    poetry run invoke test

StrictDoc can also be developed and run without Poetry:

.. code-block:: text

    git clone git@github.com:stanislaw/strictdoc.git && cd strictdoc
    # for running strictdoc:
    pip install textx jinja2 docutils
    python3 strictdoc/cli/main.py
    # for running tests:
    pip install invoke pytest pytidylib html5lib
    invoke test

Hello world
-----------

.. code-block:: text

    git clone git@github.com:stanislaw/strictdoc.git && cd strictdoc
    strictdoc export docs/

SDoc syntax
===========

StrictDoc defines a special syntax for writing specifications documents. This
syntax is called SDoc and it's grammar is encoded with the
`textX <https://github.com/textX/textX>`_
tool.

The grammar is defined using textX language for defining grammars and is
located in a single file:
`grammar.py <https://github.com/strictdoc-project/strictdoc/blob/master/strictdoc/backend/dsl/grammar.py>`_.

This is how a minimal possible SDOC document looks like:

.. code-block::

    [DOCUMENT]
    NAME: StrictDoc

This documentation is written using StrictDoc. Here is the source file:
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/master/docs/strictdoc.sdoc>`_.

Export options
==============

HTML documentation tree by StrictDoc
------------------------------------

This is a default export option supported by StrictDoc.

The following command creates an HTML export:

.. code-block:: text

    strictdoc export docs/ --formats=html --output-dir output-html

**Example:** This documentation is exported by StrictDoc to HTML:
`StrictDoc HTML export <https://strictdoc.readthedocs.io/en/latest/strictdoc-html>`_.

**Note:** The options `--formats=html` and `--output-dir output-html` can be
skipped because HTML export is a default export option and the default output
folder is `output`.

Standalone HTML pages (experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following command creates a normal HTML export with all pages having their
assets embedded into HTML using Data URI / Base64:

.. code-block:: text

    strictdoc export docs/ --formats=html-standalone --output-dir output-html

The generated document are self-contained HTML pages that can be shared via
email as single files. This option might be especially useful if you work with
a single document instead of a documentation tree with multiple documents.

HTML export via Sphinx
----------------------

The following command creates an RST export:

.. code-block:: text

    strictdoc export YourDoc.sdoc --formats=rst --output-dir output

The created RST files can be copied to a project created using Sphinx, see
`Getting Started with Sphinx <https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html>`_.

.. code-block:: text

    cp -v output/YourDoc.rst docs/sphinx/source/
    cd docs/sphinx && make html

`StrictDoc's own Sphinx/HTML documentation
<https://strictdoc.readthedocs.io/en/latest/>`_
is generated this way, see the Invoke task:
`invoke sphinx <https://github.com/strictdoc-project/strictdoc/blob/5c94aab96da4ca21944774f44b2c88509be9636e/tasks.py#L48>`_.

PDF export via Sphinx/LaTeX
---------------------------


The following command creates an RST export:

.. code-block:: text

    strictdoc export YourDoc.sdoc --formats=rst --output-dir output

The created RST files can be copied to a project created using Sphinx, see
`Getting Started with Sphinx <https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html>`_.

.. code-block:: text

    cp -v output/YourDoc.rst docs/sphinx/source/
    cd docs/sphinx && make pdf

`StrictDoc's own Sphinx/PDF documentation
<https://strictdoc.readthedocs.io/_/downloads/en/latest/pdf/>`_
is generated this way, see the Invoke task:
`invoke sphinx <https://github.com/strictdoc-project/strictdoc/blob/5c94aab96da4ca21944774f44b2c88509be9636e/tasks.py#L48>`_.

Options
=======

Parallelization
---------------

To improve performance for the large document trees (1000+ requirements),
StrictDoc parallelizes reading and generation of the documents using
process-based parallelization: `multiprocessing.Pool` and
`multiprocessing.Queue`.

Parallelization improves performance but can also complicate understanding
behavior of the code if something goes wrong.

To disable parallelization use the `--no-parallelization` option:

.. code-block:: text

    strictdoc export --no-parallelization docs/

**Note:** Currently, only the generation of HTML documents is parallelized, so
this option will only have effect on the HTML export. All other export options
are run from the main thread. Reading of the SDoc documents is parallelized for
all export options and is disabled with this option as well.

StrictDoc and other tools
=========================

StrictDoc and Doorstop
----------------------

The StrictDoc project is a close successor of another project called
`Doorstop <https://github.com/doorstop-dev/doorstop>`_.

    Doorstop is a requirements management tool that facilitates the storage of
    textual requirements alongside source code in version control.

The author of Doorstop has published a `paper about Doorstop <http://www.scirp.org/journal/PaperInformation.aspx?PaperID=44268#.UzYtfWRdXEZ>`_
where the rationale behind text-based requirements management is provided.

The first version of StrictDoc had started as a fork of the Doorstop project.
However, after a while, the StrictDoc was started from scratch as a separate
project. At this point, StrictDoc and Doorstop do not share any code but
StrictDoc still shares with Doorstop their common underlying design principles:

- Both Doorstop and StrictDoc are written using Python. Both are pip packages which are easy-to-install.
- Both Doorstop and StrictDoc provide a command-line interface.
- Both Doorstop and StrictDoc use text files for requirements management.
- Both Doorstop and StrictDoc encourage collocation of code and documentation.
  When documentation is hosted close to code it has less chances of diverging
  from the actual implementation or becoming outdated.
- As the free and open source projects, both Doorstop and StrictDoc seem to
  struggle to find resources for development of specialized GUI interfaces this
  is why both tools give a preference to supporting exporting documentation
  pages to HTML format as the primary export feature.

StrictDoc differs from Doorstop in a number of aspects:

- Doorstop stores requirements in YAML files, one separate file per requirement
  (`example <https://github.com/doorstop-dev/doorstop/blob/804153c67c7c5466ee94e9553118cc3df03a56f9/reqs/REQ001.yml>`_).
  The document in Doorstop is assembled from the requirements files into a
  single logical document during the document generation process.
  StrictDoc's documentation unit is one document stored in an .sdoc file. Such a
  document can have multiple requirements grouped by sections.
- In YAML files, Doorstop stores requirements properties such as
  `normative: true` or `level: 2.3` for which Doorstop provides validations.
  Such a design decision, in fact, assumes an existence of implicitly-defined
  grammar which is encoded "ad-hoc" in the parsing and validation rules of
  Doorstop.
  StrictDoc takes a different approach and defines its grammar explicitly using
  a tool for creating Domain-Specific Languages called `textX <https://github.com/textX/textX>`_.
  TextX support allows StrictDoc to encode a strict type-safe grammar in a
  `single grammar file <https://github.com/strictdoc-project/strictdoc/blob/93486a0e9fb30b141187587eae9e995cd86c6cbf/strictdoc/backend/dsl/grammar.py>`_
  that StrictDoc uses to parse the documentation files
  using the parsing capabilities provided by textX out of the box.

The roadmap of StrictDoc contains a work item for supporting the export/import
to/from Doorstop format.

StrictDoc and Sphinx
--------------------

Both Sphinx and StrictDoc are both documentation generators but StrictDoc is at
a higher level of abstraction: StrictDoc's specialization is requirements and
specifications documents. StrictDoc can generate documentation to a number of
formats including HTML format as well as the RST format which is a default
input format for Sphinx. A two stage generation is therefore possible:
StrictDoc generates RST documentation which then can be generated to HTML, PDF,
and other formats using Sphinx.

If you are reading this documentation at
https://strictdoc.readthedocs.io/en/latest
then you are already looking at the example: this documentation stored in
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/master/docs/strictdoc.sdoc>`_
is converted to RST format by StrictDoc which is further converted to the HTML
website by readthedocs which uses Sphinx under the hood. The
`StrictDoc -> RST -> Sphinx -> PDF` example is also generated using readthedocs:
`StrictDoc <https://strictdoc.readthedocs.io/_/downloads/en/latest/pdf/>`_.

StrictDoc and Sphinx-Needs
--------------------------

`Sphinx-Needs <https://sphinxcontrib-needs.readthedocs.io/en/latest/>`_ is a
text-based requirements management system based on Sphinx. It is implemented
as a Sphinx extension that extends the
`reStructuredText (RST)
<https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_
markup language with additional syntax for writing requirements documents.

Sphinx-Needs was a great source of inspiration for the second version of
StrictDoc which was first implemented as a Sphinx extension and then as a more
independent library on top of `docutils <https://docutils.sourceforge.io/>`_
that Sphinx uses for the underlying RST syntax processing work.

The similarities between Sphinx-Needs and StrictDoc:

- In contrast to Doorstop, both Sphinx-Needs and StrictDoc do not split a
  document into many small files, one file per single requirement (see
  discussion
  `doorstop#401 <https://github.com/doorstop-dev/doorstop/issues/401>`_). Both
  tools follow the "file per document" approach.
- Sphinx-Needs has a
  `well-developed language
  <https://sphinxcontrib-needs.readthedocs.io/en/latest/directives/index.html>`_
  based on custom RST directives, such
  as `req::`, `spec::`, `needtable::`, etc. The RST document is parsed
  by Sphinx/docutils into RST abstract syntax tree (AST) which allows creating
  an object graph out for the documents and their requirements from the RST
  document. StrictDoc uses textX for building an AST from a SDoc document.
  Essentially, both Sphinx-Needs and StrictDoc works in a similar way but use
  different markup languages and tooling for the job.

The difference between Sphinx-Needs and StrictDoc:

- RST tooling provided by Sphinx/docutils is very powerful, yet it can also be
  rather limiting. The RST syntax and underlying docutils tooling do not allow
  much flexibility needed for creating a language for defining requirements
  using a custom and explicit grammar, a feature that became a cornerstone of
  StrictDoc. This was a major reason why the third generation of
  StrictDoc started with a migration from docutils to
  `textX <https://github.com/textX/textX>`_ which is a
  dedicated tool for creating custom Domain-Specific Languages. After the
  migration to textX, StrictDoc is no longer restricted to the limitations of
  the RST document, while it is still possible to generate SDoc files to RST
  using StrictDoc and then further generate RST to HTML/PDF and other formats
  using Sphinx.
- Sphinx-Needs has an impressive list of config options and features that
  StrictDoc is missing. Examples: Customizing the look of the requirements,
  `Roles <https://sphinxcontrib-needs.readthedocs.io/en/latest/roles.html>`_,
  `Services
  <https://sphinxcontrib-needs.readthedocs.io/en/latest/services/index.html>`_
  and
  `others
  <https://sphinxcontrib-needs.readthedocs.io/en/latest/index.html>`_.

StrictDoc Requirements
======================

Project goals
-------------

.. _GOAL-1-TOOL-SUPPORT:

Software support for writing requirements and specifications documents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - GOAL-1-TOOL-SUPPORT

There shall exist free and lightweight yet capable software for writing
requirements and specifications documents

**Comment:** Technical documentation is hard, it can be an extremely laborious process.
Software shall support engineers in their work with documentation.

**Comment:** The state of the art for many small companies working with
requirements: using Excel for requirements management in the projects with
hundreds or thousands of requirements.

**Children:**

- ``[SDOC-HIGH-REQS-MANAGEMENT]`` :ref:`SDOC-HIGH-REQS-MANAGEMENT`

.. _GOAL-2-REDUCE-DOCUMENTATION-HAZARDS:

Reduce documentation hazards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - GOAL-2-REDUCE-DOCUMENTATION-HAZARDS

There shall exist no (or less) opportunity for writing incorrect or inconsistent
documentation.

**Comment:** Every serious engineering activity, such as safety engineering or systems
engineering, starts with requirements. The more critical is a product the higher
the importance of good documentation.

Technical documentation can be and often becomes a source of hazards.
It is recognized that many failures stem from inadequate requirements
engineering. While it is not possible to fix the problem of inadequate
requirements engineering in general, it is definitely possible to improve
software that supports engineers in activities such as requirements engineering
and writing technical documentation.

.. _GOAL-3-NO-RUNAWAY-DOCUMENTATION:

No (or less) run-away documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - GOAL-3-NO-RUNAWAY-DOCUMENTATION

Software shall support engineers in keeping documentation up-to-date.

**Comment:** Technical documentation easily becomes outdated. Many existing tools for
documentation do not provide any measures for ensuring overall consistency of
documents and documentation trees.

.. _GOAL-4-CHANGE-MANAGEMENT:

Change management
~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - GOAL-4-CHANGE-MANAGEMENT

Software shall provide capabilities for change management and impact assessment.

**Comment:** Change management is difficult. The bigger the project is, the harder it is to
maintain its documentation. If a change is introduced to a project, it usually
requires a full revision of its requirements TBD.

High-level requirements
-----------------------

.. _SDOC-HIGH-REQS-MANAGEMENT:

Requirements management
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-REQS-MANAGEMENT

StrictDoc shall enable requirements management.

**Parents:**

- ``[GOAL-1-TOOL-SUPPORT]`` :ref:`GOAL-1-TOOL-SUPPORT`

**Children:**

- ``[SDOC-DM-001]`` :ref:`SDOC-DM-001`

.. _SDOC-HIGH-DATA-MODEL:

Data model
~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-DATA-MODEL

StrictDoc shall be based on a well-defined data model.

**Comment:** StrictDoc is a result of multiple attempts to find a solution for working with
text-based requirements:

- StrictDoc, first generation: Markdown-based C++ program. Custom requirements
  metadata in YAML.
- StrictDoc, second generation: RST/Sphinx-based Python program. Using Sphinx
  extensions to manage meta information.

The result of these efforts is the realization that a text-based requirements
and specifications management tool TBD.

Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall provide a command-line interface.

Platform support
~~~~~~~~~~~~~~~~

StrictDoc shall work on all major platforms.

macOS support
^^^^^^^^^^^^^

StrictDoc shall work on macOS systems.

Linux support
^^^^^^^^^^^^^

StrictDoc shall work on Linux systems.

Windows support
^^^^^^^^^^^^^^^

StrictDoc shall work on Windows systems.

Requirements validation
~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall allow validation of requirement documents.

Requirements text format
~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall allow storage of requirements in a plain-text human readable form.

Linking requirements
~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support linking requirements to each other.

Scalability
~~~~~~~~~~~

StrictDoc shall allow working with large documents and document trees containing at least 10000 requirement items.

.. _SDOC-HIGH-REQS-TRACEABILITY:

Traceability
~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-REQS-TRACEABILITY

StrictDoc shall support traceability of requirements.

Visualization
~~~~~~~~~~~~~

StrictDoc shall provide means for visualization of requirement documents.

Open source software
~~~~~~~~~~~~~~~~~~~~

StrictDoc shall always be free and open source software.

Implementation requirements
---------------------------

.. _SDOC-IMPL-PARAL:

Parallelization
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-IMPL-PARAL

StrictDoc shall enable parallelization of the time-consuming parts of the code.

.. _SDOC-IMPL-INCREMENTAL:

Incremental generation
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-IMPL-INCREMENTAL

StrictDoc shall enable incremental generation of the documents.

**Comment:** When exporting documentation tree, StrictDoc shall regenerate only changed
documents and files.

Data model
----------

.. _SDOC-DM-001:

Modeling capability
~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-DM-001

StrictDoc's Data Model shall accommodate for maximum possible standard requirement document formats.

**Comment:** Examples of standard requirements documents include but are not limited to:

- Non-nested requirement lists split by categories
  (e.g., Functional Requirements, Interface Requirements, Performance Requirements, etc.)

**Parents:**

- ``[SDOC-HIGH-REQS-MANAGEMENT]`` :ref:`SDOC-HIGH-REQS-MANAGEMENT`

**Children:**

- ``[SDOC-FMT-001]`` :ref:`SDOC-FMT-001`

Section item
~~~~~~~~~~~~

Requirement item
~~~~~~~~~~~~~~~~

Statement
^^^^^^^^^

Requirement item shall have a statement.

Content body
^^^^^^^^^^^^

Requirement item might have an content body.

UID identifier
^^^^^^^^^^^^^^

Requirement item might have an UID identifier.

UID identifier format
"""""""""""""""""""""

StrictDoc shall not impose any restrictions on the UID field format.

**Comment:** Conventions used for requirement UIDs can be very different. And there seems to
be no way to define a single rule.

Some examples:

- FUN-003
- cES1008, cTBL6000.1 (NASA cFS)
- Requirements without a number, e.g. SDOC-HIGH-DATA-MODEL (StrictDoc)
- SAVOIR.OBC.PM.80 (SAVOIR)

Title
^^^^^

Requirement item might have an title.

References
^^^^^^^^^^

Requirement item might have one or more references.

Comments
^^^^^^^^

Requirement item might have one or more comments.

Special fields
^^^^^^^^^^^^^^

StrictDoc shall support customization of the default Requirement's grammar with special fields.

**Comment:** Examples:

- RAIT compliance fields (Review of design, analysis, inspection, testing)
- Automotive Safety Integrity Level level (ASIL).

Composite Requirement item
~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

Links
~~~~~

StrictDoc's data model shall support linking document content nodes to each other.

Parent links
^^^^^^^^^^^^

StrictDoc's data model shall support linking a requirement to another requirement using PARENT link.

SDOC file format
----------------

.. _SDOC-FMT-001:

Primary text implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-FMT-001

SDOC format shall support encoding the Strict Doc Data Model in a plain-text human readable form.

**Parents:**

- ``[SDOC-DM-001]`` :ref:`SDOC-DM-001`

Grammar
~~~~~~~

SDOC format shall be based on a fixed grammar.

Type safety
~~~~~~~~~~~

SDOC format shall allow type-safe encoding of requirement documents.

Document Generators
-------------------

HTML Export
~~~~~~~~~~~

Single document: Normal form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export single document pages in a normal document-like form.

Single document: Tabular form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export single document pages in a tabular form.

Single document: 1-level traceability
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export 1-level traceability document.

**Parents:**

- ``[SDOC-HIGH-REQS-TRACEABILITY]`` :ref:`SDOC-HIGH-REQS-TRACEABILITY`

Single document: Deep traceability
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export deep traceability document.

**Parents:**

- ``[SDOC-HIGH-REQS-TRACEABILITY]`` :ref:`SDOC-HIGH-REQS-TRACEABILITY`

Left panel: Table of contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export all HTML pages with Table of Contents.

PDF Export
~~~~~~~~~~

Sphinx documentation generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support exporting documents to Sphinx/RST format.

Excel Export
~~~~~~~~~~~~

StrictDoc shall support exporting documents to Excel format.

Validation requirements
-----------------------

Valid HTML markup
~~~~~~~~~~~~~~~~~

StrictDoc's HTML export tests shall validate the generated HTML markup.

**Comment:** First candidate: Table of contents and its nested ``<ul>/<li>`` items.

Design decisions
================

Building blocks
---------------

TextX
~~~~~

TextX shall be used for StrictDoc grammar definition and parsing of the sdoc files.

**Comment:** TextX is an easy-to-install Python tool. It is fast, works out of the box.

Jinja2
~~~~~~

Jinja2 shall be used for rendering HTML templates.

Sphinx and Docutils
~~~~~~~~~~~~~~~~~~~

Sphinx and Docutils shall be used for the following capabilities:

- Support of Restructured Text (reST) format
- Generation of RST documents into HTML
- Generation of RST documents into PDF using LaTeX
- Generating documentation websites using Sphinx

SDoc grammar
------------

No indentation
~~~~~~~~~~~~~~

SDoc grammar's building blocks shall not allow any indentation.

**Comment:** Rationale: Adding indentation to any of the fields does not scale well when the
documents have deeply nested section structure as well as when the size of the
paragraphs becomes sufficiently large. Keeping every keyword like [REQUIREMENT]
or [COMMENT] with no indentation ensures that one does not have to think about
possible indentation issues.

Roadmap
=======

First public release
--------------------

Generated file names
~~~~~~~~~~~~~~~~~~~~

Document name must be transformed into a valid file name.

**Comment:** Alternative: Simply use the original document file names.

Validation: Uniqueness of UID identifiers in a document tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall ensure that each UID used in a document tree is unique.

Backlog
-------

StrictDoc as library
~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support it use as a Python library.

**Comment:** Such a use allows a more fine-grained access to the StrictDoc's modules, such
as Grammar, Import, Export classes, etc.

Export capabilities
~~~~~~~~~~~~~~~~~~~

CSV Import/Export
^^^^^^^^^^^^^^^^^

StrictDoc shall support exporting documents to CSV format.

PlantUML Export
^^^^^^^^^^^^^^^

StrictDoc shall support exporting documents to PlantUML format.

ReqIF Import/Export
^^^^^^^^^^^^^^^^^^^

StrictDoc shall support ReqIF format.

Confluence Import/Export
^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support importing/exporting documents from/to Confluence HTML storage format.

Tex Export
^^^^^^^^^^

StrictDoc shall support exporting documents to Tex format.

Doorstop Import/Export
^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support import and exporting documents from/to Doorstop format.

Markdown support for text and code blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support rendering text/code blocks into RST syntax.

Traceability and coverage
~~~~~~~~~~~~~~~~~~~~~~~~~

Linking with implementation artifacts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support linking requirements to files.

Requirement checksumming
^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support calculation of checksums for requirements.

Documentation coverage
^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall generate requirements coverage information.

Validations and testing
~~~~~~~~~~~~~~~~~~~~~~~

Validation: Section Levels
^^^^^^^^^^^^^^^^^^^^^^^^^^

Section levels must be properly nested.

Filtering by tags
~~~~~~~~~~~~~~~~~

StrictDoc shall support filtering filtering by tags.

Options
~~~~~~~

Option: RST: Top-level title: document name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support config option `include_toplevel_title`.

Option: Title: Automatic numeration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support config option `numeric_titles`.

Option: Title: Display requirement titles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support config option `display_requirement_titles`.

Option: Title: Display requirement UID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support config option `display_requirement_uids`.

Advanced
~~~~~~~~

Facts table. Invariants calculation.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support creation of fact tables calculating invariants that
enforce numerical constraints.

FMEA/FMECA tables
^^^^^^^^^^^^^^^^^

StrictDoc shall support creation of FMEA/FMECA safety analysis documents.

Graphical User Interface (GUI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall provide a Graphical User Interface (GUI).

Web server and editable HTML pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall provide a web server that serves as a StrictDoc backend for
reading and writing SDoc files.



