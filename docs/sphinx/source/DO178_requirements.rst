DO-178C requirements tool requirements
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

This document outlines a set of high-level requirements for StrictDoc, a text-based requirements management system. While StrictDoc already meets many of these requirements, further discussion is needed to clarify any remaining questions. For the outstanding requirements, we can establish a practical implementation plan within the upcoming 2023-2024 StrictDoc roadmap.

These requirements are recommended by engineers who adhere to the DO-178B and DO-178C standards of the aviation industry. For a visual summary of the DO-178 standard, please refer to this link: https://upload.wikimedia.org/wikipedia/commons/4/4f/DO-178B_Process_Visual_Summary_Rev_A.pdf.

.. _SECTION-DR-Already-implemented-features:

Already implemented features
============================

.. _DO178-1:

Document concept
----------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-1
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall store requirements in document files.

**Rationale:**

A concept of a "document file with requirements" helps to structure requirements like they are normally structured in the documents.

An alternative implementation of "1 file per 1 requirement" can be very restrictive in some use cases. For example, one needs to open lots of files to edit, if one file can only have one requirement.

**Children:**

- ``[SDOC-SRS-105]`` :ref:`SDOC-SRS-105`

.. _DO178-2:

Strict specified grammar
------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-2
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall feature a specified document grammar.

**Rationale:**

The grammar helps to standardize a document structure.

**Comment:**

N: StrictDoc is nice.

**Children:**

- ``[SDOC-SRS-19]`` :ref:`SDOC-SRS-19`

.. _DO178-14:

Requirement UID autocompletion
------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-14
    * - **STATUS:**
      - Active

StrictDoc shall provide autocompletion feature for requirement UID identifiers.

Note: Most immediate use case: adding/editing parent requirements.

**Comment:**

N: When adding parent links, StrictDoc GUI shall present a selection list of UID, with a completion filter, then compute the sha1 of the selected parent req.

**Comment:**

N: Upon req editing, a completion list of already existing reqs (+ "derived" item) would be definitely nice in Webgui !
and would be the ultimate argument to NOT text edit.

**Children:**

- ``[SDOC-SRS-120]`` :ref:`SDOC-SRS-120`

.. _DO178-3:

Multiple git repositories document assembly
-------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-3
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall support generating requirement trees from multiple Git repositories.

**Comment:**

N: StrictDoc is compliant.

**Children:**

- ``[SDOC-SRS-115]`` :ref:`SDOC-SRS-115`

.. _DO178-4:

Document fragments in separate files
------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-4
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall support assembly of documents from multiple files.

**Comment:**

S: StrictDoc supports document fragments. A document fragment corresponds to a section that can be kept in a separate file. A document stored in another file can import the fragment and have it included in the main document.

**Children:**

- ``[SDOC-SRS-109]`` :ref:`SDOC-SRS-109`

.. _DO178-5:

PDF and HTML publishing
-----------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-5
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall support publication of documents to HTML and PDF formats.

**Comment:**

N: Sphinx is nice for release.

**Children:**

- ``[SDOC-SRS-51]`` :ref:`SDOC-SRS-51`
- ``[SDOC-SRS-70]`` :ref:`SDOC-SRS-70`
- ``[SDOC-SRS-71]`` :ref:`SDOC-SRS-71`

.. _DO178-6:

Graphical user interface (GUI)
------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-6
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall support a graphical user interface.

**Comment:**

N: A Web GUI in StrictDoc is nice in daily work, especially for non developer people.

**Comment:**

N: GUI for editing is NTH but it shall scale well to thousands of requirements. And it could also contribute to traceability feature.

**Children:**

- ``[SDOC-SRS-50]`` :ref:`SDOC-SRS-50`

.. _DO178-8:

Configuration: 'Host' parameter
-------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-8
    * - **STATUS:**
      - Active

StrictDoc shall provide an option to configure a host where a server is deployed.

**Comment:**

N: Binding to any local address (localhost) with an option would enable to edit from a smartphone bound to a Raspberry server, for instance.

**Children:**

- ``[SDOC-SRS-119]`` :ref:`SDOC-SRS-119`

.. _DO178-7:

No use of proprietary technology
--------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-7
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall not use any proprietary tools.

**Rationale:**

Use of proprietary tools complicates the workflows and the interoperability between companies and teams.

**Comment:**

S: StrictDoc is written using Python and supports the ReqIF format out of the box. All StrictDoc's dependencies are open-source software components.

**Children:**

- ``[SDOC-SRS-89]`` :ref:`SDOC-SRS-89`

.. _DO178-13:

Source file coverage
--------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-13
    * - **STATUS:**
      - Backlog

StrictDoc shall support generation of source code coverage information.

**Comment:**

S: Source file coverage is StrictDoc's experimental feature. With a more detailed specification, we can turn it to a more advanced and clear presentation of the needed aspects.

**Children:**

- ``[SDOC-SRS-35]`` :ref:`SDOC-SRS-35`

.. _SECTION-DR-Needs-discussion:

Needs discussion
================

.. _DO178-19:

WYSIWYG editing
---------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-19
    * - **STATUS:**
      - Active

StrictDoc's GUI shall support a WYSIWYG text editing.

**Comment:**

Simplifies editing of formatted text.

**Children:**

- ``[SDOC-SRS-121]`` :ref:`SDOC-SRS-121`

.. _DO178-15:

Diff between document trees
---------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-15
    * - **STATUS:**
      - Backlog

StrictDoc shall allow calculating Diff between two document trees.

Note: The primary use case is calculating a diff between two Git revisions.

**Comment:**

N: Highlight a req diff with its previous version (Git).

**Children:**

- ``[SDOC-SRS-111]`` :ref:`SDOC-SRS-111`

.. _DO178-10:

Traceability matrices
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-10
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Backlog

StrictDoc shall support generation of forward and backward traceability matrices.

**Comment:**

N: Trace matrix publishing (both ways : is covered by ... and covers ...) published in HTML/PDF.

**Comment:**

S: This feature, especially a very basic initial one, is very easy to implement, and it is already on the nearest roadmap, see https://github.com/strictdoc-project/strictdoc/issues/964#issuecomment-1497900436>. We only need to agree on if we are on the same page about how the produced matrices look like.

**Children:**

- ``[SDOC-SRS-112]`` :ref:`SDOC-SRS-112`

.. _DO178-11:

Impact analysis
---------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-11
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Active

StrictDoc shall support generation of Impact Analysis information.

**Comment:**

N: Impact analysis – upon modification of a requirement: report the recursive list of impacted items.

**Comment:**

S: This feature is doable and a basic variant can be derived from the existing code that generates the Deep Traceability screen. A more advanced one includes a document-to-document Diff between version control revisions, including "tell me what changed between the latest commit and my changes". Based on this information, a full impact analysis package can be generated. This is less trivial to implement and requires prioritization.

**Comment:**

N: For impact analysis we were thinking about some design which help to satisfy these feature: upon modification of a requirement which owns some parent links, a SHA1 of each parent requirement statement is computed and set in the edited requirement.
=> this could be captured by the GUI, and there also could exist a CLI command to perform this tagging.

For overall analysis, a CLI command could parse the tree and compute the SHA1 and tel which requirement are to be updated because one of there ancestor were modified.
This is almost the same feature called review status in doorstop.

**Comment:**

N: When adding parent links, the GUI could present a selection list of UID, with a completion filter, then compute the SHA1 of the selected parent req.
Then highlight uncovered requirement, and requirements impacted by parent change.

**Children:**

- ``[SDOC-SRS-117]`` :ref:`SDOC-SRS-117`

.. _DO178-12:

Uncovered requirement report
----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-12
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Backlog

StrictDoc shall support generation of uncovered requirement report.

Note: An uncovered requirement is one that has no children.

**Comment:**

S: This is easy to implement but would be nice to have it specified in terms of how exactly it should look like. The requirements coverage screen was one experimental attempt to visualize and highlight the uncovered requirements but we didn't stabilize the feature in terms of the visual clarity.

**Children:**

- ``[SDOC-SRS-66]`` :ref:`SDOC-SRS-66`
- ``[SDOC-SRS-97]`` :ref:`SDOC-SRS-97`
- ``[SDOC-SRS-112]`` :ref:`SDOC-SRS-112`

.. _DO178-9:

Project-level grammar
---------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-9
    * - **COMPLIANCE:**
      - C
    * - **STATUS:**
      - Backlog

StrictDoc shall support creation of a project-level grammar.

**Rationale:**

A single grammar defined for a project (same grammar for several documents) helps to standardize the structure of all documents in a documentation tree and reduces the effort needed to create identical grammars all the time.

**Comment:**

S: This feature is easy to implement. The easiest implementation path is to include a config parameter, such as ``project_grammar`` in the already-existing ``strictdoc.toml`` file. At startup, StrictDoc recognizes the parameter and reads the grammar from a separate file. The project grammar becomes a single source of truth for all documents in the project tree but the option to override a grammar for a given document is still preserved.

**Children:**

- ``[SDOC-SRS-122]`` :ref:`SDOC-SRS-122`

.. _DO178-16:

Interoperability with Sphinx
----------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-16
    * - **COMPLIANCE:**
      - PC
    * - **STATUS:**
      - Backlog

StrictDoc shall support interoperability with Sphinx:

1) StrictDoc shall read RST fragments with Sphinx directives without errors.
2) StrictDoc shall render Sphinx plugins natively.

**Comment:**

N: Support various fragments (images, csv, doxygen, uml, math expr...) => Sphinx extensions nice.

**Comment:**

S: It should be possible to achieve the goal 1 by implementing a complete or limited behavior of each Sphinx plugin feature like I already suggested `here <https://github.com/strictdoc-project/strictdoc/issues/1093#issuecomment-1505108384>`_. For each needed plugin, we can implement a simulative directive using Docutils, and I expected that for many plugins we can achieve a good compatible behavior. The goal 2 needs a special R&D activity where it has to be decided what would be the interface between StrictDoc and Sphinx.

**Comment:**

N: ``image.*`` is MTH to enable both HTML and pdf.
breathe is required for the Software Design Description document which defines software architecture, low level requirements and code component interfaces. But it could be Split in 2 separate documents. LLR in .sdoc and code component interface with sphinx/breathe. So I consider it as NTH.

**Children:**

- ``[SDOC-SRS-70]`` :ref:`SDOC-SRS-70`
- ``[SDOC-SRS-71]`` :ref:`SDOC-SRS-71`

.. _DO178-17:

Multi-user editing of documents
-------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-17
    * - **COMPLIANCE:**
      - NC
    * - **STATUS:**
      - Backlog

StrictDoc shall allow multi-user editing of documents.

**Comment:**

N: .sdoc file lock?

**Children:**

- ``[SDOC-SRS-123]`` :ref:`SDOC-SRS-123`

.. _DO178-18:

Support for Derived requirements
--------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - DO178-18
    * - **STATUS:**
      - Backlog

StrictDoc shall provide first-class support for Derived requirements.

**Comment:**

N: I would mention another important feature related to DO178. The requirement which have not parent are "derived" and shall be assessed by safety.

Two issues when a parent ref is set to ``REQUIRED: True`` in grammar:

1. I cannot specify derived requirements.
2. Top reqs do not have parents by définition.

I worked around this, using a top .sdoc with grammar parent ref optional. Including a specific requirement titled "derived" on which all other .sdoc derived reqd will point as parent ref. But this might be improved.

**Children:**

- ``[SDOC-BACKLOG-9]`` :ref:`SDOC-BACKLOG-9`
