StrictDoc Requirements Specification (L2)
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

SDoc data model
===============

.. _SDOC-SRS-18:

Data model
----------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-18
    * - **STATUS:**
      - Active

StrictDoc shall be based on a data model.

**RATIONALE:**

Designing StrictDoc with a goal of having a consistent data model ensures that the tool:

1) can support a rich set of use cases,
2) model the existing documentation templates used by the industries,
3) interface well with other formats for storing documentation and requirements, e.g., ReqIF and SPDX.

**COMMENT:**

Verification: data model diagram TBD.

**Parents:**

- ``[SDOC-SSS-88]`` :ref:`SDOC-SSS-88`
- ``[SDOC-SSS-58]`` :ref:`SDOC-SSS-58`

.. _SDOC-SRS-26:

Requirement model
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-26
    * - **STATUS:**
      - Active

StrictDoc's data model shall support modeling requirements.

**Parents:**

- ``[SDOC-SSS-4]`` :ref:`SDOC-SSS-4`

.. _SDOC-SRS-100:

Requirement model fields
------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-100
    * - **STATUS:**
      - Active

StrictDoc's "Requirement" model shall support configurable fields system.

**Parents:**

- ``[SDOC-SSS-62]`` :ref:`SDOC-SSS-62`

.. _SDOC-SRS-132:

Requirement model default fields
--------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-132
    * - **STATUS:**
      - Active

By default, the Requirement shall support the following fields:

- MID
- UID
- STATUS
- TITLE
- STATEMENT
- RATIONALE
- COMMENT.

**RATIONALE:**

These fields are the most typical fields found in requirement documents.

**Parents:**

- ``[SDOC-SSS-61]`` :ref:`SDOC-SSS-61`

.. _SDOC-SRS-98:

Document model
--------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-98
    * - **STATUS:**
      - Active

StrictDoc's data model shall support modeling documents.

**Parents:**

- ``[SDOC-SSS-64]`` :ref:`SDOC-SSS-64`

.. _SDOC-SRS-110:

Document metadata
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-110
    * - **STATUS:**
      - Active

StrictDoc's data model shall support a Document metadata model including at least:

- UID
- Document version
- Document classification
- Document authors.

**Parents:**

- ``[SDOC-SSS-53]`` :ref:`SDOC-SSS-53`
- ``[SDOC-SSS-75]`` :ref:`SDOC-SSS-75`

.. _SDOC-SRS-99:

Section model
-------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-99
    * - **STATUS:**
      - Active

StrictDoc's data model shall support a concept of a "Section" which nests other Sections, Requirements, Texts.

**RATIONALE:**

"Section" corresponds to a chapter or a section in a document and helps to organize a document by grouping text nodes, requirements and other sections.

**Parents:**

- ``[SDOC-SSS-51]`` :ref:`SDOC-SSS-51`

.. _SDOC-SRS-135:

Free text
---------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-135
    * - **STATUS:**
      - Active

StrictDoc's data model shall support a "Free Text" model, representing non-normative documentation content.

**RATIONALE:**

Documentation comprises normative components, such as uniquely identifiable elements like requirements or design items, and non-normative components, including introductory text, overview chapters, and other content. The non-normative parts help provide a general understanding for the reader but do not contribute to traceability information. StrictDoc's free text is designed to store this type of non-normative information in SDoc documents.

**Parents:**

- ``[SDOC-SSS-3]`` :ref:`SDOC-SSS-3`

.. _SDOC-SRS-109:

Composeable document
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-109
    * - **STATUS:**
      - Active

StrictDoc's data model shall allow composing a Document from other Documents.

**RATIONALE:**

The logic behind the parent requirement remains fully relevant. Additionally, an alternative approach could involve using a dedicated entity, like "Fragment", to allow a Document to be composed of includable sections or document fragments. Managing composition at the Document level eliminates the need in additional entities like "Fragment", streamlining both the conceptual understanding and the practical implementation of composability.

**COMMENT:**

The corresponding UI capability for Fragments CRUD is TBD.

**Parents:**

- ``[SDOC-SSS-52]`` :ref:`SDOC-SSS-52`
- ``[DO178-4]`` :ref:`DO178-4`

.. _SDOC-SRS-31:

Requirement relations
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-31
    * - **STATUS:**
      - Active

The StrictDoc data model shall support connecting requirements using Parent and Child relations.

**RATIONALE:**

Support of both Parent and Child relations allows to build typical requirements relations such as child-to-parent and less common relations when one document can have parent links to a parent document and child links to a child document (e.g., the so-called "compliance" or "tailoring matrix" documents may use this structure).

**Parents:**

- ``[SDOC-SSS-7]`` :ref:`SDOC-SSS-7`
- ``[SDOC-SSS-48]`` :ref:`SDOC-SSS-48`

.. _SDOC-SRS-101:

Requirement relation roles
--------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-101
    * - **STATUS:**
      - Active

Each SDoc relation shall be optionally configurable with a relation role.

NOTE: A relation role is a string value. Typical examples: "refines", "verifies", "implements".

**Parents:**

- ``[SDOC-SSS-8]`` :ref:`SDOC-SSS-8`

SDoc text markup
================

.. _SDOC-SRS-20:

SDoc markup language
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-20
    * - **STATUS:**
      - Active

StrictDoc shall implement its own text markup language called S-Doc (strict-doc).

**RATIONALE:**

The most commonly used Markdown format lacks the ability to store requirements metadata. While the RST syntax does allow for customization with directives to implement metadata extensions, its visual appearance contradicts other requirements of StrictDoc, such as the type-safety of the grammar and visual readability. Therefore, a markup language tailored specifically to the needs of the requirements tool provides direct control over the capabilities implemented in both the markup and the user interface.

**Parents:**

- ``[SDOC-SSS-88]`` :ref:`SDOC-SSS-88`

.. _SDOC-SRS-136:

Identical SDoc content by import/export roundtrip
-------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-136
    * - **STATUS:**
      - Active

StrictDoc shall ensure that identical SDoc content is produced every time StrictDoc reads an SDoc file and then writes it to another SDoc file.

**RATIONALE:**

A consistent import/export roundtrip implementation and testing reduces the risk of the SDoc bi-directional import/export corruption.

**Parents:**

- ``[SDOC-SSS-94]`` :ref:`SDOC-SSS-94`

.. _SDOC-SRS-127:

SDoc and Git storage
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-127
    * - **STATUS:**
      - Active

StrictDoc shall assume and implement capabilities for storage of SDoc files using Git version control system.

**Parents:**

- ``[SDOC-SSS-87]`` :ref:`SDOC-SSS-87`
- ``[SDOC-SSS-33]`` :ref:`SDOC-SSS-33`
- ``[SDOC-SSS-84]`` :ref:`SDOC-SSS-84`
- ``[SDOC-SSS-94]`` :ref:`SDOC-SSS-94`

.. _SDOC-SRS-104:

SDoc file extension
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-104
    * - **STATUS:**
      - Active

The SDoc markup content shall be stored in files with .sdoc extension.

**RATIONALE:**

Given that the name of the model is S-Doc (strict-doc), it is reasonable to make the document files have the ``.sdoc`` extension. This helps to identify the document files.

**Parents:**

- ``[SDOC-SSS-80]`` :ref:`SDOC-SSS-80`

.. _SDOC-SRS-105:

One document per one SDoc file
------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-105
    * - **STATUS:**
      - Active

StrictDoc's SDoc file shall represent content of a single document.

**COMMENT:**

A "Document" corresponds to a "Document" of the SDoc data model.

**Parents:**

- ``[SDOC-SSS-64]`` :ref:`SDOC-SSS-64`
- ``[DO178-1]`` :ref:`DO178-1`

.. _SDOC-SRS-19:

Fixed grammar
-------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-19
    * - **STATUS:**
      - Active

StrictDoc's markup language shall be based on a well-defined grammar.

**Parents:**

- ``[DO178-2]`` :ref:`DO178-2`
- ``[SDOC-SSS-55]`` :ref:`SDOC-SSS-55`
- ``[SDOC-SSS-54]`` :ref:`SDOC-SSS-54`
- ``[SDOC-SSS-94]`` :ref:`SDOC-SSS-94`

.. _SDOC-SRS-93:

Default grammar fields
----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-93
    * - **STATUS:**
      - Active

The StrictDoc grammar shall have at least the following fields activated by default:

- UID
- STATUS
- LINKS (references to other requirements)
- TITLE
- STATEMENT
- RATIONALE
- COMMENT.

**Parents:**

- ``[SDOC-SSS-61]`` :ref:`SDOC-SSS-61`

.. _SDOC-SRS-21:

Custom grammar / fields
-----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-21
    * - **STATUS:**
      - Active

The SDoc markup shall support custom grammars.

**RATIONALE:**

A custom grammar allows a user to define their own configuration of requirement fields.

**Parents:**

- ``[SDOC-SSS-62]`` :ref:`SDOC-SSS-62`

.. _SDOC-SRS-122:

Importable grammars
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-122
    * - **STATUS:**
      - Active

StrictDoc shall support an inclusion of a grammar stored in a separate file.

**RATIONALE:**

A single grammar defined for several documents helps to standardize the structure of all documents in a documentation tree and removes the effort needed to create identical grammars all the time.

**Parents:**

- ``[DO178-9]`` :ref:`DO178-9`
- ``[SDOC-SSS-52]`` :ref:`SDOC-SSS-52`

.. _SDOC-SRS-22:

UID identifier format
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-22
    * - **STATUS:**
      - Active

The SDoc markup shall only accept UID identifiers that consist of alphanumeric characters separated by a limited set of ("_", "-", ".") characters (TBD).

**RATIONALE:**

A standardized UID format supports easier unique identification of requirements. It is easier to visually identify UIDs that look similar and common to a given industry.

**COMMENT:**

This requirement may need a revision to accommodate for more UID formats.

**Parents:**

- ``[SDOC-SSS-89]`` :ref:`SDOC-SSS-89`

.. _SDOC-SRS-24:

Support RST markup
------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-24
    * - **STATUS:**
      - Active

StrictDoc shall support the RST markup.

**Parents:**

- ``[SDOC-SSS-63]`` :ref:`SDOC-SSS-63`

.. _SDOC-SRS-27:

MathJAX
-------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-27
    * - **STATUS:**
      - Active

StrictDoc's markup shall enable support integration with MathJax.

**Parents:**

- ``[SDOC-SSS-63]`` :ref:`SDOC-SSS-63`

.. _SDOC-SRS-23:

No indentation
--------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-23
    * - **STATUS:**
      - Active

SDoc text markup blocks shall all start from column 1, i.e., the nesting of the blocks is not allowed.

**RATIONALE:**

Nesting large text blocks of free text and requirements compromises readability.

**Parents:**

- ``[SDOC-SSS-55]`` :ref:`SDOC-SSS-55`

.. _SDOC-SRS-25:

Type-safe fields
----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-25
    * - **STATUS:**
      - Active

SDoc markup shall provide "type safety" for all fields.

NOTE: "Type safety" means that each field has a type and a corresponding set of validation checks.

**Parents:**

- ``[SDOC-SSS-55]`` :ref:`SDOC-SSS-55`
- ``[SDOC-SSS-94]`` :ref:`SDOC-SSS-94`

.. _SECTION-SRS-Graph-database:

Graph database
==============

.. _SDOC-SRS-28:

Traceability index
------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-28
    * - **STATUS:**
      - Active

StrictDoc shall maintain a complete Traceability Index of all documentation- and requirements-related information available in a project tree.

**Parents:**

- ``[SDOC-SSS-7]`` :ref:`SDOC-SSS-7`

.. _SDOC-SRS-29:

Uniqueness UID in tree
----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-29
    * - **STATUS:**
      - Active

For each requirement node, the Traceability Index shall ensure its uniqueness throughout the node's lifecycle.

**RATIONALE:**

The requirement ensures that the Traceability Index takes of care of validating the uniqueness of all nodes in a document/requirements graph.

**Parents:**

- ``[SDOC-SSS-89]`` :ref:`SDOC-SSS-89`
- ``[SDOC-SSS-94]`` :ref:`SDOC-SSS-94`

.. _SDOC-SRS-30:

Detect links cycles
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-30
    * - **STATUS:**
      - Active

The Traceability Index shall detect cycles between requirements.

**Parents:**

- ``[SDOC-SSS-47]`` :ref:`SDOC-SSS-47`
- ``[SDOC-SSS-94]`` :ref:`SDOC-SSS-94`

.. _SDOC-SRS-32:

Link document nodes
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-32
    * - **STATUS:**
      - Active

The Traceability Index shall recognize and maintain the relations between all documents of a project tree.

**RATIONALE:**

The relations between all documents are a summary of all relations between these documents' requirements. This information is useful for:

1) Structural analysis of a requirements/documents graph.
2) Incremental regeneration of only those documents whose content was modified.

**Parents:**

- ``[SDOC-SSS-47]`` :ref:`SDOC-SSS-47`
- ``[SDOC-SSS-13]`` :ref:`SDOC-SSS-13`
- ``[SDOC-SSS-14]`` :ref:`SDOC-SSS-14`

.. _SDOC-SRS-102:

Automatic resolution of reverse relations
-----------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-102
    * - **STATUS:**
      - Active

The StrictDoc's graph database shall maintain the requirement relations and their reverse relations as follows:

- For a Parent relation, the database shall calculate the reverse Child relation.
- For a Child relation, the database shall calculate the reverse Parent relation.

**RATIONALE:**

The calculation of the reverse relations allows the user interface code to get and display both requirement's parent and child relations.

**COMMENT:**

Example: If a child requirement REQ-002 has a parent requirement REQ-001, the graph database first reads the link ``REQ-002 -Parent> REQ-001``, then it creates a corresponding ``REQ-001 -Child> REQ-002`` on the go. Both relations can be queried as follows, in pseudocode:

.. code-block::

    get_parent_requirements(REQ-002) == [REQ-001]
    get_children_requirements(REQ-001) == [REQ-002]

**Parents:**

- ``[SDOC-SSS-71]`` :ref:`SDOC-SSS-71`
- ``[SDOC-SSS-48]`` :ref:`SDOC-SSS-48`

Documentation tree
==================

.. _SDOC-SRS-115:

Finding documents recursively
-----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-115
    * - **STATUS:**
      - Active

StrictDoc shall discover SDoc documents recursively based on a specified input path.

**RATIONALE:**

Recursive search allows working with documents located in multiple folders, potentially spanning over several Git repositories.

**Parents:**

- ``[SDOC-SSS-34]`` :ref:`SDOC-SSS-34`
- ``[DO178-3]`` :ref:`DO178-3`

.. _SECTION-SRS-Web-HTML-frontend:

Web/HTML frontend
=================

.. _SECTION-SRS-General-export-requirements-2:

General export requirements
---------------------------

.. _SDOC-SRS-49:

Export to static HTML website
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-49
    * - **STATUS:**
      - Active

StrictDoc shall support generating requirements documentation into static HTML.

**Parents:**

- ``[SDOC-SSS-30]`` :ref:`SDOC-SSS-30`

.. _SDOC-SRS-50:

Web interface
~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-50
    * - **STATUS:**
      - Active

StrictDoc shall provide a web interface.

**Parents:**

- ``[SDOC-SSS-31]`` :ref:`SDOC-SSS-31`
- ``[DO178-6]`` :ref:`DO178-6`
- ``[SDOC-SSS-79]`` :ref:`SDOC-SSS-79`
- ``[SDOC-SSS-80]`` :ref:`SDOC-SSS-80`

.. _SDOC-SRS-51:

Export to printable HTML pages (HTML2PDF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-51
    * - **STATUS:**
      - Active

StrictDoc shall provide export to printable HTML pages.

**Parents:**

- ``[DO178-5]`` :ref:`DO178-5`

.. _SDOC-SRS-48:

Preserve generated file names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-48
    * - **STATUS:**
      - Active

For all export operations, StrictDoc shall maintain the original filenames of the documents when producing output files.

**RATIONALE:**

Name preservation helps to visually identify which input file an output file corresponds to.

**Parents:**

- ``[SDOC-SSS-80]`` :ref:`SDOC-SSS-80`

.. _SECTION-SRS-Screen-Project-tree:

Screen: Project tree
--------------------

.. _SDOC-SRS-53:

View project tree
~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-53
    * - **STATUS:**
      - Active

StrictDoc's "Project tree" screen shall provide browsing of a documentation project tree.

**RATIONALE:**

This screen is the main tool for visualizing the project tree structure.

**Parents:**

- ``[SDOC-SSS-91]`` :ref:`SDOC-SSS-91`

.. _SDOC-SRS-107:

Create document
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-107
    * - **STATUS:**
      - Active

StrictDoc's Project Tree screen shall allow creating documents.

**Parents:**

- ``[SDOC-SSS-3]`` :ref:`SDOC-SSS-3`

.. _SDOC-SRS-108:

Delete document
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-108
    * - **STATUS:**
      - Active

StrictDoc's Project Tree screen shall allow deleting documents.

**Parents:**

- ``[SDOC-SSS-3]`` :ref:`SDOC-SSS-3`

.. _SECTION-SRS-Screen-Document-DOC:

Screen: Document (DOC)
----------------------

.. _SDOC-SRS-54:

Read document
~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-54
    * - **STATUS:**
      - Active

StrictDoc's Document screen shall allow reading documents.

**Parents:**

- ``[SDOC-SSS-3]`` :ref:`SDOC-SSS-3`

.. _SDOC-SRS-106:

Update document
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-106
    * - **STATUS:**
      - Active

StrictDoc's Document screen shall allow updating documents.

**Parents:**

- ``[SDOC-SSS-3]`` :ref:`SDOC-SSS-3`

.. _SDOC-SRS-55:

Edit requirement nodes
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-55
    * - **STATUS:**
      - Active

StrictDoc's Document screen shall allow editing requirements.

**Parents:**

- ``[SDOC-SSS-4]`` :ref:`SDOC-SSS-4`

.. _SDOC-SRS-92:

Move requirement / section nodes within document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-92
    * - **STATUS:**
      - Active

StrictDoc's Document screen shall provide a capability to move the nodes within a document.

**RATIONALE:**

Moving the nodes within a document is a convenience feature that speeds up the requirements editing process significantly.

**Parents:**

- ``[SDOC-SSS-5]`` :ref:`SDOC-SSS-5`

.. _SDOC-SRS-56:

Edit Document grammar
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-56
    * - **STATUS:**
      - Active

StrictDoc's screen shall allow editing a document's grammar.

**RATIONALE:**

Editing document grammar allows a user to customize the requirements fields.

**Parents:**

- ``[SDOC-SSS-62]`` :ref:`SDOC-SSS-62`

.. _SDOC-SRS-57:

Edit Document options
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-57
    * - **STATUS:**
      - Active

StrictDoc's Document screen shall provide controls for configuring the document-specific options.

**Parents:**

- ``[SDOC-SSS-93]`` :ref:`SDOC-SSS-93`

.. _SDOC-SRS-96:

Auto-generate requirements UIDs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-96
    * - **STATUS:**
      - Progress

StrictDoc's Document screen shall provide controls for automatic generation of requirements UIDs.

**Parents:**

- ``[SDOC-SSS-6]`` :ref:`SDOC-SSS-6`
- ``[SDOC-SSS-80]`` :ref:`SDOC-SSS-80`

.. _SDOC-SRS-59:

Buttons to copy text to buffer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-59
    * - **STATUS:**
      - Active

StrictDoc shall provide a "copy text to buffer" button for all requirement's text fields.

**Parents:**

- ``[SDOC-SSS-80]`` :ref:`SDOC-SSS-80`

.. _SECTION-SRS-Screen-Table-TBL:

Screen: Table (TBL)
-------------------

.. _SDOC-SRS-62:

View TBL screen
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-62
    * - **STATUS:**
      - Active

StrictDoc's Table screen shall allow reading documents in a table-like manner.

**Parents:**

- ``[SDOC-SSS-73]`` :ref:`SDOC-SSS-73`

.. _SECTION-SRS-Screen-Traceability-TR:

Screen: Traceability (TR)
-------------------------

.. _SDOC-SRS-65:

View TR screen
~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-65
    * - **STATUS:**
      - Active

StrictDoc shall provide a single document-level traceability screen.

NOTE: This screen helps to read a document like a normal document while the traceability to this document's parent and child elements is visible at the same time.

**Parents:**

- ``[SDOC-SSS-28]`` :ref:`SDOC-SSS-28`

.. _SECTION-SRS-Screen-Deep-traceability-DTR:

Screen: Deep traceability (DTR)
-------------------------------

.. _SDOC-SRS-66:

View DTR screen
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-66
    * - **STATUS:**
      - Active

StrictDoc shall provide a deep traceability screen.

**Parents:**

- ``[DO178-12]`` :ref:`DO178-12`

Screen: Project statistics
--------------------------

.. _SDOC-SRS-97:

Display project statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-97
    * - **STATUS:**
      - Active

StrictDoc shall provide a Project Statistics screen that displays the following project information:

- Project title
- Date of generation
- Git revision
- Total documents
- Total requirements
- Requirements status breakdown
- Total number of TBD/TBC found in documents.

**RATIONALE:**

TBD

**Parents:**

- ``[SDOC-SSS-49]`` :ref:`SDOC-SSS-49`
- ``[DO178-12]`` :ref:`DO178-12`
- ``[SDOC-SSS-29]`` :ref:`SDOC-SSS-29`

Screen: Traceability matrix
---------------------------

.. _SDOC-SRS-112:

Traceability matrix
~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-112
    * - **STATUS:**
      - Active

StrictDoc shall provide a traceability matrix screen.

**Parents:**

- ``[SDOC-SSS-28]`` :ref:`SDOC-SSS-28`
- ``[DO178-10]`` :ref:`DO178-10`
- ``[DO178-12]`` :ref:`DO178-12`

Screen: Project tree diff
-------------------------

.. _SDOC-SRS-111:

Project tree diff
~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-111
    * - **STATUS:**
      - Active

StrictDoc shall provide a project tree diff screen.

**Parents:**

- ``[SDOC-SSS-75]`` :ref:`SDOC-SSS-75`
- ``[SDOC-SSS-74]`` :ref:`SDOC-SSS-74`
- ``[DO178-15]`` :ref:`DO178-15`

.. _SECTION-SRS-Requirements-to-source-traceability:

Requirements-to-source traceability
===================================

.. _SDOC-SRS-33:

Link requirements with source files
-----------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-33
    * - **STATUS:**
      - Active

StrictDoc shall support bi-directional linking requirements with source files.

**Parents:**

- ``[SDOC-SSS-72]`` :ref:`SDOC-SSS-72`

.. _SDOC-SRS-34:

Annotate source file
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-34
    * - **STATUS:**
      - Active

StrictDoc shall support a dedicated markup language for annotating source code with links referencing the requirements.

**Parents:**

- ``[SDOC-SSS-72]`` :ref:`SDOC-SSS-72`

.. _SDOC-SRS-124:

Single-line code marker
-----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-124
    * - **STATUS:**
      - Active

StrictDoc's source file marker syntax shall support single-line markers.

NOTE: A single-line marker points to a single line in a source file.

**RATIONALE:**

The advantage of a single-line marker compared to a range marker is that a single-line marker is not intrusive and does not clutter source code. Such a single-marker can be kept in a comment to a function (e.g., Doxygen), not in the function body.

**Parents:**

- ``[SDOC-SSS-72]`` :ref:`SDOC-SSS-72`

.. _SDOC-SRS-35:

Generate source coverage
------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-35
    * - **STATUS:**
      - Active

StrictDoc shall generate project source code coverage information.

NOTE: Source code information can be visualized using both web or CLI interfaces.

**Parents:**

- ``[SDOC-SSS-72]`` :ref:`SDOC-SSS-72`
- ``[DO178-13]`` :ref:`DO178-13`

.. _SDOC-SRS-36:

Generate source file traceability
---------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-36
    * - **STATUS:**
      - Active

StrictDoc shall generate single file traceability information.

**RATIONALE:**

With this capability in place, it is possible to focus on a single implementation file's links to requirements which helps in the code reviews and inspections.

**Parents:**

- ``[SDOC-SSS-72]`` :ref:`SDOC-SSS-72`

.. _SECTION-SRS-Export-import-formats:

Export/import formats
=====================

.. _SECTION-SRS-RST:

RST
---

.. _SDOC-SRS-70:

Export to RST
~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-70
    * - **STATUS:**
      - Active

StrictDoc shall allow exporting SDoc content to the RST format.

**RATIONALE:**

Exporting SDoc content to RST enables:

1) Generating RST to Sphinx HTML documentation.
2) Generating RST to PDF using Sphinx/LaTeX.

**Parents:**

- ``[DO178-5]`` :ref:`DO178-5`
- ``[DO178-16]`` :ref:`DO178-16`

.. _SDOC-SRS-71:

Docutils
~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-71
    * - **STATUS:**
      - Active

StrictDoc shall generate RST markup to HTML using Docutils.

**RATIONALE:**

Docutils is the most mature RST-to-HTML converter.

**COMMENT:**

TBD: Move this to design decisions.

**Parents:**

- ``[DO178-5]`` :ref:`DO178-5`
- ``[DO178-16]`` :ref:`DO178-16`

.. _SECTION-SRS-ReqIF:

ReqIF
-----

.. _SDOC-SRS-72:

Export/import from/to ReqIF
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-72
    * - **STATUS:**
      - Progress

StrictDoc shall support exporting/importing requirements content from/to ReqIF format.

**Parents:**

- ``[SDOC-SSS-58]`` :ref:`SDOC-SSS-58`

.. _SDOC-SRS-73:

Standalone ReqIF layer
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-73
    * - **STATUS:**
      - Active

StrictDoc shall maintain the core ReqIF implementation as a separate software component.

**RATIONALE:**

ReqIF is a well-defined standard which exists independently of StrictDoc's development. It is reasonable to maintain the ReqIF codebase as a separate software component to allow independent development and easier maintainability.

**Parents:**

- ``[SDOC-SSS-90]`` :ref:`SDOC-SSS-90`

.. _SECTION-SRS-Excel:

Excel and CSV
-------------

.. _SDOC-SRS-74:

Export to Excel
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-74
    * - **STATUS:**
      - Active

StrictDoc shall allow exporting SDoc documents to Excel, one Excel sheet per document.

**Parents:**

- ``[SDOC-SSS-60]`` :ref:`SDOC-SSS-60`

.. _SDOC-SRS-134:

Selected fields export
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-134
    * - **STATUS:**
      - Active

StrictDoc Excel export shall allow exporting SDoc documents to Excel with only selected fields.

**Parents:**

- ``[SDOC-SSS-60]`` :ref:`SDOC-SSS-60`

.. _SECTION-SRS-Graphviz-Dot-export:

Graphviz/Dot export
-------------------

.. _SDOC-SRS-90:

Export to Graphviz/Dot
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-90
    * - **STATUS:**
      - Active

StrictDoc shall support exporting requirements information to PDF format using Graphviz.

**RATIONALE:**

Graphviz is one of the most capable tools for visualizing graph information, which makes it a perfect tool for visualizing requirements graphs create in StrictDoc.

**Parents:**

- ``[SDOC-SSS-56]`` :ref:`SDOC-SSS-56`

.. _SECTION-SRS-Command-line-interface:

Command-line interface
======================

General CLI requirements
------------------------

.. _SDOC-SRS-103:

Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-103
    * - **STATUS:**
      - Active

StrictDoc shall provide a command-line interface.

**Parents:**

- ``[SDOC-SSS-32]`` :ref:`SDOC-SSS-32`

.. _SECTION-SRS-Command-Manage:

Command: Manage
---------------

.. _SECTION-SRS-Command-Auto-UID:

Command: Auto UID
~~~~~~~~~~~~~~~~~

.. _SDOC-SRS-85:

Auto-generate requirements UIDs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-85
    * - **STATUS:**
      - Active

StrictDoc shall allow automatic generation of requirements UIDs.

**Parents:**

- ``[SDOC-SSS-6]`` :ref:`SDOC-SSS-6`

Python API
==========

.. _SDOC-SRS-125:

StrictDoc Python API
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-125
    * - **STATUS:**
      - Active

StrictDoc shall provide a Python API for its core functions:

- Reading SDoc files
- Creating traceability graph
- Generating HTML exports
- Converting SDoc to other formats.

**Parents:**

- ``[SDOC-SSS-79]`` :ref:`SDOC-SSS-79`
- ``[SDOC-SSS-86]`` :ref:`SDOC-SSS-86`
- ``[SDOC-SSS-87]`` :ref:`SDOC-SSS-87`

Web server
==========

.. _SDOC-SRS-126:

Web server
----------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-126
    * - **STATUS:**
      - Active

StrictDoc shall provide a web server.

**RATIONALE:**

A web server is a precondition for StrictDoc's web interface. A web server can be available to a single user on their local machine or it can be deployed to a network and be made accessible by several computers.

**Parents:**

- ``[SDOC-SSS-83]`` :ref:`SDOC-SSS-83`

User experience
===============

.. _SECTION-SSRS-Strict-mode-by-default:

Strict mode by default
----------------------

.. _SDOC-SRS-6:

Warnings are errors
~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-6
    * - **STATUS:**
      - Active

StrictDoc's default mode of operation shall treat all warnings as errors.

**Parents:**

- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SECTION-SRS-Configurability:

Configurability
===============

.. _SDOC-SRS-37:

strictdoc.toml file
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-37
    * - **STATUS:**
      - Active

StrictDoc shall support a configuration of project-level options through a TOML file named ``strictdoc.toml``.

**Parents:**

- ``[SDOC-SSS-92]`` :ref:`SDOC-SSS-92`

.. _SDOC-SRS-39:

Feature toggles
---------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-39
    * - **STATUS:**
      - Active

StrictDoc shall allow a user to select a subset of StrictDoc's available features by listing them in the ``strictdoc.toml`` file.

**Parents:**

- ``[SDOC-SSS-92]`` :ref:`SDOC-SSS-92`

.. _SDOC-SRS-119:

'Host' parameter
----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-119
    * - **STATUS:**
      - Active

StrictDoc shall support configuring a host/port on which the StrictDoc web server is run.

**Parents:**

- ``[DO178-8]`` :ref:`DO178-8`

.. _SECTION-SSRS-Performance:

Performance
===========

.. _SDOC-SRS-1:

Process-based parallelization
-----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-1
    * - **STATUS:**
      - Active

StrictDoc shall support process-based parallelization for time-critical tasks.

**RATIONALE:**

Process-based parallelization can provide a good speed-up when several large documents have to be generated.

**Parents:**

- ``[SDOC-SSS-13]`` :ref:`SDOC-SSS-13`
- ``[SDOC-SSS-14]`` :ref:`SDOC-SSS-14`

.. _SDOC-SRS-95:

Caching of parsed SDoc documents
--------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-95
    * - **STATUS:**
      - Active

StrictDoc shall implement caching of parsed SDoc documents.

**Parents:**

- ``[SDOC-SSS-13]`` :ref:`SDOC-SSS-13`
- ``[SDOC-SSS-14]`` :ref:`SDOC-SSS-14`

.. _SDOC-SRS-2:

Incremental generation of documents
-----------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-2
    * - **STATUS:**
      - Active

StrictDoc shall support incremental generation of documents.

NOTE: "Incremental" means that only the modified documents are regenerated when StrictDoc is run repeatedly against the same project tree.

**Parents:**

- ``[SDOC-SSS-13]`` :ref:`SDOC-SSS-13`
- ``[SDOC-SSS-14]`` :ref:`SDOC-SSS-14`

.. _SDOC-SRS-3:

Caching of RST fragments
------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-3
    * - **STATUS:**
      - Active

StrictDoc shall cache the RST fragments rendered to HTML.

**RATIONALE:**

Conversion of RST markup to HTML is a time consuming process. Caching the rendered HTML of each fragment helps to save time when rendering the HTML content.

**Parents:**

- ``[SDOC-SSS-13]`` :ref:`SDOC-SSS-13`
- ``[SDOC-SSS-14]`` :ref:`SDOC-SSS-14`

.. _SDOC-SRS-4:

On-demand loading of HTML pages
-------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-4
    * - **STATUS:**
      - Active

StrictDoc's web interface shall generate the HTML content only when it is directly requested by a user.

**RATIONALE:**

Generating a whole documentation tree for a user project can be time consuming. The on-demand loading ensures the "do less work" approach when it comes to rendering the HTML pages.

**Parents:**

- ``[SDOC-SSS-13]`` :ref:`SDOC-SSS-13`
- ``[SDOC-SSS-14]`` :ref:`SDOC-SSS-14`

.. _SDOC-SRS-5:

Precompiled Jinja templates
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-5
    * - **STATUS:**
      - Active

StrictDoc shall support a precompilation of HTML templates.

**RATIONALE:**

The StrictDoc-exported HTML content visible to a user is assembled from numerous small HTML fragments. Precompiling the HTML templates from which the content gets rendered improves the performance of the HTML rendering.

**Parents:**

- ``[SDOC-SSS-13]`` :ref:`SDOC-SSS-13`
- ``[SDOC-SSS-14]`` :ref:`SDOC-SSS-14`

.. _SECTION-SRS-Quality-requirements:

Development process requirements
================================

General process
---------------

.. _SDOC-SRS-133:

Priority handling of critical issues in StrictDoc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-133
    * - **STATUS:**
      - Active

All critical issues reported in relation to StrictDoc shall be addressed with utmost priority.

**RATIONALE:**

Prioritizing major issues ensures StrictDoc remains stable and reliable, preventing serious problems that could compromise its performance and integrity.

**Parents:**

- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SECTION-SRS-Requirements-engineering:

Requirements engineering
------------------------

.. _SDOC-SRS-128:

Requirements-based development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-128
    * - **STATUS:**
      - Active

StrictDoc's development shall be requirements-based.

**Parents:**

- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`
- ``[SDOC-SSS-76]`` :ref:`SDOC-SSS-76`

.. _SDOC-SRS-91:

Self-hosted requirements
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-91
    * - **STATUS:**
      - Active

StrictDoc's requirements shall be written using StrictDoc.

**Parents:**

- ``[SDOC-SSS-50]`` :ref:`SDOC-SSS-50`
- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SECTION-SRS-Implementation-requirements:

Implementation requirements
---------------------------

.. _SECTION-SRS-Programming-languages:

Programming languages
~~~~~~~~~~~~~~~~~~~~~

.. _SDOC-SRS-8:

Python language
^^^^^^^^^^^^^^^

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-8
    * - **STATUS:**
      - Active

StrictDoc shall be written in Python.

**RATIONALE:**

Python has an excellent package ecosystem. It is a widely used language. It is most often the next language for C/C++ programming community when it comes to the tools development and scripting tasks.

**Parents:**

- ``[SDOC-SSS-69]`` :ref:`SDOC-SSS-69`

.. _SECTION-SRS-Cross-platform-availability:

Cross-platform availability
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _SDOC-SRS-9:

Linux
^^^^^

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-9
    * - **STATUS:**
      - Active

StrictDoc shall support the Linux operating systems.

**Parents:**

- ``[SDOC-SSS-67]`` :ref:`SDOC-SSS-67`

.. _SDOC-SRS-10:

macOS
^^^^^

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-10
    * - **STATUS:**
      - Active

StrictDoc shall support the macOS operating system.

**Parents:**

- ``[SDOC-SSS-67]`` :ref:`SDOC-SSS-67`

.. _SDOC-SRS-11:

Windows
^^^^^^^

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-11
    * - **STATUS:**
      - Active

StrictDoc shall support the Windows operating system.

**Parents:**

- ``[SDOC-SSS-67]`` :ref:`SDOC-SSS-67`

.. _SECTION-SRS-Implementation-constraints:

Implementation constraints
--------------------------

.. _SDOC-SRS-89:

Use of open source components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-89
    * - **STATUS:**
      - Active

StrictDoc shall be built using only open source software components.

**RATIONALE:**

No commercial/proprietary dependency chain ensures that StrictDoc remain free and open for everyone.

**Parents:**

- ``[DO178-7]`` :ref:`DO178-7`
- ``[SDOC-SSS-39]`` :ref:`SDOC-SSS-39`

.. _SDOC-SRS-14:

No heavy UI frameworks
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-14
    * - **STATUS:**
      - Active

StrictDoc shall avoid using large and demanding UI frameworks.

NOTE: An example of frameworks that require a very specific architecture: React JS, AngularJS.

**Parents:**

- ``[SDOC-SSS-90]`` :ref:`SDOC-SSS-90`

.. _SDOC-SRS-15:

No use of NPM
~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-15
    * - **STATUS:**
      - Active

StrictDoc shall avoid extending its infrastructure with anything based on NPM-ecosystem.

**RATIONALE:**

StrictDoc already deals with the Python/Pip/Pypi ecosystem. The amount of necessary maintenance is already quite high. NPM is known for splitting its projects into very small parts, which increases the complexity of maintaining all dependencies.

**Parents:**

- ``[SDOC-SSS-90]`` :ref:`SDOC-SSS-90`

.. _SDOC-SRS-16:

No use of JavaScript replacement languages (e.g., Typescript)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-16
    * - **STATUS:**
      - Active

StrictDoc shall avoid using JavaScript-based programming languages.

**RATIONALE:**

The development team does not have specific experience with any of the JS alternatives. Staying with a general subset of JavaScript is a safer choice.

**Parents:**

- ``[SDOC-SSS-90]`` :ref:`SDOC-SSS-90`

.. _SDOC-SRS-87:

Monolithic application with no microservices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-87
    * - **STATUS:**
      - Active

StrictDoc shall avoid using microservices and microservice-based architectures.

**RATIONALE:**

The project is too small to scale to a multi-service architecture.

**COMMENT:**

This requirement could be re-considered only if a significant technical pressure
would require the use of microservices.

**Parents:**

- ``[SDOC-SSS-82]`` :ref:`SDOC-SSS-82`

.. _SDOC-SRS-88:

No reliance on containerization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-88
    * - **STATUS:**
      - Active

StrictDoc shall avoid using containers and containerization technologies.

**RATIONALE:**

Containers are significant extra layer of complexity. They are hard to debug.

**COMMENT:**

This constraint does not block a StrictDoc user from wrapping StrictDoc into their containers.

**Parents:**

- ``[SDOC-SSS-82]`` :ref:`SDOC-SSS-82`

.. _SECTION-SRS-Coding-constraints:

Coding constraints
------------------

.. _SDOC-SRS-40:

Use of asserts
~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-40
    * - **STATUS:**
      - Active

StrictDoc's development shall ensure a use of assertions throughout the project codebase.

NOTE: At a minimum, the function input parameters must be checked for validity.

**Parents:**

- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SDOC-SRS-41:

Use of type annotations in Python code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-41
    * - **STATUS:**
      - Active

StrictDoc's development shall ensure a use of type annotations throughout the project's Python codebase.

**Parents:**

- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SECTION-SRS-Linting:

Linting
-------

.. _SDOC-SRS-42:

Compliance with Python community practices (PEP8 etc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-42
    * - **STATUS:**
      - Active

StrictDoc's development shall ensure that the project's codebase is compliant with the Python community's modern practices.

**Parents:**

- ``[SDOC-SSS-90]`` :ref:`SDOC-SSS-90`

.. _SECTION-SRS-Static-analysis:

Static analysis
---------------

.. _SDOC-SRS-43:

Static type checking
~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-43
    * - **STATUS:**
      - Active

StrictDoc's development shall include a continuous type checking of StrictDoc's codebase.

**Parents:**

- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SECTION-SRS-Testing:

Testing
-------

.. _SDOC-SRS-44:

Unit testing
~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-44
    * - **STATUS:**
      - Active

StrictDoc's development shall provide unit testing of its codebase.

**Parents:**

- ``[SDOC-SSS-77]`` :ref:`SDOC-SSS-77`
- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SDOC-SRS-45:

CLI interface black-box integration testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-45
    * - **STATUS:**
      - Active

StrictDoc's development shall provide complete black-box integration testing of its command-line interface.

**Parents:**

- ``[SDOC-SSS-77]`` :ref:`SDOC-SSS-77`
- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SDOC-SRS-46:

Web end-to-end testing
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-46
    * - **STATUS:**
      - Active

StrictDoc's development shall provide complete end-to-end testing of the web interface.

**Parents:**

- ``[SDOC-SSS-77]`` :ref:`SDOC-SSS-77`
- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

.. _SDOC-SRS-47:

At least one integration or end-to-end test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-47
    * - **STATUS:**
      - Active

Every update to the StrictDoc codebase shall be complemented with a corresponding provision of at least one test as follows:

- For web interface: at least one end-to-end test.
- For command-line interface: at least one black-box integration test.
- For internal Python functions: at least one unit test.

NOTE: This requirement implies that no modifications to StrictDoc's functionality can be merged unless accompanied by at least one test.

**RATIONALE:**

This requirement ensures that every new feature or a chance in the codebase is covered/stressed by at least one test, according to the change type.

**Parents:**

- ``[SDOC-SSS-77]`` :ref:`SDOC-SSS-77`
- ``[SDOC-SSS-78]`` :ref:`SDOC-SSS-78`

Code hosting and distribution
=============================

.. _SECTION-SRS-Code-hosting:

Code hosting
------------

.. _SDOC-SRS-12:

GitHub
~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-12
    * - **STATUS:**
      - Active

StrictDoc's source code shall be hosted on GitHub.

**Parents:**

- ``[SDOC-SSS-38]`` :ref:`SDOC-SSS-38`
- ``[SDOC-SSS-82]`` :ref:`SDOC-SSS-82`

.. _SDOC-SRS-118:

StrictDoc license
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-118
    * - **STATUS:**
      - Active

All StrictDoc software shall be licensed under the Apache 2 license.

**Parents:**

- ``[SDOC-SSS-40]`` :ref:`SDOC-SSS-40`
