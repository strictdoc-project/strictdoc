StrictDoc Development Plan
$$$$$$$$$$$$$$$$$$$$$$$$$$

This document presents the goals of the StrictDoc project and describes how the
project is developed.

Project goals
=============

StrictDoc is an attempt to create an open source tool for writing
technical requirements specifications.

.. _GOAL-1-TOOL-SUPPORT:

Software support for writing requirements and specifications documents
----------------------------------------------------------------------

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
----------------------------

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
-----------------------------------

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
-----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - GOAL-4-CHANGE-MANAGEMENT

Software shall provide capabilities for change management and impact assessment.

**Comment:** Change management is difficult. The bigger the project is, the harder it is to
maintain its documentation. If a change is introduced to a project, it usually
requires a full revision of its requirements.

**Comment:** When the basic capabilities of StrictDoc are in place, it should be possible
to do a more advanced analysis of requirements and requirement trees:

- Finding similar or relevant requirements.
- Enforce invariants that should be hold. Example: mass or power budget.

**Children:**

- ``[BACKLOG-FUZZY-SEARCH]`` :ref:`BACKLOG-FUZZY-SEARCH`

Two frontends
=============

There are two frontends for StrictDoc:

1) Text frontend
2) Web frontend

The text frontend is already developed, the web frontend is incubation.

.. _FRONTEND-1-TEXT:

Text frontend
-------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - FRONTEND-1-TEXT

...

**Children:**

- ``[BACKLOG-LSP]`` :ref:`BACKLOG-LSP`

.. _FRONTEND-2-WEB:

Web frontend
------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - FRONTEND-2-WEB

...

**Children:**

- ``[BACKLOG-WEB]`` :ref:`BACKLOG-WEB`

Development team
================

StrictDoc is a spare time project developed and maintained by a single person
with occasional contributions from the Open Source community.

