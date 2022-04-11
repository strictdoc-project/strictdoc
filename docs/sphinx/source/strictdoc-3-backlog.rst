StrictDoc Backlog
$$$$$$$$$$$$$$$$$

**Note:** The items below are weakly sorted from top to bottom. The topmost
items are either work-in-progress or will be implemented next.

Work in progress
================

Integration with Capella
------------------------

StrictDoc shall allow bi-directional data exchange with Capella tool.

**Comment:** The current plan is to implement this using ReqIF export/import features.

SDoc Language Server Protocol
=============================

StrictDoc shall support Language Server Protocol.

**Comment:** The promising base for the implementation: https://github.com/openlawlibrary/pygls.

Document archetypes
===================

StrictDoc shall support the following document archetypes: **requirements document**
and **specification** document. For both archetypes, StrictDoc shall further
support the following options.

.. list-table:: Table: Requirements and specification document
   :widths: 20 40 40
   :header-rows: 1

   * -
     - Requirements document
     - Specification document
   * - Examples
     - Most typical: requirements lists split by categories (e.g., Functional
       Requirements, Interface Requirements, Performance Requirements, etc.)
     - Often: a standard document
   * - Structure
     - Not nested or not too deeply nested
     - Nested
   * - Visual presentation
     - Requirements are often presented as table cells. Cells can be standalone
       or the whole section or document can be a long table with cells.
     - Requirements are rather presented as header + text
   * - Unique requirement identifiers (UID)
     - Most always
     - - Present or not
       - **NOT SUPPORTED YET:** Can be missing, the chapter headers are used instead.
         The combination "Number + Title" becomes a reference-able identifier.
         A possible intermediate solution when modeling such a document is to
         make the UIDs map to the section number.
   * - Requirement titles
     - - Often
       - **NOT SUPPORTED YET:** But maybe absent (ex: NASA cFS SCH). If absent,
         the grouping is provided by sections.
     - Requirement titles are most often section titles
   * - Real-world examples
     - - NASA cFE Functional Requirements
       - MISRA C coding guidelines,
       - NASA Software Engineering Requirements NPR 7150.2
     - - ECSS Software ECSS-E-ST-40C

**Comment:** This draft requirement is the first attempt to organize this information.

Project-level configuration file
================================

StrictDoc shall support reading project configuration from a file.

**Comment:** - TOML format looks like a good option.

- Project title.

- Project prefix?

- Explicit or wildcard paths to sdoc files.

- Paths to dirs with source files.

- Config options for presenting requirements.

  - Include/exclude requirements in TOC

Further export and import capabilities
======================================

CSV import/export
-----------------

StrictDoc shall support exporting documents to CSV format.

PlantUML export
---------------

StrictDoc shall support exporting documents to PlantUML format.

Confluence import/export
------------------------

StrictDoc shall support importing/exporting documents from/to Confluence HTML storage format.

Tex export
----------

StrictDoc shall support exporting documents to Tex format.

Doorstop import/export
----------------------

StrictDoc shall support import and exporting documents from/to
`Doorstop <https://github.com/doorstop-dev/doorstop>`_ format.

Markdown support for text and code blocks
=========================================

StrictDoc shall support rendering text/code blocks into Markdown syntax.

StrictDoc as library
====================

StrictDoc shall support it use as a Python library.

**Comment:** Such a use allows a more fine-grained access to the StrictDoc's modules, such
as Grammar, Import, Export classes, etc.

.. _BACKLOG-FUZZY-SEARCH:

Fuzzy requirements search
=========================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - BACKLOG-FUZZY-SEARCH

StrictDoc shall support finding relevant requirements.

**Comment:** This feature can be implemented in the CLI as well as in the future GUI. A fuzzy
requirements search can help to find existing requirements and also identify
relevant requirements when creating new requirements.

**Parents:**

- ``[GOAL-4-CHANGE-MANAGEMENT]`` :ref:`GOAL-4-CHANGE-MANAGEMENT`

Filtering by tags
=================

StrictDoc shall support filtering filtering by tags.

Advanced
========

Requirement checksumming
------------------------

StrictDoc shall support calculation of checksums for requirements.

**Comment:** This feature is relatively easy to implement but the implementation is postponed
until the linking between requirements and files is implemented.

Graphical User Interface (GUI)
------------------------------

StrictDoc shall provide a Graphical User Interface (GUI).

**Comment:** Several trade-offs to consider:

- Desktop vs Web. Rather web-based, i.e. Python backend and JS frontend, but
  which technology?
- Still keep the current behavior of a statically generated website?

Web server and editable HTML pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall provide a web server that serves as a StrictDoc backend for
reading and writing SDoc files.

Facts table. Invariants calculation.
------------------------------------

StrictDoc shall support creation of fact tables and allow calculation of
invariants for constraints enforcement.

FMEA/FMECA tables
-----------------

StrictDoc shall support creation of FMEA/FMECA safety analysis documents.

Open questions
==============

One or many input sdoc trees
----------------------------

StrictDoc supports this for HTML already but not for RST.

When passed
``strictdoc export ... /path/to/doctree1, /path/to/doctree2, /path/to/doctree3``,
the following is generated:

.. code-block:: text

    output folder:
    - doctree1/
      - contents
    - doctree2/
      - contents
    - doctree3/
      - contents

and all three doctrees' requirements are merged into a single documentation
space with cross-linking possible.

The question is if it is worth supporting this case further or StrictDoc should
only work with one input folder with a single doc tree.

