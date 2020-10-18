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

Roadmap
=======

First public release
--------------------

StrictDoc via CLI interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support it use as a Python command-line application.

**Comment:** Such a use allows a more fine-grained access to the StrictDoc's modules, such
as Grammar, Import, Export classes, etc.

Document tree: Incremental generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When exporting documentation tree, StrictDoc shall regenerate only changed documents and files.

Generated file names
~~~~~~~~~~~~~~~~~~~~

Document name must be transformed into a valid file name.

**Comment:** Alternative: Simply use the original document file names.

Validation: Uniqueness of UID identifiers in a document tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall ensure that each UID used in a document tree is unique.

StrictDoc as library
--------------------

StrictDoc shall support it use as a Python library.

**Comment:** Such a use allows a more fine-grained access to the StrictDoc's modules, such
as Grammar, Import, Export classes, etc.

Excel Export
------------

StrictDoc shall support exporting documents to Excel format.

PlantUML Export
---------------

StrictDoc shall support exporting documents to ReqIF format.

ReqIF Import/Export
-------------------

StrictDoc shall support ReqIF format.

Markdown support for text and code blocks
-----------------------------------------

StrictDoc shall support rendering text/code blocks into RST syntax.

Platform support
----------------

StrictDoc shall work on macOS, Linux, and Windows systems.

Custom fields
-------------

StrictDoc shall support customization of the default grammar with custom fields.

**Comment:** Examples:

- RAIT compliance fields (Review of design, analysis, inspection, testing)
- Automotive Safety Integrity Level level (ASIL).

Filtering by tags
-----------------

StrictDoc shall support filtering filtering by tags.

Linking with implementation artifacts
-------------------------------------

StrictDoc shall support linking requirements to files.

Documentation coverage
----------------------

StrictDoc shall generate requirements coverage information.

Graphical User Interface (GUI)
------------------------------

StrictDoc shall provide a Graphical User Interface (GUI).

Validation: Section Levels
--------------------------

Section levels must be properly nested.

Validation: Valid HTML markup
-----------------------------

StrictDoc's HTML export tests shall validate the generated HTML markup.

**Comment:** First candidate: Table of contents and its nested ``<ul>/<li>`` items.

Option: Title: Automatic numeration
-----------------------------------

StrictDoc shall support config option `numeric_titles`.

Option: Title: Display requirement titles
-----------------------------------------

StrictDoc shall support config option `display_requirement_titles`.

Option: Title: Display requirement UID
--------------------------------------

StrictDoc shall support config option `display_requirement_uids`.

Advanced: Facts table. Invariants calculation.
----------------------------------------------

StrictDoc shall support calculating invariants that enforce numerical constraints.

