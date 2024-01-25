Technical Note: Zephyr requirements tool requirements
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

.. _ZEP-1:

Multiple files / include mechanism
==================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-1
    * - **STATUS:**
      - Active

Requirements or groups of requirements shall be distributable over several files and still form a full specification (document) via some kind of include mechanism.

**Rationale:**

In a future constellation the requirements shall be written resp. update with the code in the same PR. Smallish requirements files per topic / component next to the code in the same repo allow a better workflow than one huge requirements file somewhere.

**Children:**

- ``[SDOC-SSS-52]`` :ref:`SDOC-SSS-52`

.. _ZEP-2:

Clear separation of requirements (machine-readable)
===================================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-2
    * - **STATUS:**
      - Active

Requirements objects shall be clearly separated from each other, also when organized in the same file.

**Rationale:**

For exporting or machine processing, a clear separation of requirements objects is a prerequisite.

**Children:**

- ``[SDOC-SSS-54]`` :ref:`SDOC-SSS-54`

.. _ZEP-3:

Custom fields
=============

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-3
    * - **STATUS:**
      - Active

Requiremements objects shall be configurable to create several types with a number of custom fields.

**Rationale:**

Requirements on software level may need to hold different information than on the architecture/interface and on the component level.
By having typed requirements objects, linkages between requirements objects can be verified and filtered (start_object_type – link_role_type --> end_object_type)".

**Children:**

- ``[SDOC-SSS-62]`` :ref:`SDOC-SSS-62`

.. _ZEP-4:

Links
=====

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-4
    * - **STATUS:**
      - Active

Linking shall in general be supported between any requirement object of any object type in a 1:n manner.

**Rationale:**

A SAIS requirement will link to a SRS requirement via «refines» link. A SITS test case will link to the same SAIS requirement.

**Children:**

- ``[SDOC-SSS-7]`` :ref:`SDOC-SSS-7`

.. _ZEP-5:

Multiple link roles
===================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-5
    * - **STATUS:**
      - Active

Links shall be configurable to create multiple link roles.

**Rationale:**

Link roles and requirements object types allow to verify, that the traceability is consistent.

**Children:**

- ``[SDOC-SSS-8]`` :ref:`SDOC-SSS-8`

.. _ZEP-6:

ReqIF export
============

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-6
    * - **STATUS:**
      - Active

Requirements specification shall be exportable to ReqIF.

**Rationale:**

Will/may be used to as exchange format to generate a requirements and traceability documentation.

**Children:**

- ``[SDOC-SSS-58]`` :ref:`SDOC-SSS-58`

.. _ZEP-7:

CSV
===

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-7
    * - **STATUS:**
      - Active

Requirements specification shall be exportable to CSV.

**Rationale:**

Will/may be used to as exchange format to generate a requirements and traceability documentation.

**Children:**

- ``[SDOC-SSS-59]`` :ref:`SDOC-SSS-59`

.. _ZEP-8:

Unique ID management
====================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-8
    * - **STATUS:**
      - Active

Requirements objects shall allow unique ID management when adding new requirements on different branches.

Options could be:

- UUID: no checking required, but not handy
- Manually assigned: collision checking required
- Centralized: when not affected by branching".

**Rationale:**

Centralized object ID management might collide with a branching, PR, merging process approach commonly used in the rest of the project.

**Children:**

- ``[SDOC-SSS-6]`` :ref:`SDOC-SSS-6`

.. _ZEP-9:

Text formatting capabilities
============================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-9
    * - **STATUS:**
      - Active

The description field shall allow for formatting such as:

- lists
- tables
- headings
- UML diagrams
- etc.

**Rationale:**

In some cases a plain text requirement is not sufficiently clear and requires formatting or even UML diagrams.

**Children:**

- ``[SDOC-SSS-63]`` :ref:`SDOC-SSS-63`

.. _ZEP-10:

Minimal requirement field set
=============================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-10
    * - **STATUS:**
      - Active

A requirements object shall at least comprise the following fields (or similar):

- title
- ID
- Description
- Status
- Outbound links
- Inbound links (optional?)

**Rationale:**

TBD

**Children:**

- ``[SDOC-SSS-61]`` :ref:`SDOC-SSS-61`

.. _ZEP-11:

Requirements to source code traceability
========================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-11
    * - **STATUS:**
      - Active

Linking from requirements objects to code or from code to requirements objects via ID shall be supported.

**Rationale:**

For safety development and certification linking to code is required.

**Children:**

- ``[SDOC-SRS-33]`` :ref:`SDOC-SRS-33`

.. _ZEP-12:

Non-intrusive links in source code
==================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-12
    * - **STATUS:**
      - Active

Linking from code to requirements objects via ID shall be least code intrusive.

**Rationale:**

Code with lots of meta information in it via comment tags, makes the code less readable. Links should best be hidden in existing comment structures e.g. function headers and not be extra tags.

**Children:**

- ``[SDOC-SRS-124]`` :ref:`SDOC-SRS-124`

.. _ZEP-13:

Structuring requirements in documents
=====================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-13
    * - **STATUS:**
      - Active

Requirements objects shall be structurable in a document like manner (with requirements ordering, and organized in chapters).

**Rationale:**

A collection of unorganized requirements as a specifications are hard to read and understand. They should be organizable in topic chapters or similar.

**Children:**

- ``[SDOC-SSS-64]`` :ref:`SDOC-SSS-64`

.. _ZEP-14:

Status field
============

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-14
    * - **STATUS:**
      - Active

Each requirements object type shall have a configurable status workflow.

**Rationale:**

Requirements may be in different statuses such as Draft, InReview, Approved. Dependent on the used process is rather reflected in the development work (branch=draft, PR under Review=InReview, PR merged to main=Approved.

**Children:**

- ``[SDOC-SSS-61]`` :ref:`SDOC-SSS-61`

.. _ZEP-15:

Tool Qualifiability
===================

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - ZEP-15
    * - **STATUS:**
      - Active

The Requirement Tool shall be qualifiable for use in safety-related and/or security-related development. At the very least, the Requirement Tool shall come with its own set of requirements, which shall be amenable to validation in compliance with the relevant standards.

**Rationale:**

Certification of Zephyr-based products.

**Children:**

- ``[SDOC-SSS-50]`` :ref:`SDOC-SSS-50`
