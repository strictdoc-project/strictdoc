Requirements Tool Specification (L1)
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

The StrictDoc project is structured around two distinct requirement documents that guide its development:

1. The "Requirements Tool Specification" (this document), which is a higher-level document.
2. The "StrictDoc Requirements Specification," a more detailed and lower-level document, separate from this one.

This document, the Requirements Tool Specification, delineates the general requirements for an open-source Requirements Tool, with a focus that remains agnostic of the specific implementation details of StrictDoc. Its primary goal is to provide a comprehensive, implementation-neutral overview of what capabilities a Requirements Tool should possess, emphasizing the 'WHAT' aspect.

In contrast, the StrictDoc Requirements Specification, the second document, delves deeply into the 'HOW' aspect of StrictDoc’s implementation. It builds upon the high-level requirements set out in this document, treating them as parent requirements to guide its detailed development approach.

Summary of user needs
=====================

This section offers an overview of the necessary capabilities of a requirements and documentation management tool.

Free and open source tool
-------------------------

The primary user need and entry point for this Requirements Tool specification is the availability of free, lightweight, yet capable software for creating requirements specifications and other technical documentation. The tool should facilitate the creation of requirements specifications and technical documents, effectively lowering the entry barrier for requirements engineering and technical documentation writing.

It is assumed throughout this document that the requirements tool will be developed as open-source software available at no cost. However, with minor adjustments, these requirements could also apply to commercial requirements tools. See :ref:`Licensing and distribution <SECTION-SSSS-Licensing-and-distribution>`.

Document types
--------------

A requirements tool is very often also a documentation writing and management tool, so, besides the requirements editing functionality, the tool shall be able to accommodate for the variety of documents and templates used in different industries.

The variety comes from:

- Supporting arbitrary documentation structures, e.g., non-nested vs. deeply nested documents.
- Supporting a rich set of visualization mechanisms. Supporting images, diagrams, tables, text markup, etc.
- Supporting custom fields/attributes used by different industries (the criticality levels in various industries, RAIT verification activities in aerospace, status/workflow fields, etc.).

Examples of typical document types include:

- Requirements specification
- Design document / architecture description document
- Interface control document / API reference
- User manual
- Development plan
- Systems engineering plan, management plan
- Standard (e.g., ECSS or ISO 26262).

The documentation/requirements management requirements for a Requirements Tool are specified in the sections :ref:`Documentation management <SECTION-RTS-Documentation-management>` and :ref:`Requirements management <SECTION-RTS-Requirements-management>`.

.. _SECTION-RTC-Appendix-A-Document-archetypes:

Document structure differences
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The table below summarizes various differences observed across industry documents.

.. list-table:: Table: Requirements and specification document
   :widths: 20 80
   :header-rows: 1

   * - Criteria
     - Comments

   * - Structure
     - Non-nested, nested, deeply nested. A structure of a deeply nested specification document can reach 8-10 levels (e.g., Section 1.2.3.4.5.6.7.8 "ABC").
   * - Requirements visual presentation
     - Requirements are often presented as table cells. The cells can be standalone or a whole section or a document can be a structured as a long table with cells. Alternatively, requirements are rather presented as a section header + text.
   * - Unique requirement identifiers (UID)
     - Some documents provide UIDs for all requirements, some do not. Where the UIDs are missing, the section header numbers are used instead for unique identification. Often, a combination "Number + Title" becomes a reference-able identifier.
   * - Requirement titles
     - Not all documents provide requirement titles. When the requirement titles are missing, the grouping is may be provided by sections/chapters. When the titles are present, the requirement titles can also be section titles.

.. _SECTION-LRTS-Workflows:

Workflows
---------

Besides supporting a variety of document types, a Requirements Tool shall also support and integrate well with multiple documentation and requirements management workflows.

At least the following workflows have been identified to be relevant:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - **Workflow**
     - **Description**

   * - Requirements analysis and prototyping
     - Early phases of the project. Requirements are drafted out quickly. The higher-level picture and coverage of all topics may be more important than specific details.
   * - Requirements compliance, traceability and justification
     - Demonstrating the correctness of specification, also for contractual purposes. Every aspect shall be traceable.
   * - Requirements implementation
     - Assisting software engineers in implementing requirements in source code. Making links between requirements and source code implementation units, e.g., files, functions, code fragments. Linking source code implementation units to requirements using special markers left in source code.
   * - Requirements validation/verification workflow (RAIT)
     - Verifying the correctness of requirements themselves and the validity of the information they communicate.
   * - Configuration management, change management
     - Time machine and Diff functions. Maintaining requirements baselines (v1, v1.1, v2, etc.).
   * - Reporting
     - Progress reports, statistics, metrication.
   * - Collaboration on requirements
     - Supporting multiple users to collaborate on a documentation tree.
   * - Requirements exchange
     - Integration between distinct projects requirements trees. Example: An embedded software project has its own requirements. The developers want to integrate a requirements subtree of another product that is integrated to the parent project as an off-the-shelf solution.
   * - Formal reviews
     - Formal review of documentation. Walkthroughs, inspections. Version control of delivered documentation packages. Assessment of progress reports achieved.
   * - Interoperability with industry standards.
     - Supporting seamless integration between a project documentation tree and applicable standards.

The section :ref:`Existing workflows <SECTION-SSSS-Existing-workflows>` contains the workflow-related requirements for a Requirements Tool.

Target audience
---------------

A Requirements Tool may have different users, each with a different role, experience and background which necessitates the requirements towards usability, installation, and user experience.

The following user groups are preliminarily identified as especially relevant:

**Engineering professionals**

This group includes:

- Systems engineers
- Requirements engineers
- Assurance experts in quality, safety/security, verification/validation

For these professionals, the Requirements Tool should offer robust functionality that is adequate for complex system design and detailed requirements tracking, ensuring that all aspects of system integrity and compliance are met efficiently.

**Management**

The focus of this group is more on the progress and compliance aspects. They require high-level overviews and reporting capabilities in the tool, to track project milestones, manage risks, and ensure that the development is adhering to the predefined requirements and industry standards.

**Software engineers**

For software engineers, the Requirements Tool shall be closely integrated with their software engineering workflow, e.g., it has interfaces with software version control systems, software IDEs, and source code repositories. This integration ensures a seamless transition between requirement specification and software development tasks.

**IT/DevOps**

This group of users may not work with a Requirements Tool directly but is still an important stakeholder. The Tool shall be easy to install and deploy. It shall be easy to maintain and upgrade the tool, with support for automated updates and compatibility with various IT infrastructures.

**General audience**

Not all users of a requirements tool must have an engineering background. In fact, there are many projects where non-technical people have to maintain requirements. The Requirements Tool shall be usable without any technical training required, featuring an intuitive user interface and simplified processes for entering and managing requirements.

The requirement sets in the sections :ref:`Usability, installation and usage <SECTION-RTC-Usability-installation-and-usage>` and :ref:`Implementation suggestions <SECTION-SSSS-Implementation-suggestions>` aim to equip the Requirements Tool with sufficient capabilities to support all of the user groups described above.

.. _SECTION-RTS-Documentation-management:

Documentation management
========================

This section outlines the requirements towards a Requirements Tool as a documentation tool.

The requirements of this group are dedicated to the core tasks of documentation management:

- Writing, structuring and managing documents
- Complementing documents with meta information
- Versioning documents.

.. _SDOC-SSS-3:

Documents (CRUD)
----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-3
    * - **STATUS:**
      - Active

The Requirements Tool shall provide the CRUD operations for document management:

- Create document
- Read document
- Update document
- Delete document.

**RATIONALE:**

The CRUD operations are essential operations of document management. They are at the core of a documentation management tool.

**Children:**

- ``[SDOC-SRS-135]`` :ref:`SDOC-SRS-135`
- ``[SDOC-SRS-107]`` :ref:`SDOC-SRS-107`
- ``[SDOC-SRS-108]`` :ref:`SDOC-SRS-108`
- ``[SDOC-SRS-54]`` :ref:`SDOC-SRS-54`
- ``[SDOC-SRS-106]`` :ref:`SDOC-SRS-106`

.. _SDOC-SSS-91:

Browsing documentation tree
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-91

The Requirements Tool shall provide browsing of the documentation tree.

**Children:**

- ``[SDOC-SRS-53]`` :ref:`SDOC-SRS-53`

.. _SDOC-SSS-51:

Documents with nested sections/chapters structure
-------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-51
    * - **STATUS:**
      - Active

The Requirements Tool shall allow management of documents with nested sections/chapters structure.

**Children:**

- ``[SDOC-SRS-99]`` :ref:`SDOC-SRS-99`

.. _SDOC-SSS-52:

Assembling documents from fragments
-----------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-52
    * - **STATUS:**
      - Active

The Requirements Tool shall allow composing documents from other documents or fragments.

NOTE: If a Requirements Tool implements stores documents in a file system, the composition can be arranged at a file level when a parent document file includes the child fragment files and produces a composite document.

**RATIONALE:**

Composable documents allow assembling documents from multiple smaller documents which can be standalone documents or document fragments. This feature is particularly useful for managing extensive documents that can be more effectively organized and handled when divided into smaller document sections.

**Parents:**

- ``[ZEP-1]`` :ref:`ZEP-1`

**Children:**

- ``[SDOC-SRS-109]`` :ref:`SDOC-SRS-109`
- ``[SDOC-SRS-122]`` :ref:`SDOC-SRS-122`

.. _SDOC-SSS-53:

Document meta information (UID, version, authors, signatures, etc)
------------------------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-53
    * - **STATUS:**
      - Active

The Requirements Tool shall support management of document meta information.

**Children:**

- ``[SDOC-SRS-110]`` :ref:`SDOC-SRS-110`

.. _SDOC-SSS-75:

Document versioning
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-75
    * - **STATUS:**
      - Active

The Requirements Tool shall provide capabilities for document versioning.

**Children:**

- ``[SDOC-SRS-110]`` :ref:`SDOC-SRS-110`
- ``[SDOC-SRS-111]`` :ref:`SDOC-SRS-111`

.. _SDOC-SSS-63:

Text formatting capabilities
----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-63

The Requirements Tool shall provide "rich text" formatting capabilities which includes but not limited to:

- Headings
- Lists
- Tables
- UML diagrams
- etc.

**Parents:**

- ``[ZEP-9]`` :ref:`ZEP-9`

**Children:**

- ``[SDOC-SRS-24]`` :ref:`SDOC-SRS-24`
- ``[SDOC-SRS-27]`` :ref:`SDOC-SRS-27`

.. _SECTION-RTS-Requirements-management:

Requirements management
=======================

This section outlines the requirements towards a Requirements Tool as a requirements management tool.

The following core aspects of the requirements management are covered:

- Writing and structuring requirements
- Linking requirements with other requirements
- Managing requirement unique identifiers (UID)
- Requirement verification.

.. _SDOC-SSS-4:

Requirements CRUD
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-4
    * - **STATUS:**
      - Active

The Requirements Tool shall enable the main requirements management operations:

- Create a requirement
- Read / view / browse a requirement
- Update / edit a requirement
- Delete a requirement.

**RATIONALE:**

The CRUD operations are at the core of the requirements management.

**Children:**

- ``[SDOC-SRS-26]`` :ref:`SDOC-SRS-26`
- ``[SDOC-SRS-55]`` :ref:`SDOC-SRS-55`

.. _SDOC-SSS-61:

Minimal requirement field set
-----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-61
    * - **STATUS:**
      - Active

The Requirements Tool shall support at least the following requirement field set:

- UID
- STATUS
- TITLE
- STATEMENT
- RATIONALE
- COMMENT
- RELATIONS (connections with other requirements).

**RATIONALE:**

The selection of the minimal set is based on what is common in the industries (e.g., automotive, space, etc).

**COMMENT:**

The other fields common to each industry can be customized with custom fields handled by other requirements.

**Parents:**

- ``[ZEP-10]`` :ref:`ZEP-10`
- ``[ZEP-14]`` :ref:`ZEP-14`

**Children:**

- ``[SDOC-SRS-132]`` :ref:`SDOC-SRS-132`
- ``[SDOC-SRS-93]`` :ref:`SDOC-SRS-93`

.. _SDOC-SSS-62:

Custom fields
-------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-62
    * - **STATUS:**
      - Active

The requirements tool shall support configuring a requirement item with an arbitrary set of fields.

NOTE: Examples of typical fields include: UID, Title, Statement, Rationale, Comment. Other fields that are used very often are: Status, Tags, Criticality level, Priority, etc.

**RATIONALE:**

The tool shall not constrain a user in which fields they are able to use for their projects.

**Parents:**

- ``[ZEP-3]`` :ref:`ZEP-3`

**Children:**

- ``[SDOC-SRS-100]`` :ref:`SDOC-SRS-100`
- ``[SDOC-SRS-21]`` :ref:`SDOC-SRS-21`
- ``[SDOC-SRS-56]`` :ref:`SDOC-SRS-56`

.. _SDOC-SSS-64:

Structuring requirements in documents
-------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-64
    * - **STATUS:**
      - Active

The Requirements Tool shall support structuring requirements in documents.

**RATIONALE:**

The industry works with requirements documents. The documents have sections/chapters and requirements.

**Parents:**

- ``[ZEP-13]`` :ref:`ZEP-13`

**Children:**

- ``[SDOC-SRS-98]`` :ref:`SDOC-SRS-98`
- ``[SDOC-SRS-105]`` :ref:`SDOC-SRS-105`

.. _SDOC-SSS-5:

Move requirement nodes within document
--------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-5
    * - **STATUS:**
      - Active

The Requirements Tool shall allow moving nodes (sections, requirements) within the containing document.

**Children:**

- ``[SDOC-SRS-92]`` :ref:`SDOC-SRS-92`

.. _SDOC-SSS-70:

Move nodes between documents
----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-70
    * - **STATUS:**
      - Active

The Requirements Tool shall allow moving nodes (sections, requirements) between documents.

**Children:**

- ``[SDOC-SRS-94]`` :ref:`SDOC-SRS-94`

.. _SDOC-SSS-6:

Auto-provision of Requirement UIDs
----------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-6
    * - **STATUS:**
      - Active

The Requirements Tool shall provide controls for automatic generation of requirements UIDs.

**RATIONALE:**

When a document is large, it becomes harder to manage the assignment of the new requirements identifiers by manually exploring which requirement UID has not been assigned yet. The provision of automatically generated UIDs is a convenience feature that improves the user experience significantly.

**Parents:**

- ``[ZEP-8]`` :ref:`ZEP-8`

**Children:**

- ``[SDOC-SRS-96]`` :ref:`SDOC-SRS-96`
- ``[SDOC-SRS-85]`` :ref:`SDOC-SRS-85`
- ``[SDOC-SRS-120]`` :ref:`SDOC-SRS-120`

.. _SDOC-SSS-7:

Link requirements together
--------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-7

**Parents:**

- ``[ZEP-4]`` :ref:`ZEP-4`

**Children:**

- ``[SDOC-SRS-31]`` :ref:`SDOC-SRS-31`
- ``[SDOC-SRS-28]`` :ref:`SDOC-SRS-28`

.. _SDOC-SSS-8:

Multiple link roles
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-8
    * - **STATUS:**
      - Active

The Requirements Tool shall support the link roles.

Example of roles for a child-to-parent link: "verifies", "implements", "satisfies", etc.

**RATIONALE:**

Different industries maintain custom conventions for naming the relations between requirements and other nodes such as tests or other artefacts.

**Parents:**

- ``[ZEP-5]`` :ref:`ZEP-5`

**Children:**

- ``[SDOC-SRS-101]`` :ref:`SDOC-SRS-101`

.. _SDOC-SSS-71:

Reverse parent links
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-71
    * - **STATUS:**
      - Active

The Requirements Tool shall support the Reverse Parent relationship.

**Children:**

- ``[SDOC-SRS-102]`` :ref:`SDOC-SRS-102`

.. _SDOC-SSS-89:

Unique identification of requirements
-------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-89

The Requirements Tool shall provide means for unique identification of every requirement.

**Children:**

- ``[SDOC-SRS-22]`` :ref:`SDOC-SRS-22`
- ``[SDOC-SRS-29]`` :ref:`SDOC-SRS-29`

.. _SDOC-SSS-47:

Requirements database consistency checks
----------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-47
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a validation mechanism that ensures the integrity of requirements and connections between them.

NOTE: Examples of integrity checks:

- Requirements have correct fields.
- Requirements do not form cycles.
- Requirements only link to other requirements as specified in a project configuration.

**Children:**

- ``[SDOC-SRS-30]`` :ref:`SDOC-SRS-30`
- ``[SDOC-SRS-32]`` :ref:`SDOC-SRS-32`

.. _SDOC-SSS-57:

Requirement syntax validation (e.g. EARS)
-----------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-57
    * - **STATUS:**
      - Active

The Requirements Tool shall provide capabilities for validating requirements according to the EARS syntax.

**Children:**

- ``[SDOC-SRS-116]`` :ref:`SDOC-SRS-116`

Tool configurability
====================

.. _SDOC-SSS-92:

Project-level configuration
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-92

The Requirements Tool shall provide a solution for configuring the project-level options.

NOTE: Examples of project-level options:

- Project title.
- Global settings for the Requirements Tool itself.

**Children:**

- ``[SDOC-SRS-37]`` :ref:`SDOC-SRS-37`
- ``[SDOC-SRS-39]`` :ref:`SDOC-SRS-39`

.. _SDOC-SSS-93:

Document-level configuration
----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-93

The Requirements Tool shall provide a solution for configuring the document-level options.

NOTE: Examples of document-level options:

- Document title
- Requirement prefix.
- Other options local to the content and the presentation of a given document.

**Children:**

- ``[SDOC-SRS-57]`` :ref:`SDOC-SRS-57`

.. _SECTION-SSSS-Performance:

Performance
===========

This section captures the performance requirements towards a Requirements Tool.

.. _SDOC-SSS-13:

Support large requirements sets
-------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-13
    * - **STATUS:**
      - Active

The Requirements Tool shall support requirement trees with at least 10000 requirements.

**Children:**

- ``[SDOC-SRS-32]`` :ref:`SDOC-SRS-32`
- ``[SDOC-SRS-1]`` :ref:`SDOC-SRS-1`
- ``[SDOC-SRS-95]`` :ref:`SDOC-SRS-95`
- ``[SDOC-SRS-2]`` :ref:`SDOC-SRS-2`
- ``[SDOC-SRS-3]`` :ref:`SDOC-SRS-3`
- ``[SDOC-SRS-4]`` :ref:`SDOC-SRS-4`
- ``[SDOC-SRS-5]`` :ref:`SDOC-SRS-5`

.. _SDOC-SSS-14:

Support large project trees
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-14
    * - **STATUS:**
      - Active

The Requirements Tool shall be able to handle documentation packages of at least 100 documents without significant performance degradation.

**Children:**

- ``[SDOC-SRS-32]`` :ref:`SDOC-SRS-32`
- ``[SDOC-SRS-1]`` :ref:`SDOC-SRS-1`
- ``[SDOC-SRS-95]`` :ref:`SDOC-SRS-95`
- ``[SDOC-SRS-2]`` :ref:`SDOC-SRS-2`
- ``[SDOC-SRS-3]`` :ref:`SDOC-SRS-3`
- ``[SDOC-SRS-4]`` :ref:`SDOC-SRS-4`
- ``[SDOC-SRS-5]`` :ref:`SDOC-SRS-5`

.. _SECTION-SSSS-Existing-workflows:

Existing workflows
==================

This section captures the requirements towards specific workflows that a Requirements Tool should support as outlined in :ref:`Workflows <SECTION-LRTS-Workflows>`.

.. _SDOC-SSS-73:

Excel-like viewing and editing of requirements
----------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-73
    * - **STATUS:**
      - Active

The Requirements Tool shall provide an Excel-like user interface for viewing and editing requirements.

NOTE: This interface does not have to be the only or a default interface.

**RATIONALE:**

As recognized by the parent requirement, some requirements-based workflows are naturally easier when the requirements content is presented in a form of a table, as opposed to a document with a nested chapter structure.

**Children:**

- ``[SDOC-SRS-62]`` :ref:`SDOC-SRS-62`

.. _SDOC-SSS-56:

1000-feet view
--------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-56
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a "1000-feet view" kind of requirements visualization.

**RATIONALE:**

Compared to the other visualizations, such a visualization helps to "see the forest for the trees". Seeing requirements and their sections all at once helps to visualize groups of requirements and better understand the relationships between them.

**Children:**

- ``[SDOC-SRS-90]`` :ref:`SDOC-SRS-90`
- ``[SDOC-SRS-113]`` :ref:`SDOC-SRS-113`

.. _SDOC-SSS-28:

Traceability matrices
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-28
    * - **STATUS:**
      - Active

The Requirements Tool shall support generation of traceability matrices.

**Children:**

- ``[SDOC-SRS-65]`` :ref:`SDOC-SRS-65`
- ``[SDOC-SRS-112]`` :ref:`SDOC-SRS-112`

.. _SDOC-SSS-48:

Compliance matrices
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-48
    * - **STATUS:**
      - Active

The Requirements Tool shall allow generating a Compliance Matrix document.

**Children:**

- ``[SDOC-SRS-31]`` :ref:`SDOC-SRS-31`
- ``[SDOC-SRS-102]`` :ref:`SDOC-SRS-102`

.. _SDOC-SSS-29:

Requirements coverage
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-29

**Children:**

- ``[SDOC-SRS-97]`` :ref:`SDOC-SRS-97`

.. _SDOC-SSS-49:

Progress report
---------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-49
    * - **STATUS:**
      - Active

The Requirements Tool shall allow generating a Progress Report document.

NOTE: A progress report document shall include at least the following Key Performance Indicators.

Project-level KPIs:

- Total number of requirements
- Total number of requirements without parent (excluding top-level and derived)
- Total number of TBD/TBC
- Total number of requirements without rationale
- Tags breakdown

Document-level KPIs: the same but per document.

**Children:**

- ``[SDOC-SRS-97]`` :ref:`SDOC-SRS-97`

.. _SDOC-SSS-74:

Change management
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-74

The Requirements Tool shall provide capabilities for change management:

- Visualizing changes between project tree versions.
- Visualizing changes between document versions.
- Visualizing the impact that a changed requirement has on a project tree.

**Children:**

- ``[SDOC-SRS-111]`` :ref:`SDOC-SRS-111`
- ``[SDOC-SRS-131]`` :ref:`SDOC-SRS-131`
- ``[SDOC-SRS-117]`` :ref:`SDOC-SRS-117`

.. _SECTION-RTC-Usability-installation-and-usage:

Usability, installation and usage
=================================

.. _SDOC-SSS-79:

General usability
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-79
    * - **STATUS:**
      - Active

The Requirements Tool shall be accessible to a broad spectrum of users.

NOTE: Factors to consider:

- The cost of a tool.
- The easy of installation.
- The availability of a graphical user interface.
- The availability of a programmatic access to the functions of a tool.
- The interoperability of the tool with other tools.

**RATIONALE:**

A tool that can be used by a large number of people simplifies its adoption and allows more users to work with documentation and requirements.

**Children:**

- ``[SDOC-SRS-50]`` :ref:`SDOC-SRS-50`
- ``[SDOC-SRS-125]`` :ref:`SDOC-SRS-125`
- ``[SDOC-SRS-114]`` :ref:`SDOC-SRS-114`

.. _SDOC-SSS-80:

Easy user experience
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-80
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a smooth user experience.

NOTE: Documentation and requirements management are composite activities that consist of several types of repetitive tasks. A requirements tool user experience should assist in automating these tasks as far as possible and make the overall workflow efficient and precise.

**Children:**

- ``[SDOC-SRS-104]`` :ref:`SDOC-SRS-104`
- ``[SDOC-SRS-50]`` :ref:`SDOC-SRS-50`
- ``[SDOC-SRS-48]`` :ref:`SDOC-SRS-48`
- ``[SDOC-SRS-96]`` :ref:`SDOC-SRS-96`
- ``[SDOC-SRS-59]`` :ref:`SDOC-SRS-59`
- ``[SDOC-SRS-121]`` :ref:`SDOC-SRS-121`
- ``[SDOC-SRS-120]`` :ref:`SDOC-SRS-120`

.. _SDOC-SSS-81:

Support projects with a large number of users
---------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-81
    * - **STATUS:**
      - Active

The Requirements Tool shall be capable of supporting a large number of users.

**RATIONALE:**

Many documentation and requirements projects involve large groups of people. The requirements tool should not become a bottleneck when a number of users grows.

**Children:**

- ``[SDOC-SRS-123]`` :ref:`SDOC-SRS-123`

.. _SDOC-SSS-82:

Individual use (home PC)
------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-82
    * - **STATUS:**
      - Active

The Requirements Tool shall be usable on the normal personal computers, e.g., do not require a special cloud deployment.

**Children:**

- ``[SDOC-SRS-87]`` :ref:`SDOC-SRS-87`
- ``[SDOC-SRS-88]`` :ref:`SDOC-SRS-88`
- ``[SDOC-SRS-12]`` :ref:`SDOC-SRS-12`

.. _SDOC-SSS-83:

Server-based deployments (IT-friendly setup)
--------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-83
    * - **STATUS:**
      - Active

The Requirements Tool shall be deployable to the network of computers, e.g., provide a server instance.

**COMMENT:**

Scaling from smaller setups (e.g., Raspberry PI in an office network) to
larger in-house and cloud-base installations.

**Children:**

- ``[SDOC-SRS-126]`` :ref:`SDOC-SRS-126`

.. _SDOC-SSS-84:

Requirements database
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-84
    * - **STATUS:**
      - Active

The Requirements Tool shall store documentation and requirements data in a database.

**RATIONALE:**

A database allows:

- Persistent storage of documentation/requirements data
- Versioning
- Backups
- Exchange of information and access of the same database by multiple users.

**Children:**

- ``[SDOC-SRS-127]`` :ref:`SDOC-SRS-127`

.. _SDOC-SSS-85:

Programming access via API (Web)
--------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-85
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a Web API interface.

**RATIONALE:**

Besides a direct access to the tool's source code, accessing an API deployed to a server provides additional capabilities for getting and manipulating requirements/documentation content.

**Children:**

- ``[SDOC-SRS-114]`` :ref:`SDOC-SRS-114`

.. _SDOC-SSS-86:

Programming access via API (SDK)
--------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-86
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a Software Development Kit (SDK) that allows customization of the Requirements Tool functions.

NOTE: An SDK provides access to the API of the Requirements Tool. Examples of functions that may be used by the users of the tool:

- Custom import/export functions to/from various requirements/documentation formats.
- Implement custom visualization functions.
- Implement integration with other tools.

**RATIONALE:**

A SDK allows a software engineer to extend the Requirements Tool capabilities.

**Children:**

- ``[SDOC-SRS-125]`` :ref:`SDOC-SRS-125`

.. _SDOC-SSS-87:

Programmatic access to requirements data
----------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-87
    * - **STATUS:**
      - Active

The Requirements Tool shall provide programmatic access to requirements data.

**RATIONALE:**

When the requirements data is accessible by a user directly, it is possible to exchange the data or implement additional scripting procedures.

**Children:**

- ``[SDOC-SRS-127]`` :ref:`SDOC-SRS-127`
- ``[SDOC-SRS-125]`` :ref:`SDOC-SRS-125`

.. _SECTION-SSSS-Implementation-suggestions:

Implementation suggestions
==========================

.. _SDOC-SSS-30:

Static HTML export
------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-30
    * - **STATUS:**
      - Active

The Requirements Tool shall support generation of documentation to static HTML.

**RATIONALE:**

A static HTML export capability enables:

- Viewing requirements in browsers without any additional software.
- Exchanging HTML content as zip between users.
- Publishing HTML content via static website hosting providers (GitHub and GitLab Pages, Read the Docs, Heroku, etc.).

**Children:**

- ``[SDOC-SRS-49]`` :ref:`SDOC-SRS-49`

.. _SDOC-SSS-31:

Graphical user interface (GUI)
------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-31
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a graphical user interface.

**Children:**

- ``[SDOC-SRS-50]`` :ref:`SDOC-SRS-50`

.. _SDOC-SSS-32:

Command-line interface
----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-32
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a command line interface (CLI).

**Children:**

- ``[SDOC-SRS-103]`` :ref:`SDOC-SRS-103`

.. _SDOC-SSS-68:

Web API interface
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-68
    * - **STATUS:**
      - Active

The Requirements Tool shall provide an API interface.

**Children:**

- ``[SDOC-SRS-114]`` :ref:`SDOC-SRS-114`

.. _SDOC-SSS-33:

Version control (Git)
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-33
    * - **STATUS:**
      - Active

The Requirements Tool shall support the software version control systems (e.g., Git).

**RATIONALE:**

- Git allows precise tracking of the changes to the documentation.
- Requirements/documentation content can be release-tagged.
- The "Time machine" function: ability to review the older state of the documentation/requirements tree.

**Children:**

- ``[SDOC-SRS-127]`` :ref:`SDOC-SRS-127`

.. _SDOC-SSS-67:

Support major operating systems
-------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-67
    * - **STATUS:**
      - Active

The Requirements Tool shall support at least the following operating systems:

- Linux
- Windows
- macOS.

**Children:**

- ``[SDOC-SRS-9]`` :ref:`SDOC-SRS-9`
- ``[SDOC-SRS-10]`` :ref:`SDOC-SRS-10`
- ``[SDOC-SRS-11]`` :ref:`SDOC-SRS-11`

.. _SDOC-SSS-69:

Conservative languages for implementation
-----------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-69
    * - **STATUS:**
      - Active

The Requirements Tool shall be implemented using the popular programming languages.

NOTE: Examples of the most popular programming languages:

- Java
- C++
- Python
- JavaScript

**RATIONALE:**

Choosing a less popular programming language can limit the long-term maintainability of the tool.

**COMMENT:**

Examples of less popular programming languages, with all due respect to their powerful features: Haskell, F#, Ada, etc.

**Children:**

- ``[SDOC-SRS-8]`` :ref:`SDOC-SRS-8`

.. _SDOC-SSS-90:

Long-term maintainability of a tool
-----------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-90

The Requirements Tool shall be designed for long-term maintenance.

NOTE: Long-term maintenance aspects to consider:

- Careful selection of the technologies used, e.g., avoid building on too many unrelated technologies at the same time.
- Take into account the existing experience of the development team. Consider the availability of qualified developers in the future.
- Take into account maintainability by the development team as well as the users, e.g., IT/DevOps department.

**Children:**

- ``[SDOC-SRS-73]`` :ref:`SDOC-SRS-73`
- ``[SDOC-SRS-14]`` :ref:`SDOC-SRS-14`
- ``[SDOC-SRS-15]`` :ref:`SDOC-SRS-15`
- ``[SDOC-SRS-16]`` :ref:`SDOC-SRS-16`
- ``[SDOC-SRS-42]`` :ref:`SDOC-SRS-42`

.. _SECTION-RTS-Text-based-requirements-language:

Text-based requirements language (optional)
===========================================

Note: Not all requirements tools must be text-based. But when they are, the
following requirements apply.

.. _SDOC-SSS-88:

Text files for storing documentation and requirements
-----------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-88
    * - **STATUS:**
      - Active

The Requirements Tool shall allow storage of documentation and requirements content using text files.

**Children:**

- ``[SDOC-SRS-18]`` :ref:`SDOC-SRS-18`
- ``[SDOC-SRS-20]`` :ref:`SDOC-SRS-20`

.. _SDOC-SSS-55:

Strict text language syntax
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-55
    * - **STATUS:**
      - Active

The Requirements Tool shall provide a strict syntax for its text language.

**Children:**

- ``[SDOC-SRS-19]`` :ref:`SDOC-SRS-19`
- ``[SDOC-SRS-23]`` :ref:`SDOC-SRS-23`
- ``[SDOC-SRS-25]`` :ref:`SDOC-SRS-25`

.. _SDOC-SSS-54:

Machine-readable format
-----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-54
    * - **STATUS:**
      - Active

The Requirement Tool's text language shall be machine-readable.

**Parents:**

- ``[ZEP-2]`` :ref:`ZEP-2`

**Children:**

- ``[SDOC-SRS-19]`` :ref:`SDOC-SRS-19`

.. _SDOC-SSS-34:

Requirements data from multiple repositories
--------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-34
    * - **STATUS:**
      - Active

The Requirement Tool shall allow reading requirements files from multiple folders or repositories.

NOTE: The folders/repositories can be arbitrarily nested.

**Children:**

- ``[SDOC-SRS-115]`` :ref:`SDOC-SRS-115`

.. _SECTION-RTS-Requirements-and-source-code:

Requirements and source code
============================

.. _SDOC-SSS-72:

Traceability between requirements and source code
-------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-72
    * - **STATUS:**
      - Active

The Requirements Tool shall support bi-directional tracing between requirements content and implementation source code.

NOTE: The Requirements Tool does not necessarily have to implement the complete tracing process. It may delegate parts of the traceability task to other tools, e.g., Doxygen, Lobster.

**Children:**

- ``[SDOC-SRS-33]`` :ref:`SDOC-SRS-33`
- ``[SDOC-SRS-34]`` :ref:`SDOC-SRS-34`
- ``[SDOC-SRS-35]`` :ref:`SDOC-SRS-35`
- ``[SDOC-SRS-36]`` :ref:`SDOC-SRS-36`

.. _SECTION-RTS-Requirements-exchange-formats-export-import:

Requirements exchange formats (export/import)
=============================================

This section captures the requirements related to "Requirements exchange" as outlined in the section :ref:`Workflows <SECTION-LRTS-Workflows>`.

The Requirements Tool should fundamentally support the exchange of documentation and requirements with other tools. Importing data into this tool and exporting data from it to other tools should be straightforward. The key focus of this section's requirements is on enabling seamless access to requirements and documentation data.

.. _SDOC-SSS-58:

ReqIF export/import
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-58
    * - **STATUS:**
      - Active

The Requirements Tool shall support exporting/importing requirements content from/to ReqIF format.

**RATIONALE:**

ReqIF is a standard for exchanging requirements. There is currently no other standard of a higher maturity.

**Parents:**

- ``[ZEP-6]`` :ref:`ZEP-6`

**Children:**

- ``[SDOC-SRS-18]`` :ref:`SDOC-SRS-18`
- ``[SDOC-SRS-72]`` :ref:`SDOC-SRS-72`

.. _SDOC-SSS-59:

CSV export/import
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-59
    * - **STATUS:**
      - Active

The Requirements Tool shall support exporting/importing requirements content from/to CSV.

**Parents:**

- ``[ZEP-7]`` :ref:`ZEP-7`

**Children:**

- ``[SDOC-SRS-129]`` :ref:`SDOC-SRS-129`

.. _SDOC-SSS-60:

Excel export/import
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-60
    * - **STATUS:**
      - Active

The Requirements Tool shall support exporting/importing requirements content from/to Excel.

**Children:**

- ``[SDOC-SRS-74]`` :ref:`SDOC-SRS-74`
- ``[SDOC-SRS-134]`` :ref:`SDOC-SRS-134`

.. _SECTION-RTS-Requirements-collaboration:

Collaboration on requirements
=============================

.. _SDOC-SSS-65:

Support user accounts
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-65
    * - **STATUS:**
      - Draft

**Children:**

- ``[SDOC-SRS-130]`` :ref:`SDOC-SRS-130`

.. _SDOC-SSS-66:

Send notifications about updated requirements
---------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-66
    * - **STATUS:**
      - Draft

**Children:**

- ``[SDOC-SRS-131]`` :ref:`SDOC-SRS-131`

.. _SECTION-SSSS-Development-process:

Development process
===================

.. _SDOC-SSS-76:

Requirements engineering
------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-76
    * - **STATUS:**
      - Active

The Requirements Tool's development process shall include the Requirements Tool's own requirements engineering.

**RATIONALE:**

A requirements tool is not a trivial project. A clear set of requirements for the developed tool helps to structure the development and communicate the functions of the tool to the developers and the users of the tool.

**Children:**

- ``[SDOC-SRS-128]`` :ref:`SDOC-SRS-128`

.. _SDOC-SSS-50:

Self-hosted requirements
------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-50
    * - **STATUS:**
      - Active

The Requirements Tool's requirements shall be developed and stored using the Requirements Tool itself.

**RATIONALE:**

While not strictly necessary, developing the requirements for the tool using the tool itself aids developers in test-driving its functionality during the requirement development phase. Moreover, having the tool host its own requirements provides a tangible and dynamic illustration of how the tool can be employed for crafting requirements documentation.

**Parents:**

- ``[ZEP-15]`` :ref:`ZEP-15`

**Children:**

- ``[SDOC-SRS-91]`` :ref:`SDOC-SRS-91`

.. _SDOC-SSS-77:

Test coverage
-------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-77
    * - **STATUS:**
      - Active

The Requirements Tool's development process shall ensure:

- A testability of the tool.
- The highest possible coverage of the tool's code by test.
- Usage of modern testing methods to ensure adequate coverage of the tool's functions (e.g., command-line interface, web interface, smallest units of code, etc.).

**RATIONALE:**

The presence of tests, the adequate selection of test methods and a high test coverage are preconditions for a high quality of the requirements tool.

**Children:**

- ``[SDOC-SRS-44]`` :ref:`SDOC-SRS-44`
- ``[SDOC-SRS-45]`` :ref:`SDOC-SRS-45`
- ``[SDOC-SRS-46]`` :ref:`SDOC-SRS-46`
- ``[SDOC-SRS-47]`` :ref:`SDOC-SRS-47`

.. _SDOC-SSS-78:

Tool qualification
------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-78
    * - **STATUS:**
      - Active

The Requirements Tool's development process shall ensure that the tool can be qualified for the use in critical product developments as required by the rigorous technical standards (e.g., EN IEC 61508).

**RATIONALE:**

Many project developments require a qualification of the tools used during the development. A requirements tool is one of the critical tools that affect the project development. If a requirement tool is developed to the higher standards of quality, it simplifies the argument of bringing the tool forward and using it in a particular project.

**Children:**

- ``[SDOC-SRS-6]`` :ref:`SDOC-SRS-6`
- ``[SDOC-SRS-133]`` :ref:`SDOC-SRS-133`
- ``[SDOC-SRS-128]`` :ref:`SDOC-SRS-128`
- ``[SDOC-SRS-91]`` :ref:`SDOC-SRS-91`
- ``[SDOC-SRS-40]`` :ref:`SDOC-SRS-40`
- ``[SDOC-SRS-41]`` :ref:`SDOC-SRS-41`
- ``[SDOC-SRS-43]`` :ref:`SDOC-SRS-43`
- ``[SDOC-SRS-44]`` :ref:`SDOC-SRS-44`
- ``[SDOC-SRS-45]`` :ref:`SDOC-SRS-45`
- ``[SDOC-SRS-46]`` :ref:`SDOC-SRS-46`
- ``[SDOC-SRS-47]`` :ref:`SDOC-SRS-47`

.. _SECTION-SSSS-Licensing-and-distribution:

Licensing and distribution
==========================

This section outlines the requirements for the "free and open source" aspect of the Requirements Tool.

.. _SDOC-SSS-38:

Open source
-----------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-38
    * - **STATUS:**
      - Active

The Requirements Tool's source code shall be publicly available, e.g., hosted on a code hosting platform such as GitHub or GitLab.

**Children:**

- ``[SDOC-SRS-12]`` :ref:`SDOC-SRS-12`

.. _SDOC-SSS-39:

Only open source dependencies
-----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-39
    * - **STATUS:**
      - Active

The Requirement Tool's source code shall be based on open source software components.

**Children:**

- ``[SDOC-SRS-89]`` :ref:`SDOC-SRS-89`

.. _SDOC-SSS-40:

Free
----

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SSS-40
    * - **STATUS:**
      - Active

The Requirements Tool shall be licensed under a permissive license, ensuring no/minimal constraints on the utilization and dissemination of the project.

NOTE: Example of a permissive license: MIT, Apache 2.

**RATIONALE:**

This requirement captures the essence of an open and free requirements management tool.

**Children:**

- ``[SDOC-SRS-118]`` :ref:`SDOC-SRS-118`
