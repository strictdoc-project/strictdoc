StrictDoc
$$$$$$$$$

StrictDoc is software for writing technical requirements and specifications.

Summary of StrictDoc features:

- The documentation files are stored as human-readable text files.
- A simple domain-specific language DSL is used for writing the documents. The
  text format encoding this language is called SDoc (strict-doc).
- StrictDoc reads `*.sdoc` files and builds an in-memory representation of the
  document tree.
- From this in-memory representation, StrictDoc can generate the documentation
  into a number of formats including HTML, RST, and PDF.
- The initial focus of the tool is modeling requirements and specifications
  documents. Such documents consist of multiple statements like
  "system X shall do Y" called requirements.
- The requirements can be linked together to form the relationships, such as
  "parent-child", and from these connections, many useful features such as
  `Requirements Traceability <https://en.wikipedia.org/wiki/Requirements_traceability>`_
  and Documentation Coverage can be derived.

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

    strictdoc export docs/ --output-dir output-html

Example: This documentation is exported by StrictDoc to HTML:
`StrictDoc HTML export <https://strictdoc.readthedocs.io/en/latest/strictdoc-html>`_.

HTML export via Sphinx
----------------------

TBD

PDF export via Sphinx/Latex
---------------------------

TBD

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

TBD

StrictDoc Requirements
======================

Project goals
-------------

Software support for writing requirements and specifications documents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[GOAL-1-TOOL-SUPPORT]``

There shall exist free and lightweight yet capable software for writing
requirements and specifications documents

**Comment:** Technical documentation is hard, it can be an extremely laborious process.
Software shall support engineers in their work with documentation.

**Comment:** The state of the art for many small companies working with
requirements: using Excel for requirements management in the projects with
hundreds or thousands of requirements.

Reduce documentation hazards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[GOAL-2-REDUCE-DOCUMENTATION-HAZARDS]``

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

No (or less) run-away documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[GOAL-3-NO-RUNAWAY-DOCUMENTATION]``

Software shall support engineers in keeping documentation up-to-date.

**Comment:** Technical documentation easily becomes outdated. Many existing tools for
documentation do not provide any measures for ensuring overall consistency of
documents and documentation trees.

Change management
~~~~~~~~~~~~~~~~~

``[GOAL-4-CHANGE-MANAGEMENT]``

Software shall provide capabilities for change management and impact assessment.

**Comment:** Change management is difficult. The bigger the project is, the harder it is to
maintain its documentation. If a change is introduced to a project, it usually
requires a full revision of its requirements TBD.

High-level requirements
-----------------------

Requirements management
~~~~~~~~~~~~~~~~~~~~~~~

``[SDOC-HIGH-REQS-MANAGEMENT]``

StrictDoc shall enable requirements management.

Data model
~~~~~~~~~~

``[SDOC-HIGH-DATA-MODEL]``

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

Traceability
~~~~~~~~~~~~

``[SDOC-HIGH-REQS-TRACEABILITY]``

StrictDoc shall support traceability of requirements.

Visualization
~~~~~~~~~~~~~

StrictDoc shall provide means for visualization of requirement documents.

Open source software
~~~~~~~~~~~~~~~~~~~~

StrictDoc shall always be free and open source software.

Implementation requirements
---------------------------

Parallelization
~~~~~~~~~~~~~~~

``[SDOC-IMPL-PARAL]``

StrictDoc shall enable parallelization of the time-consuming parts of the code.

Incremental generation
~~~~~~~~~~~~~~~~~~~~~~

``[SDOC-IMPL-INCREMENTAL]``

StrictDoc shall enable incremental generation of the documents.

**Comment:** When exporting documentation tree, StrictDoc shall regenerate only changed
documents and files.

Data model
----------

Modeling capability
~~~~~~~~~~~~~~~~~~~

``[SDOC-DM-001]``

StrictDoc's Data Model shall accommodate for maximum possible standard requirement document formats.


Examples of standard requirements documents include but are not limited to:

- Non-nested requirement lists split by categories
  (e.g., Functional Requirements, Interface Requirements, Performance Requirements, etc.)

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

Composite Requirement item
~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

SDOC file format
----------------

Primary text implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[SDOC-FMT-001]``

SDOC format shall support encoding the Strict Doc Data Model in a plain-text human readable form.

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

Single document: Deep traceability
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export deep traceability document.

PDF Export
~~~~~~~~~~

Sphinx documentation generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support exporting documents to Sphinx/RST format.

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
- Generation of RST documents into PDF using Latex
- Generating documentation websites using Sphinx

SDoc grammar
------------

No indentation
~~~~~~~~~~~~~~

SDoc grammar building blocks shall not allow any indentation.

**Comment:** Rationale: Adding indentation to any of the fields does not scale well when the
documents have deeply nested section structure as well as when the size of the
paragraphs becomes sufficiently large. Keeping every keyword like [REQUIREMENT]
or [COMMENT] with no indentation ensures that one does not have to think about
possible indentation issues.

Roadmap
=======

In works
--------

HTML Export
~~~~~~~~~~~

Left panel: Table of contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Left panel: Table of contents.

Document page CSS: Proper markup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Document page: make it look like a document.

Table page CSS: Proper table
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Table page: make columns be always of the same size while respecting min-max widths.

Traceability page CSS: Proper middle column document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Traceability page CSS: Proper middle column document

Deep Traceability page CSS: Improvements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deep Traceability page CSS: Improvements

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

Links
~~~~~

StrictDoc's data model shall support linking document content nodes to each other.

**Comment:** Examples:
- Link that references a section

Export capabilities
~~~~~~~~~~~~~~~~~~~

Excel Export
^^^^^^^^^^^^

StrictDoc shall support exporting documents to Excel format.

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

Custom fields
~~~~~~~~~~~~~

StrictDoc shall support customization of the default grammar with custom fields.

**Comment:** Examples:

- RAIT compliance fields (Review of design, analysis, inspection, testing)
- Automotive Safety Integrity Level level (ASIL).

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

