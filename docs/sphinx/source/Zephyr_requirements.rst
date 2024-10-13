Technical Note: Zephyr requirements tool requirements
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

.. _ZEP-1:

Multiple files / include mechanism
==================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 68e87901205c4b0dbb6a0071479330b5
    * - **UID:**
      - ZEP-1
    * - **STATUS:**
      - Active

Requirements or groups of requirements shall be distributable over several files and still form a full specification (document) via some kind of include mechanism.

**RATIONALE:**

In a future constellation the requirements shall be written resp. update with the code in the same PR. Smallish requirements files per topic / component next to the code in the same repo allow a better workflow than one huge requirements file somewhere.

**Children:**

- ``[SDOC-SSS-52]`` :ref:`SDOC-SSS-52`

.. _ZEP-2:

Clear separation of requirements (machine-readable)
===================================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 36415af620f645388af4dc51c2a19b97
    * - **UID:**
      - ZEP-2
    * - **STATUS:**
      - Active

Requirements objects shall be clearly separated from each other, also when organized in the same file.

**RATIONALE:**

For exporting or machine processing, a clear separation of requirements objects is a prerequisite.

**Children:**

- ``[SDOC-SSS-54]`` :ref:`SDOC-SSS-54`

.. _ZEP-3:

Custom fields
=============

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 7a9e26240f5c4fe29143cf3348ac3d3b
    * - **UID:**
      - ZEP-3
    * - **STATUS:**
      - Active

Requiremements objects shall be configurable to create several types with a number of custom fields.

**RATIONALE:**

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

    * - **MID:**
      - a5928d6204a84d02a3c367d6dbc54092
    * - **UID:**
      - ZEP-4
    * - **STATUS:**
      - Active

Linking shall in general be supported between any requirement object of any object type in a 1:n manner.

**RATIONALE:**

A SAIS requirement will link to a SRS requirement via «refines» link. A SITS test case will link to the same SAIS requirement.

**Children:**

- ``[SDOC-SSS-7]`` :ref:`SDOC-SSS-7`

.. _ZEP-5:

Multiple link roles
===================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 55bbe693d12d4e00956d41a837ef15ef
    * - **UID:**
      - ZEP-5
    * - **STATUS:**
      - Active

Links shall be configurable to create multiple link roles.

**RATIONALE:**

Link roles and requirements object types allow to verify, that the traceability is consistent.

**Children:**

- ``[SDOC-SSS-8]`` :ref:`SDOC-SSS-8`

.. _ZEP-6:

ReqIF export
============

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - b58c387f3a2d4cf6a540e279dbe49e47
    * - **UID:**
      - ZEP-6
    * - **STATUS:**
      - Active

Requirements specification shall be exportable to ReqIF.

**RATIONALE:**

Will/may be used to as exchange format to generate a requirements and traceability documentation.

**Children:**

- ``[SDOC-SSS-58]`` :ref:`SDOC-SSS-58`

.. _ZEP-7:

CSV
===

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 17a141add32f4d7696b5a74b6507b9aa
    * - **UID:**
      - ZEP-7
    * - **STATUS:**
      - Active

Requirements specification shall be exportable to CSV.

**RATIONALE:**

Will/may be used to as exchange format to generate a requirements and traceability documentation.

**Children:**

- ``[SDOC-SSS-59]`` :ref:`SDOC-SSS-59`

.. _ZEP-8:

Unique ID management
====================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - d0d258d8640443578c7ec508c014b50d
    * - **UID:**
      - ZEP-8
    * - **STATUS:**
      - Active

Requirements objects shall allow unique ID management when adding new requirements on different branches.

Options could be:

- UUID: no checking required, but not handy
- Manually assigned: collision checking required
- Centralized: when not affected by branching".

**RATIONALE:**

Centralized object ID management might collide with a branching, PR, merging process approach commonly used in the rest of the project.

**Children:**

- ``[SDOC-SSS-6]`` :ref:`SDOC-SSS-6`

.. _ZEP-9:

Text formatting capabilities
============================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 611546bf2409417e8844f93854d54268
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

**RATIONALE:**

In some cases a plain text requirement is not sufficiently clear and requires formatting or even UML diagrams.

**Children:**

- ``[SDOC-SSS-63]`` :ref:`SDOC-SSS-63`

.. _ZEP-10:

Minimal requirement field set
=============================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - f1f6da87da5c49d1b8c3441b14863975
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

**RATIONALE:**

TBD

**Children:**

- ``[SDOC-SSS-61]`` :ref:`SDOC-SSS-61`

.. _ZEP-11:

Requirements to source code traceability
========================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 55cbd9b658164414adb0c13b0446e3f7
    * - **UID:**
      - ZEP-11
    * - **STATUS:**
      - Active

Linking from requirements objects to code or from code to requirements objects via ID shall be supported.

**RATIONALE:**

For safety development and certification linking to code is required.

**Children:**

- ``[SDOC-SSS-72]`` :ref:`SDOC-SSS-72`

.. _ZEP-12:

Non-intrusive links in source code
==================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - a2930225168147808e6554a4da49aeb4
    * - **UID:**
      - ZEP-12
    * - **STATUS:**
      - Active

Linking from code to requirements objects via ID shall be least code intrusive.

**RATIONALE:**

Code with lots of meta information in it via comment tags, makes the code less readable. Links should best be hidden in existing comment structures e.g. function headers and not be extra tags.

**Children:**

- ``[SDOC-SSS-72]`` :ref:`SDOC-SSS-72`

.. _ZEP-13:

Structuring requirements in documents
=====================================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 2614d6673a594da995df672e8943839e
    * - **UID:**
      - ZEP-13
    * - **STATUS:**
      - Active

Requirements objects shall be structurable in a document like manner (with requirements ordering, and organized in chapters).

**RATIONALE:**

A collection of unorganized requirements as a specifications are hard to read and understand. They should be organizable in topic chapters or similar.

**Children:**

- ``[SDOC-SSS-64]`` :ref:`SDOC-SSS-64`

.. _ZEP-14:

Status field
============

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - a92a28ce3bcb4b3590f36e778a604ccb
    * - **UID:**
      - ZEP-14
    * - **STATUS:**
      - Active

Each requirements object type shall have a configurable status workflow.

**RATIONALE:**

Requirements may be in different statuses such as Draft, InReview, Approved. Dependent on the used process is rather reflected in the development work (branch=draft, PR under Review=InReview, PR merged to main=Approved.

**Children:**

- ``[SDOC-SSS-61]`` :ref:`SDOC-SSS-61`

.. _ZEP-15:

Tool Qualifiability
===================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - b74919612283422a9e139418a20926c6
    * - **UID:**
      - ZEP-15
    * - **STATUS:**
      - Active

The Requirement Tool shall be qualifiable for use in safety-related and/or security-related development. At the very least, the Requirement Tool shall come with its own set of requirements, which shall be amenable to validation in compliance with the relevant standards.

**RATIONALE:**

Certification of Zephyr-based products.

**Children:**

- ``[SDOC-SSS-50]`` :ref:`SDOC-SSS-50`
