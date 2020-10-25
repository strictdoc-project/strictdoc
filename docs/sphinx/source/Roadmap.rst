Roadmap
$$$$$$$

In works
========

PDF Export
----------

PDF Export: TOC sections: bottom alignment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Numbers do not align with titles.

HTML Export
-----------

RST support for text and code blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support rendering text/code blocks into RST syntax.

Left panel: Table of contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Left panel: Table of contents.

Document page CSS: Proper markup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Document page: make it look like a document.

Table page CSS: Proper table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Table page: make columns be always of the same size while respecting min-max widths.

Traceability page CSS: Proper middle column document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Traceability page CSS: Proper middle column document

Deep Traceability page CSS: Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deep Traceability page CSS: Improvements

First public release
====================

Document tree: Incremental generation
-------------------------------------

When exporting documentation tree, StrictDoc shall regenerate only changed documents and files.

Generated file names
--------------------

Document name must be transformed into a valid file name.

**Comment:** Alternative: Simply use the original document file names.

Validation: Uniqueness of UID identifiers in a document tree
------------------------------------------------------------

StrictDoc shall ensure that each UID used in a document tree is unique.

Backlog
=======

StrictDoc as library
--------------------

StrictDoc shall support it use as a Python library.

**Comment:** Such a use allows a more fine-grained access to the StrictDoc's modules, such
as Grammar, Import, Export classes, etc.

Export capabilities
-------------------

Excel Export
~~~~~~~~~~~~

StrictDoc shall support exporting documents to Excel format.

PlantUML Export
~~~~~~~~~~~~~~~

StrictDoc shall support exporting documents to ReqIF format.

ReqIF Import/Export
~~~~~~~~~~~~~~~~~~~

StrictDoc shall support ReqIF format.

Tex Export
~~~~~~~~~~

StrictDoc shall support exporting documents to Tex format.

Markdown support for text and code blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support rendering text/code blocks into RST syntax.

Platform support
----------------

Linux support
~~~~~~~~~~~~~

StrictDoc shall work on Linux systems.

Windows support
~~~~~~~~~~~~~~~

StrictDoc shall work on Windows systems.

Traceability and coverage
-------------------------

Linking with implementation artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support linking requirements to files.

Requirement checksumming
~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support calculation of checksums for requirements.

Documentation coverage
~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall generate requirements coverage information.

Validations and testing
-----------------------

Validation: Section Levels
~~~~~~~~~~~~~~~~~~~~~~~~~~

Section levels must be properly nested.

Validation: Valid HTML markup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc's HTML export tests shall validate the generated HTML markup.

**Comment:** First candidate: Table of contents and its nested ``<ul>/<li>`` items.

Custom fields
-------------

StrictDoc shall support customization of the default grammar with custom fields.

**Comment:** Examples:

- RAIT compliance fields (Review of design, analysis, inspection, testing)
- Automotive Safety Integrity Level level (ASIL).

Filtering by tags
-----------------

StrictDoc shall support filtering filtering by tags.

Options
-------

Option: Title: Automatic numeration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support config option `numeric_titles`.

Option: Title: Display requirement titles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support config option `display_requirement_titles`.

Option: Title: Display requirement UID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support config option `display_requirement_uids`.

Advanced
--------

Facts table. Invariants calculation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support creation of fact tables calculating invariants that enforce numerical constraints.

Graphical User Interface (GUI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall provide a Graphical User Interface (GUI).

