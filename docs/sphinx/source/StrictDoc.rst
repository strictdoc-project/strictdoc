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

Examples
========

"Hello World" example:

.. code-block::

    [DOCUMENT]
    NAME: StrictDoc

    [REQUIREMENT]
    UID: SDOC-HIGH-REQS-MANAGEMENT
    TITLE: Requirements management
    STATEMENT: StrictDoc shall enable requirements management.

For a more comprehensive example check the source file of this documentation
itself which is written using StrictDoc:
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/master/docs/strictdoc.sdoc>`_.

Getting started
===============

Installing StrictDoc as a Pip package
-------------------------------------

.. code-block:: text

    pip install strictdoc

Installing StrictDoc from GitHub (development)
----------------------------------------------

.. code-block:: text

    git clone git@github.com:stanislaw/strictdoc.git && cd strictdoc
    poetry install
    poetry run strictdoc

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

The source file of this documentation itself which is written using StrictDoc:
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/master/docs/strictdoc.sdoc>`_.

Export options
==============

HTML documentation tree by StrictDoc
------------------------------------

TBD

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

    "Doorstop is a requirements management tool that facilitates the storage of
    textual requirements alongside source code in version control."

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

TBD

StrictDoc and Sphinx-Needs
--------------------------

TBD

StrictDoc Requirements
======================

Problems
--------

Technical documentation software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[PROBLEM-1-TOOLS]``

There shall exist free and lightweight yet capable software for technical
documentation.

**Comment:** The state of the art for many small companies working with
requirements: using Excel for requirements management in the projects with
hundreds or thousands of requirements.

Technical documentation is hard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[PROBLEM-2-DOCUMENTATION-IS-HARD]``

Software shall support engineers in their work with documentation.

**Comment:** Technical documentation can be an extremely laborious process.

Technical documentation as a source of hazards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[PROBLEM-3-DOCUMENTATION-AS-HAZARD]``

There shall exist no (or less) opportunity for writing incorrect documentation.

**Comment:** Every serious engineering activity, such as safety engineering or systems
engineering, starts with requirements. The more critical is a product the higher
the importance of good documentation.

It is recognized that many failures stem from inadequate requirements
engineering. While it is not possible to fix the problem of inadequate
requirements engineering in general, it is definitely possible to improve
software that supports engineers in activities such as requirements engineering
and writing technical documentation.

Technical documentation easily becomes outdated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[PROBLEM-4-OUTDATED-DOCUMENTATION]``

Software shall support engineers in keeping documentation up-to-date.

**Comment:** Many existing tools for documentation do not provide any measures for
ensuring overall consistency of documents and documentation trees.

Change management is difficult
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``[PROBLEM-5-CHANGE-MANAGEMENT]``

Software shall provide capabilities for change management and impact assessment.

**Comment:** The bigger the project is, the harder it is to maintain its documentation.
If a change is introduced to a project, it usually requires a full revision
of its requirements TBD.

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

Design decisions
================

TextX
-----

TextX shall be used for StrictDoc grammar definition and parsing of the sdoc files.

**Comment:** TextX is an easy-to-install Python tool. It is fast, works out of the box.

Jinja2
------

Jinja2 shall be used for rendering HTML templates.

Sphinx and Docutils
-------------------

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

PDF Export
~~~~~~~~~~

PDF Export: TOC sections: bottom alignment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Numbers do not align with titles.

HTML Export
~~~~~~~~~~~

RST support for text and code blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support rendering text/code blocks into RST syntax.

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

Document tree: Incremental generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When exporting documentation tree, StrictDoc shall regenerate only changed documents and files.

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

Excel Export
^^^^^^^^^^^^

StrictDoc shall support exporting documents to Excel format.

PlantUML Export
^^^^^^^^^^^^^^^

StrictDoc shall support exporting documents to ReqIF format.

ReqIF Import/Export
^^^^^^^^^^^^^^^^^^^

StrictDoc shall support ReqIF format.

Tex Export
^^^^^^^^^^

StrictDoc shall support exporting documents to Tex format.

Markdown support for text and code blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support rendering text/code blocks into RST syntax.

Platform support
~~~~~~~~~~~~~~~~

Linux support
^^^^^^^^^^^^^

StrictDoc shall work on Linux systems.

Windows support
^^^^^^^^^^^^^^^

StrictDoc shall work on Windows systems.

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

Validation: Valid HTML markup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc's HTML export tests shall validate the generated HTML markup.

**Comment:** First candidate: Table of contents and its nested ``<ul>/<li>`` items.

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

StrictDoc shall support creation of fact tables calculating invariants that enforce numerical constraints.

Graphical User Interface (GUI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall provide a Graphical User Interface (GUI).

