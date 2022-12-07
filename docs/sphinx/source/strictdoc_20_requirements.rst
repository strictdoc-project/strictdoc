Requirements
$$$$$$$$$$$$

High-level requirements
=======================

.. _SDOC-HIGH-REQS-MANAGEMENT:

Requirements management
-----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-REQS-MANAGEMENT

StrictDoc shall enable requirements management.

**Parents:**

- ``[GOAL-1-TOOL-SUPPORT]`` :ref:`GOAL-1-TOOL-SUPPORT`

**Children:**

- ``[SDOC-DM-MODEL]`` :ref:`SDOC-DM-MODEL`

.. _SDOC-HIGH-DATA-MODEL:

Data model
----------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-DATA-MODEL

StrictDoc shall be based on a well-defined data model.

**Comment:** StrictDoc is a result of several attempts to find a solution for working with
text-based requirements:

- StrictDoc, first generation: Markdown-based C++ program. Custom requirements
  metadata in YAML.
- StrictDoc, second generation: RST/Sphinx-based Python program. Using Sphinx
  extensions to manage meta information.

The result of these efforts was the realization that a text-based requirements
and specifications management tool could be built on top of a domain-specific
language (DSL) created specifically for the purpose of writing requirements and
specifications documents. Such a language allows an explicit definition of a
document data model which is called "grammar".

**Children:**

- ``[SDOC-DM-MODEL]`` :ref:`SDOC-DM-MODEL`
- ``[SDOC-FMT-GRAMMAR]`` :ref:`SDOC-FMT-GRAMMAR`

Command-line interface
----------------------

StrictDoc shall provide a command-line interface.

Graphical user interface
------------------------

StrictDoc shall provide a Graphical User Interface (GUI).

Several trade-offs to consider:

- Desktop vs Web. Rather web-based, i.e. Python backend and JS frontend, but which technology?
- Still keep the current behavior of a statically generated website?


Statically generated website
----------------------------

StrictDoc shall allow generating requirements content to static HTML website.

Platform support
----------------

StrictDoc shall work on all major platforms.

macOS support
~~~~~~~~~~~~~

StrictDoc shall work on macOS systems.

Linux support
~~~~~~~~~~~~~

StrictDoc shall work on Linux systems.

Windows support
~~~~~~~~~~~~~~~

StrictDoc shall work on Windows systems.

.. _SDOC-HIGH-VALIDATION:

Requirements validation
-----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-VALIDATION

StrictDoc shall allow validation of requirement documents.

**Children:**

- ``[SDOC-VALIDATION-UNIQUE-UID]`` :ref:`SDOC-VALIDATION-UNIQUE-UID`
- ``[SDOC-VALIDATION-NO-CYCLES]`` :ref:`SDOC-VALIDATION-NO-CYCLES`
- ``[SDOC-VALIDATION-VALID-HTML]`` :ref:`SDOC-VALIDATION-VALID-HTML`

Requirements text format
------------------------

StrictDoc shall allow storage of requirements in a plain-text human readable form.

Linking requirements
--------------------

StrictDoc shall support linking requirements to each other.

Scalability
-----------

StrictDoc shall allow working with large documents and document trees containing at least 10000 requirement items.

.. _SDOC-HIGH-REQS-TRACEABILITY:

Traceability
------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-REQS-TRACEABILITY

StrictDoc shall support traceability of requirements.

Visualization
-------------

StrictDoc shall provide means for visualization of requirement documents.

Open source software
--------------------

StrictDoc shall always be free and open source software.

Implementation requirements
===========================

.. _SDOC-IMPL-PARAL:

Parallelization
---------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-IMPL-PARAL

StrictDoc shall enable parallelization of the time-consuming parts of the code.

.. _SDOC-IMPL-INCREMENTAL:

Incremental generation
----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-IMPL-INCREMENTAL

StrictDoc shall enable incremental generation of the documents.

**Comment:** When exporting documentation tree, StrictDoc shall regenerate only changed
documents and files.

Data model
==========

.. _SDOC-DM-MODEL:

Modeling capability
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-DM-MODEL

StrictDoc's Data Model shall accommodate for maximum possible standard requirement document formats.

**Comment:** Examples of standard requirements documents include but are not limited to:

- Non-nested requirement lists split by categories
  (e.g., Functional Requirements, Interface Requirements, Performance Requirements, etc.)

**Parents:**

- ``[SDOC-HIGH-REQS-MANAGEMENT]`` :ref:`SDOC-HIGH-REQS-MANAGEMENT`
- ``[SDOC-HIGH-DATA-MODEL]`` :ref:`SDOC-HIGH-DATA-MODEL`

**Children:**

- ``[SDOC-FMT-PRIMARY]`` :ref:`SDOC-FMT-PRIMARY`

Project
-------

StrictDoc shall support the "Project" concept as a top-level entity that serves
for grouping of SDoc documents into a single project documentation tree.

Project title
~~~~~~~~~~~~~

Project shall have a "Title" property.

**Comment:** Currently, the project title aspect is not part of the SDoc grammar. It is
simply specified via the ``--project-title`` command-line option. This might
change when the project title will be configured as part of the project-level
config file (TOML or SDoc-like grammar).

Document
--------

TBD

Section
-------

TBD

Requirement item
----------------

Statement
~~~~~~~~~

Requirement item shall have a statement.

UID identifier
~~~~~~~~~~~~~~

Requirement item may have an UID identifier.

UID identifier format
^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall not impose any restrictions on the UID field format.

**Comment:** Conventions used for requirement UIDs can be very different. And there seems to
be no way to define a single rule.

Some examples:

- FUN-003
- cES1008, cTBL6000.1 (NASA cFS)
- Requirements without a number, e.g. SDOC-HIGH-DATA-MODEL (StrictDoc)
- SAVOIR.OBC.PM.80 (SAVOIR)

Title
~~~~~

Requirement item may have an title.

References
~~~~~~~~~~

Requirement item may have one or more references.

Comments
~~~~~~~~

Requirement item may have one or more comments.

Special fields
~~~~~~~~~~~~~~

StrictDoc shall support customization of the default Requirement's grammar with special fields.

**Comment:** Examples:

- RAIT compliance fields (Review of design, analysis, inspection, testing)
- Automotive Safety Integrity Level level (ASIL).

Composite Requirement item
--------------------------

TBD

Links
-----

StrictDoc's data model shall support linking document content nodes to each other.

Parent links
~~~~~~~~~~~~

StrictDoc's data model shall support linking a requirement to another requirement using PARENT link.

SDoc file format
================

.. _SDOC-FMT-PRIMARY:

Primary text implementation
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-FMT-PRIMARY

The SDoc format shall support encoding the Strict Doc Data Model in a plain-text human readable form.

**Parents:**

- ``[SDOC-DM-MODEL]`` :ref:`SDOC-DM-MODEL`

.. _SDOC-FMT-GRAMMAR:

Grammar
-------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-FMT-GRAMMAR

The SDoc format shall be based on a fixed grammar.

**Parents:**

- ``[SDOC-HIGH-DATA-MODEL]`` :ref:`SDOC-HIGH-DATA-MODEL`

No indentation
~~~~~~~~~~~~~~

The SDoc grammar's building blocks shall not allow any indentation.

**Comment:** Rationale: Adding indentation to any of the fields does not scale well when the
documents have deeply nested section structure as well as when the size of the
paragraphs becomes sufficiently large. Keeping every keyword like [REQUIREMENT]
or [COMMENT] with no indentation ensures that one does not have to think about
possible indentation issues.

Type safety
-----------

The SDoc format shall allow type-safe encoding of requirement documents.

Export and import capabilities
==============================

General
-------

Generated file names
~~~~~~~~~~~~~~~~~~~~

StrictDoc shall preserve original document file names when generating to all
export formats.

HTML Export
-----------

Single document: Normal form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall export single document pages in a normal document-like form.

Single document: Tabular form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall export single document pages in a tabular form.

Single document: 1-level traceability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall export 1-level traceability document.

**Parents:**

- ``[SDOC-HIGH-REQS-TRACEABILITY]`` :ref:`SDOC-HIGH-REQS-TRACEABILITY`

Single document: Deep traceability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall export deep traceability document.

**Parents:**

- ``[SDOC-HIGH-REQS-TRACEABILITY]`` :ref:`SDOC-HIGH-REQS-TRACEABILITY`

Left panel: Table of contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall export all HTML pages with Table of Contents.

PDF Export
----------

Sphinx documentation generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support exporting documents to Sphinx/RST format.

.. _SDOC-GEN-EXCEL-EXPORT:

Excel Export
------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-GEN-EXCEL-EXPORT

StrictDoc shall support exporting documents to Excel format.

ReqIF import/export
-------------------

StrictDoc shall support the ReqIF format.

Validation
==========

.. _SDOC-VALIDATION-UNIQUE-UID:

Uniqueness of UID identifiers in a document tree
------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-VALIDATION-UNIQUE-UID

StrictDoc shall ensure that each UID used in a document tree is unique.

**Comment:** This is implemented but the error message shall be made more readable.

**Parents:**

- ``[SDOC-HIGH-VALIDATION]`` :ref:`SDOC-HIGH-VALIDATION`

.. _SDOC-VALIDATION-NO-CYCLES:

No cycles in a document tree
----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-VALIDATION-NO-CYCLES

StrictDoc shall ensure that no requirements in document tree reference each other.

**Parents:**

- ``[SDOC-HIGH-VALIDATION]`` :ref:`SDOC-HIGH-VALIDATION`

.. _SDOC-VALIDATION-VALID-HTML:

Valid HTML markup
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-VALIDATION-VALID-HTML

StrictDoc's HTML export tests shall validate the generated HTML markup.

**Comment:** First candidate: Table of contents and its nested ``<ul>/<li>`` items.

**Parents:**

- ``[SDOC-HIGH-VALIDATION]`` :ref:`SDOC-HIGH-VALIDATION`

Traceability and coverage
=========================

Linking with implementation artifacts
-------------------------------------

StrictDoc shall support linking requirements to files.

Validation: Broken links from requirements to source files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall warn a user about all requirements whose links reference source
files that do not exist.

Validation: Broken links from source files to requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall warn a user about all source files whose links reference
requirements that do not exist.

Requirements coverage
---------------------

StrictDoc shall generate requirements coverage information.

**Comment:** Requirements coverage screen shows how requirements are linked with source files.

Source coverage
---------------

StrictDoc shall generate source coverage information.

**Comment:** Source coverage screen shows how source files are linked with requirements.

Web frontend requirements
=========================

AJAX updates of multiple web forms
----------------------------------

StrictDoc's Web GUI shall provide capability to do multipart updates.

