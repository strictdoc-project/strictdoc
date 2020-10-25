Requirements
$$$$$$$$$$$$

Problems
========

Technical documentation software
--------------------------------

``[PROBLEM-1-TOOLS]``

There shall exist free and lightweight yet capable software for technical
documentation.

**Comment:** The state of the art for many small companies working with
requirements: using Excel for requirements management in the projects with
hundreds or thousands of requirements.

Technical documentation is hard
-------------------------------

``[PROBLEM-2-DOCUMENTATION-IS-HARD]``

Software shall support engineers in their work with documentation.

**Comment:** Technical documentation can be an extremely laborious process.

Technical documentation as a source of hazards
----------------------------------------------

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
-----------------------------------------------

``[PROBLEM-4-OUTDATED-DOCUMENTATION]``

Software shall support engineers in keeping documentation up-to-date.

**Comment:** Many existing tools for documentation do not provide any measures for
ensuring overall consistency of documents and documentation trees.

Change management is difficult
------------------------------

``[PROBLEM-5-CHANGE-MANAGEMENT]``

Software shall provide capabilities for change management and impact assessment.

**Comment:** The bigger the project is, the harder it is to maintain its documentation.
If a change is introduced to a project, it usually requires a full revision
of its requirements TBD.

High-level requirements
=======================

Requirements management
-----------------------

``[SDOC-HIGH-REQS-MANAGEMENT]``

StrictDoc shall enable requirements management.

Data model
----------

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
----------------------

StrictDoc shall provide a command-line interface.

Requirements validation
-----------------------

StrictDoc shall allow validation of requirement documents.

Requirements text format
------------------------

StrictDoc shall allow storage of requirements in a plain-text human readable form.

Linking requirements
--------------------

StrictDoc shall support linking requirements to each other.

Scalability
-----------

StrictDoc shall allow working with large documents and document trees containing at least 10000 requirement items.

Traceability
------------

``[SDOC-HIGH-REQS-TRACEABILITY]``

StrictDoc shall support traceability of requirements.

Visualization
-------------

StrictDoc shall provide means for visualization of requirement documents.

Open source software
--------------------

StrictDoc shall always be free and open source software.

Implementation requirements
===========================

Parallelization
---------------

``[SDOC-IMPL-PARAL]``

StrictDoc shall enable parallelization of the time-consuming parts of the code.

Incremental generation
----------------------

``[SDOC-IMPL-INCREMENTAL]``

StrictDoc shall enable incremental generation of the documents.

Data model
==========

Modeling capability
-------------------

``[SDOC-DM-001]``

StrictDoc's Data Model shall accommodate for maximum possible standard requirement document formats.


Examples of standard requirements documents include but are not limited to:

- Non-nested requirement lists split by categories
  (e.g., Functional Requirements, Interface Requirements, Performance Requirements, etc.)

Section item
------------

Requirement item
----------------

Statement
~~~~~~~~~

Requirement item shall have a statement.

Content body
~~~~~~~~~~~~

Requirement item might have an content body.

UID identifier
~~~~~~~~~~~~~~

Requirement item might have an UID identifier.

UID identifier format
^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall not impose any restrictions on the UID field format.

**Comment:** Conventions used for requirement UIDs can be very different. And there seems to
be no way to define a single rule.

Some examples:

- FUN-003
- cES1008, cTBL6000.1 (NASA cFS)
- Requirements without a number, e.g. SDOC-HIGH-DATA-MODEL (StrictDoc)

Title
~~~~~

Requirement item might have an title.

References
~~~~~~~~~~

Requirement item might have one or more references.

Comments
~~~~~~~~

Requirement item might have one or more comments.

Composite Requirement item
--------------------------

TBD

SDOC file format
================

Primary text implementation
---------------------------

``[SDOC-RDF-001]``

SDOC format shall support encoding the Strict Doc Data Model in a plain-text human readable form.

Grammar
-------

SDOC format shall be based on a fixed grammar.

Type safety
-----------

SDOC format shall allow type-safe encoding of requirement documents.

Document Generators
===================

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

Single document: Deep traceability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall export deep traceability document.

PDF Export
----------

Sphinx documentation generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support exporting documents to Sphinx/RST format.

