Requirements
$$$$$$$$$$$$

High-level Requirements
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

- Doorstop
- StrictDoc, first generation: Markdown-based C++ program.
- StrictDoc, second generation: RST/Sphinx-based Python program. Using Sphinx
  extensions to manage meta information.

Requirements validation
-----------------------

StrictDoc shall allow validation of requirement documents.

Requirements text format
------------------------

StrictDoc shall allow storage of requirements in text form.

Linking requirements
--------------------

StrictDoc shall support linking requirements to each other.

Traceability
------------

``[SDOC-HIGH-REQS-TRACEABILITY]``

StrictDoc shall support traceability of requirements.

Visualization
-------------

StrictDoc shall provide means for visualization of requirement documents.

Open Source software
--------------------

StrictDoc shall always be free and open source software.

Data Model
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

Requirements Document Format
============================

Primary text implementation
---------------------------

``[SDOC-RDF-001]``

StrictDoc RDF shall serve as a text-based implementation of the Strict Doc Data Model.

Grammar
-------

StrictDoc RDF shall provide a fixed grammar structure.

Type safety
-----------

StrictDoc RDF shall enable type-safe parsing of requirement documents.

HTML Export
===========

Single document: Normal form
----------------------------

StrictDoc shall export single document pages in a normal document-like form.

Single document: Tabular form
-----------------------------

StrictDoc shall export single document pages in a tabular form.

Single document: 1-level traceability
-------------------------------------

StrictDoc shall export 1-level traceability document.

Single document: Deep traceability
----------------------------------

StrictDoc shall export deep traceability document.

PDF Export
==========

Sphinx documentation generator
------------------------------

StrictDoc shall support exporting documents to Sphinx/RST format.

