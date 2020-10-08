StrictDoc
$$$$$$$$$

High-level Requirements
=======================

Requirements management
-----------------------

``[SDOC-HIGH-REQS-MANAGEMENT]``

StrictDoc shall enable requirements management.

**Comment:** Under this requirement, StrictDoc shall enable work with requirements in a structured manner.

Requirements validation
-----------------------

StrictDoc shall allow validation of requirement documents.

Requirements text format
------------------------

StrictDoc shall allow storage of requirements in a text format.

Linking requirements
--------------------

StrictDoc shall support linking requirements to each other.

Linking with implementation artefacts
-------------------------------------

StrictDoc shall support linking requirements to files.

Traceability
------------

``[SDOC-HIGH-REQS-TRACEABILITY]``

StrictDoc shall support traceability of requirements.

Visualization
-------------

StrictDoc shall provide means for visualization of requirement documents.

Documentation coverage
----------------------

StrictDoc shall generate requirements coverage information.

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
- ESA Statement of Work documents

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

Title
~~~~~

Requirement item might have an title.

References
~~~~~~~~~~

Requirement item might have one or more references.

Comments
~~~~~~~~

Requirement item might have one or more comments.

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

