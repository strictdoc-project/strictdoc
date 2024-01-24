StrictDoc Backlog
$$$$$$$$$$$$$$$$$

This document outlines the future work items for StrictDoc.

The following items are listed in descending order of priority, with the topmost items either currently in progress or scheduled to be implemented next.

While this backlog overlaps with StrictDoc's `GitHub issues tracker <https://github.com/strictdoc-project/strictdoc/issues>`_ by more than 50%, it includes more strategic items compared to the GitHub issues, which are primarily focused on actual implementation work.

.. _SECTION-SB-Open-source-requirements-tool-challenges:

Open-source requirements tool challenges
========================================

- Very limited development time
- Not enough time to develop certain capabilities
- Not possible to scale to multi-user environment quickly.

.. _SDOC-SRS-13:

Real-time editing out of scope
------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-13
    * - **STATUS:**
      - Backlog

StrictDoc shall not implement the real-time editing capability to its web interface.

**Rationale:**

The real-time editing feature is hard to achieve with a small part-time involvement from the development team. This requirement can only be reconsidered, if StrictDoc would experience a significant increase in the development power.

.. _SECTION-SB-Backlog:

Backlog
=======

.. _SDOC-BACKLOG-6:

Auto-commit to Git repository
-----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-6
    * - **STATUS:**
      - Backlog

.. _SDOC-SRS-86:

Auto-generate section UIDs
--------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-86
    * - **STATUS:**
      - Backlog

TBD

.. _SECTION-SRS-Screen-Project-home:

Screen: Project home
--------------------

.. _SDOC-SRS-52:

View project home page
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-52
    * - **STATUS:**
      - Backlog

Screen: Traceability navigator
------------------------------

.. _SDOC-SRS-113:

Traceability navigator
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-113
    * - **STATUS:**
      - Backlog

StrictDoc shall provide a traceability navigator screen.

**Rationale:**

Provide an interactive 1000-ft view of a requirements project.

**Parents:**

- ``[SDOC-SSS-56]`` :ref:`SDOC-SSS-56`

.. _SECTION-SB-Formal-modeling:

Formal modeling
---------------

.. _SDOC-RMC-27:

Integration with other systems engineering processes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-RMC-27
    * - **STATUS:**
      - Backlog

The Requirements Tool shall provide capabilities for integration with other systems engineering tools.

.. _SDOC-RMC-29:

Integration with Capella
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-RMC-29
    * - **STATUS:**
      - Backlog

The Requirements Tool shall provide integration with Capella MBSE tool.

**Rationale:**

Eclipse Capella is a capable open-source tool for Model-Based Systems Engineering, https://www.eclipse.org/capella/. It should be beneficial for the requirements tool to interface with the Capella engineering community.

**Comment:**

At the very least, the integration can happen through the ReqIF interface that Capella is known to support.

.. _SDOC-RMC-55:

Support STPA method
~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-RMC-55
    * - **STATUS:**
      - Backlog

The Requirements Tool shall provide support for the STPA method.

.. _SDOC-RMC-28:

Formalized statements
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-RMC-28
    * - **STATUS:**
      - Backlog

The Requirements Tool shall provide capabilities for hardening requirements content with formal semantics.

**Comment:**

The directions to explore:

- NASA FRET
- bmw-software-engineering/trlc

.. _SDOC-RMC-30:

AI Assistant
~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-RMC-30
    * - **STATUS:**
      - Backlog

The Requirements Tool shall provide integration with AI tools (e.g., ChatGPT).

.. _SECTION-SRS-LaTeX-export:

LaTeX export
------------

.. _SDOC-SRS-76:

Export to Tex
~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-76
    * - **STATUS:**
      - Backlog

.. _SDOC-BACKLOG-1:

Focused mode: Edit a single section / requirement
-------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-1
    * - **STATUS:**
      - Backlog

.. _SDOC-BACKLOG-2:

Interoperability with Doxygen
-----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-2
    * - **STATUS:**
      - Backlog

.. _SDOC-BACKLOG-3:

Fuzzy search (the whole documentation)
--------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-3
    * - **STATUS:**
      - Backlog

.. _SDOC-BACKLOG-9:

Derived requirements
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-9
    * - **STATUS:**
      - Backlog

StrictDoc shall provide first-class support for Derived requirements.

**Parents:**

- ``[DO178-18]`` :ref:`DO178-18`

.. _SDOC-BACKLOG-4:

Support Markdown markup
-----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-4
    * - **STATUS:**
      - Backlog

.. _SDOC-BACKLOG-7:

Language Server Protocol (LSP)
------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-7
    * - **STATUS:**
      - Backlog

.. _SDOC-BACKLOG-8:

UML
---

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-BACKLOG-8
    * - **STATUS:**
      - Backlog

.. _SDOC-SRS-129:

Export/import to CSV
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-129
    * - **STATUS:**
      - Backlog

StrictDoc shall allow exporting/import SDoc content to/from CSV.

**Parents:**

- ``[SDOC-SSS-59]`` :ref:`SDOC-SSS-59`

.. _SDOC-SRS-114:

Web API
-------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-114
    * - **STATUS:**
      - Backlog

StrictDoc shall provide a web API.

**Rationale:**

A web API allows integration with tools and workflows external to StrictDoc itself.

**Parents:**

- ``[SDOC-SSS-68]`` :ref:`SDOC-SSS-68`
- ``[SDOC-SSS-79]`` :ref:`SDOC-SSS-79`
- ``[SDOC-SSS-85]`` :ref:`SDOC-SSS-85`

Multi-user workflow
-------------------

.. _SDOC-SRS-123:

Multi-user editing of documents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-123
    * - **STATUS:**
      - Backlog

StrictDoc shall support concurrent use and editing of a single StrictDoc web server instance by multiple users.

**Parents:**

- ``[DO178-17]`` :ref:`DO178-17`
- ``[SDOC-SSS-81]`` :ref:`SDOC-SSS-81`

.. _SDOC-SRS-130:

User accounts
~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-130
    * - **STATUS:**
      - Backlog

StrictDoc shall support user accounts.

**Parents:**

- ``[SDOC-SSS-65]`` :ref:`SDOC-SSS-65`

.. _SDOC-SRS-131:

Update notifications
~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-131
    * - **STATUS:**
      - Backlog

StrictDoc shall support notifying a user (users) about updated requirements.

**Parents:**

- ``[SDOC-SSS-66]`` :ref:`SDOC-SSS-66`
- ``[SDOC-SSS-74]`` :ref:`SDOC-SSS-74`

.. _SDOC-SRS-116:

Requirement validation according to EARS syntax
-----------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-116
    * - **STATUS:**
      - Backlog

The SDoc model shall provide validation of requirements according to the EARS syntax.

**Parents:**

- ``[SDOC-SSS-57]`` :ref:`SDOC-SSS-57`

.. _SDOC-SRS-122:

Project-level grammar
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-122
    * - **STATUS:**
      - Backlog

StrictDoc shall support creation of a project-level grammar.

**Rationale:**

A single grammar defined for a project (same grammar for several documents) helps to standardize the structure of all documents in a documentation tree and reduces the effort needed to create identical grammars all the time.

**Comment:**

The implementation is easy model-wise but the user interface details need to be elaborated.

**Parents:**

- ``[DO178-9]`` :ref:`DO178-9`

.. _SDOC-SRS-121:

WYSIWYG editing
---------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-121
    * - **STATUS:**
      - Backlog

StrictDoc shall provide WYSIWYG kind of editing for all multiline text input fields.

**Rationale:**

WYSIWYG improves the user experience, especially for non-programmer users.

**Parents:**

- ``[DO178-19]`` :ref:`DO178-19`
- ``[SDOC-SSS-80]`` :ref:`SDOC-SSS-80`

.. _SDOC-SRS-61:

Tables HTML editor
------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-61
    * - **STATUS:**
      - Backlog

StrictDoc shall provide a solution for editing tables in its web interface.

.. _SDOC-SRS-94:

Move requirement / section nodes between documents
--------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-94
    * - **STATUS:**
      - Backlog

StrictDoc's Document screen shall provide a capability to move the nodes between documents.

**Rationale:**

Moving the nodes within a document is a convenience feature that speeds up the requirements editing process significantly.

**Parents:**

- ``[SDOC-SSS-70]`` :ref:`SDOC-SSS-70`

.. _SDOC-SRS-120:

Auto-completion for requirements UIDs
-------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-120
    * - **STATUS:**
      - Backlog

StrictDoc's Document screen shall provide controls for automatic completion of requirements UIDs.

**Comment:**

The automatic completion can be especially useful when a user has to fill in a parent relation UID.

**Parents:**

- ``[SDOC-SSS-6]`` :ref:`SDOC-SSS-6`
- ``[DO178-14]`` :ref:`DO178-14`
- ``[SDOC-SSS-80]`` :ref:`SDOC-SSS-80`

.. _SDOC-SRS-58:

Attach image to requirement
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-58
    * - **STATUS:**
      - Backlog

.. _SDOC-SRS-60:

Provide contextual help about RST markup
----------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-60
    * - **STATUS:**
      - Backlog

.. _SDOC-SRS-63:

TBL: Hide/show columns
----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-63
    * - **STATUS:**
      - Backlog

StrictDoc's Table screen shall allow hiding/showing columns.

.. _SDOC-SRS-64:

TBL: Select/deselect tags
-------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-64
    * - **STATUS:**
      - Backlog

StrictDoc's Table screen shall allow filtering content based on the selection/deselection of available tags.

Screen: Impact analysis
-----------------------

.. _SDOC-SRS-117:

Impact analysis
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-117
    * - **STATUS:**
      - Backlog

StrictDoc shall provide the Impact Analysis screen.

NOTE: The Impact Analysis screen helps to get information about the impact that a given change to a requirement has on the other requirements in the project tree.

**Rationale:**

The impact analysis is one of the core functions of a requirements management tool. Analyzing the impact that a requirement has on other requirements and an overall project's technical definition helps to perform effective change management.

**Parents:**

- ``[SDOC-SSS-74]`` :ref:`SDOC-SSS-74`
- ``[DO178-11]`` :ref:`DO178-11`

.. _SDOC-SRS-75:

ReqXLS
------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-SRS-75
    * - **STATUS:**
      - Backlog

.. _SECTION-SB-Backlog-Web-based-user-interface:

Backlog: Web-based user interface
=================================

- Uploading images via Web interface.

- Deleting sections recursively. Correct clean-up of all traceability information.

- Editing remaining document options: Inline/Table, Requirements in TOC, etc.

- **Integration with Git repository.** Make the server commit changes to .sdoc files automatically. To a user, provide visibility to what happens under the hood.

- ``LINK`` between sections and documents.

- Option to keep all multi-line text fields to 80 symbols width.

- Moving nodes between documents.

- TBL view: Column filters to show/hide columns.

- TBL view: Completely empty columns are hidden by default.

- Contextual help about the RST markup.
- How to edit tables conveniently?

- What to do with web content going out of sync with the server/file system state?

- Issue when adding a child section from a nested section. The child section appears right after the nested section, not after its farthest descendant child.

- ReqIF: Export complete documentation tree or a single document.
- ReqIF: Import complete documentation tree or a single document.

.. _SECTION-SB-Backlog-Nice-to-have:

Backlog: Nice to have
=====================

- Configuration file options:

  - CLI command to dump default config file
  - Project prefix?
  - Config options for presenting requirements.
    - Include/exclude requirements in TOC

- **StrictDoc as a Python library**. Such a use allows a more fine-grained access to the StrictDoc's modules, such as Grammar, Import, Export classes, etc.

- **Data exchange with Capella tool.** The current idea would be to implement this using ReqIF export/import features.

- **Language Server Protocol.** The LSP can enable editing of SDoc files in IDEs like Eclipse, Visual Studio, PyCharm. A smart LSP can enable features like syntax highlighting, autocompletion and easy navigation through requirements. The promising base for the implementation: https://github.com/openlawlibrary/pygls.

- StrictDoc shall support rendering text/code blocks into Markdown syntax.

- **Fuzzy requirements search.** This feature can be implemented in the CLI as well as in the future GUI. A fuzzy requirements search can help to find existing requirements and also identify relevant requirements when creating new requirements.

- Support creation of FMEA/FMECA safety analysis documents.

- Calculation of checksums for requirements. This feature is relatively easy to implement, but the implementation is postponed until the linking between requirements and files is implemented.

- Filtering of requirements by tags.

- Import/export: Excel, CSV, PlantUML, Confluence, Tex, Doorstop.

- **Partial evaluation of Jinja templates.** Many of the template variables could be made to be evaluated once, for example, config object's variables.

- UI version for mobile devices (at least some basic tweaks).

.. _SECTION-SB-Backlog-Technical-debt:

Backlog: Technical debt
=======================

- When a document is added, the whole documentation is rebuilt from the file system from scratch. A more fine-grained re-indexing of documentation tree can be implemented. The current idea is to introduce a layer of pickled cached data: preserve the whole in-memory traceability graph in a cache, and then use the cached data for making decisions about what should be regenerated.
- The "no framework" approach with FastAPI and Turbo/Stimulus allows writing almost zero Javascript, however some proto-framework conventions are still needed. Currently, all code is written in the ``main_controller`` which combines all responsibilities, such as parsing HTTP request fields, accessing traceability graph, validations, rendering back the updated AJAX templates. A lack of abstraction is better than a poor abstraction, but some solution has to be found.
- Request form object vs Response form object. The workflow of form validations is not optimal.
- For Web development, the responsibilities of the ``TraceabilityIndex`` class compared to the ``ExportAction``, ``MarkupRenderer``, ``LinkRenderer`` classes are unstable. A more ecological composition of classes has to be found. ``Traceability`` index is rightfully a "god object" because it contains all information about the in-memory documentation graph.

.. _SECTION-SB-Open-questions:

Open questions
==============

.. _SECTION-SB-One-or-many-input-sdoc-trees:

One or many input sdoc trees
----------------------------

StrictDoc supports this for HTML already but not for RST.

When passed
``strictdoc export ... /path/to/doctree1, /path/to/doctree2, /path/to/doctree3``,
the following is generated:

.. code-block:: text

    output folder:
    - doctree1/
      - contents
    - doctree2/
      - contents
    - doctree3/
      - contents

and all three doctrees' requirements are merged into a single documentation
space with cross-linking possible.

The question is if it is worth supporting this case further or StrictDoc should
only work with one input folder with a single doc tree.
