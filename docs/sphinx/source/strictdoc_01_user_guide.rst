User Guide
$$$$$$$$$$

Introduction
============

StrictDoc is software for writing technical requirements and specifications.

Summary of StrictDoc features:

- The documentation files are stored as human-readable text files.
- A simple domain-specific language DSL is used for writing the documents. The
  text format for encoding this language is called SDoc (strict-doc).
- StrictDoc reads ``*.sdoc`` files and builds an in-memory representation of the
  document tree.
- From this in-memory representation, StrictDoc can generate the documentation
  into a number of formats including HTML, RST, ReqIF, PDF, Excel.
- The focus of the tool is modeling requirements and specifications documents.
  Such documents consist of multiple statements like "system X shall do Y"
  called requirements.
- The requirements can be linked together to form the relationships, such as
  "parent-child", and from these connections, many useful features, such as
  `Requirements Traceability <https://en.wikipedia.org/wiki/Requirements_traceability>`_
  and Documentation Coverage, can be derived.
- Requirements to source files traceability (experimental). See
  `Traceability between requirements and source code`_.
- Custom grammar and custom fields support. The StrictDoc's grammar can be
  extended to support arbitrary special fields, such as ``PRIORITY``, ``OWNER``,
  or even more specialized fields, such as
  ``Automotive Safety Integrity Level (ASIL)`` or ``Verification method``.
  See `Custom grammars`_.
- Good performance of the `textX <https://github.com/textX/textX>`_
  parser and parallelized incremental generation of documents: generation of
  document trees with up to 2000-3000 requirements into HTML pages stays within
  a few seconds. From the second run, only changed documents are regenerated.
  Further performance tuning should be possible.

See the Backlog to get an idea of the overall project direction.

Contact the developers
----------------------

Join us in Discord. Here is the invitation link: https://discord.gg/4BAAME9MmG

The author can be also contacted via `email <s.pankevich@gmail.com>`_.

Examples
========

"Hello World" example of the text language:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: SDOC-HIGH-REQS-MANAGEMENT
    TITLE: Requirements management
    STATEMENT: StrictDoc shall enable requirements management.

For a more comprehensive example check the source file of this documentation
which is written using StrictDoc:
`strictdoc_01_user_guide.sdoc <https://github.com/strictdoc-project/strictdoc/blob/main/docs/strictdoc_01_user_guide.sdoc>`_.

- `StrictDoc HTML export <https://strictdoc.readthedocs.io/en/latest/strictdoc-html>`_
- `StrictDoc HTML export using Sphinx <https://strictdoc.readthedocs.io/en/latest>`_
- `StrictDoc PDF export using Sphinx <https://strictdoc.readthedocs.io/_/downloads/en/latest/pdf/>`_

Additionally, the project's repository contains a folder
``tests/integration/examples``. In this folder, there is a collection of basic
examples.

Getting started
===============

Requirements
------------

- Python 3.6+
- macOS, Linux or Windows

Installing StrictDoc as a Pip package (recommended way)
-------------------------------------------------------

.. code-block:: text

    pip install strictdoc

Installing StrictDoc into a Docker container
--------------------------------------------

StrictDoc can be invoked inside of a Docker container. To make data available
to the Docker container (here: ``strictdoc:latest``) as well as to the host
system, one needs to mount a volume via ``-v`` option.

In the host operating system terminal:

.. code-block:: text

    docker build . -t strictdoc:latest
    docker run --name strictdoc --rm -v "$(pwd)/docs:/data" -i -t strictdoc:latest

In the container terminal:

.. code-block:: text

    bash-5.1# strictdoc export .
    bash-5.1# exit

The documentation resides in ``./docs/output/html``.

Installing StrictDoc as a Snap package (not maintained)
-------------------------------------------------------

This way of installing StrictDoc is not maintained anymore. If you want to
use it, refer to the instructions located in ``developer/snap/README.md``.

Hello world
-----------

.. code-block:: text

    git clone --depth 1 https://github.com/strictdoc-project/strictdoc && cd strictdoc
    strictdoc export docs/

SDoc syntax
===========

StrictDoc defines a special syntax for writing specifications documents. This
syntax is called SDoc and it's grammar is encoded with the
`textX <https://github.com/textX/textX>`_
tool.

The grammar is defined using textX language for defining grammars and is
located in a single file:
`grammar.py <https://github.com/strictdoc-project/strictdoc/blob/main/strictdoc/backend/sdoc/grammar/grammar.py>`_.

This is how a minimal possible SDoc document looks like:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

This documentation is written using StrictDoc. Here is the source file:
`strictdoc_01_user_guide.sdoc <https://github.com/strictdoc-project/strictdoc/blob/main/docs/strictdoc_01_user_guide.sdoc>`_.

Document structure
------------------

An SDoc document consists of a ``[DOCUMENT]`` declaration followed by one or many
``[REQUIREMENT]`` or ``[COMPOSITE_REQUIREMENT]`` statements which can be grouped
into ``[SECTION]`` blocks.

The following grammatical constructs are currently supported:

- ``DOCUMENT``

  - ``FREETEXT``

- ``REQUIREMENT`` and ``COMPOSITE_REQUIREMENT``

- ``SECTION``

  - ``FREETEXT``

Each construct is described in more detail below.

Strict rule #1: One empty line between all nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc's grammar requires each node, such as ``[REQUIREMENT]``, ``[SECTION]``,
etc., to be separated with exactly one empty line from the nodes surrounding it.
This rule is valid for all nodes. Absence of an empty line or presence of more
than one empty line between two nodes will result in an SDoc parsing error.

Strict rule #2: No content is allowed outside of SDoc grammar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc's grammar does not allow any content to be written outside of the SDoc
grammatical constructs. It is assumed that the critical content shall always be
written in form of requirements:
``[REQUIREMENT]`` and ``[COMPOSITE_REQUIREMENT]``. Non-critical content shall
be specified using ``[FREETEXT]`` nodes. By design, the ``[FREETEXT]`` nodes can
be only attached to the ``[DOCUMENT]`` and ``[SECTION]`` nodes.

Grammar elements
----------------

Document
~~~~~~~~

The ``[DOCUMENT]`` element must always be present in an SDoc document. It is a
root of an SDoc document graph.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc
    (newline)

The following ``DOCUMENT`` fields are allowed:

.. list-table:: SDoc grammar ``DOCUMENT`` fields
   :widths: 20 80
   :header-rows: 1

   * - **Field**
     - **Description**

   * - ``TITLE``
     - Title of the document (mandatory)

   * - ``UID``
     - Unique identifier of the document

   * - ``VERSION``
     - Current version of the document

   * - ``CLASSIFICATION``
     - Security classification of the document, e.g. Public, Internal,
       Restricted, Confidential

   * - ``OPTIONS``
     -  Document configuration options

The ``DOCUMENT`` declaration must always have a ``TITLE`` field. The other
fields are optional. The ``OPTIONS`` field can be used for specifying
the document configuration options. Note: The sequence of the fields is defined
by the document's Grammar, i.e. should not be changed.

Finally an optional ``[FREETEXT]`` block can be included.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc
    OPTIONS:
      REQUIREMENT_STYLE: Table

    [FREETEXT]
    StrictDoc is software for writing technical requirements and specifications.
    [/FREETEXT]


Document configuration options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``OPTIONS`` field may have the following attribute fields:

.. list-table:: SDoc grammar ``DOCUMENT``-``OPTIONS`` fields
   :widths: 20 80
   :header-rows: 1

   * - **Field**
     - **Attribute values**

   * - ``MARKUP``
     - ``RST``, ``HTML``, ``Text``

   * - ``AUTO_LEVELS``
     - ``On``, ``Off``

   * - ``REQUIREMENT_STYLE``
     - ``Inline``, ``Table``

   * - ``REQUIREMENT_IN_TOC``
     - ``True``, ``False``


MARKUP
""""""

The ``MARKUP`` option controls which markup renderer will be used.
The available options are: ``RST``, ``HTML`` and ``Text``. Default is
``RST``.

AUTO_LEVELS
"""""""""""

The ``AUTO_LEVELS`` option controls StrictDoc's system of automatic numbering
of the section levels.
The available options are: ``On`` /  ``Off``. Default is ``On``.

In case of ``On``, the ``[SECTION].LEVEL`` fields must be absent or may only
contain ``None`` to exclude that section from StrictDoc's automatic section
numbering. See also `Section without a level`_.

In case of ``Off``, all ``[SECTION].LEVEL`` fields must be populated.

REQUIREMENT_STYLE
"""""""""""""""""

The ``REQUIREMENT_STYLE`` option controls whether requirement's elements are
displayed inline or as table blocks. The available options are: ``Inline`` /
``Table``. Default is ``Inline``.

.. code-block:: text

    [DOCUMENT]
    TITLE: Hello world
    OPTIONS:
      REQUIREMENT_STYLE: Table

REQUIREMENT_IN_TOC
""""""""""""""""""

The ``REQUIREMENT_IN_TOC`` option controls whether requirement's title appear
in the table of contents (TOC). The available options are: ``True`` / ``False``.
Default is ``True``.

.. code-block:: text

    [DOCUMENT]
    TITLE: Hello world
    OPTIONS:
      REQUIREMENT_IN_TOC: True

Requirement
~~~~~~~~~~~

Minimal "Hello World" program with 3 empty requirements:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]

    [REQUIREMENT]

    [REQUIREMENT]


The following ``REQUIREMENT`` fields are supported:

.. list-table:: SDoc grammar ``REQUIREMENT`` fields
   :widths: 20 80
   :header-rows: 1

   * - **Field**
     - **Description**

   * - ``UID``
     - Unique identifier of the requirement

   * - ``LEVEL``
     - Define section/requirement Level numbering

   * - ``STATUS``
     - Status of the requirement, e.g. ``Draft``, ``Active``, ``Deleted``

   * - ``TAGS``
     - Tags of the requirement (comma separated AlphaNum words)

   * - ``REFS``
     - List of Parent and File references

   * - ``TITLE``
     - Title of the requirement

   * - ``STATEMENT``
     - The statement of the requirement. The field can be single-line or multiline.

   * - ``RATIONALE``
     - The rationale of the requirement. The field can be single-line or multiline.

   * - ``COMMENT``
     -  Comments to the rationale. The field can be single-line or multiline.
        Note: Multiple comment fields are possible.

Currently, all ``[REQUIREMENT]``'s fields are optional but most of the time at
least the ``STATEMENT`` field as well as the ``TITLE`` field should be
present.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    TITLE: Requirements management
    STATEMENT: StrictDoc shall enable requirements management.


UID
^^^

Unique identifier of the requirement.

**Observation:** Some documents do not use unique identifiers which makes it
impossible to trace their requirements to each other. Within StrictDoc's
framework, it is assumed that a good requirements document has all of its
requirements uniquely identifiable, however, the ``UID`` field is optional to
accommodate for documents without connections between requirements.

StrictDoc does not impose any limitations on the format of a UID. Examples of
typical conventions for naming UIDs:

- ``REQ-001``, ``SCA-001`` (scalability), ``PERF-001`` (performance), etc.
- ``cES1008``, ``cTBL6000.1`` (example from NASA cFS requirements)
- Requirements without a number, e.g. ``SDOC-HIGH-DATA-MODEL`` (StrictDoc)
- ``SAVOIR.OBC.PM.80`` (SAVOIR guidelines)

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: SDOC-HIGH-DATA-MODEL
    STATEMENT: STATEMENT: StrictDoc shall be based on a well-defined data model.

Level
^^^^^

Also a ``[REQUIREMENT]`` can have no section level attached to it. To enable
this behavior, the field ``LEVEL`` has to be set to ``None``.

Status
^^^^^^

Defines the current status of the ``[REQUIREMENT]``, e.g. ``Draft``, ``Active``,
``Deleted``.

Tags
^^^^

Allows to add tags to a ``[REQUIREMENT]``. Tags are a comma separated list of
single words. Only Alphanumeric tags (a-z, A-Z, 0-9 and underscore) are
supported.

References (REFS)
^^^^^^^^^^^^^^^^^

The ``REFS`` field is used to connect requirements to each other:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: REQ-001
    STATEMENT: StrictDoc shall enable requirements management.

    [REQUIREMENT]
    UID: REQ-002
    REFS:
    - TYPE: Parent
      VALUE: REQ-001
    - TYPE: File
      VALUE: /full/path/file.py
    TITLE: Requirement #2's title
    STATEMENT: Requirement #2 statement

The ``TYPE: Parent``-``VALUE`` attribute contains a parent's requirement
``UID``. A requirement may reference multiple parent requirements by
adding multiple ``TYPE: Parent``-``VALUE`` items. The opposite direction i.e.
"Child" References are traced automatically by strictdoc. Defining circular
references e.g. ``Req-A`` ⇒ ``Req-B`` ⇒ ``Reg-C`` ⇒ ``Req-A`` must be avoided.

The ``TYPE: File``-``VALUE`` attribute contains a filename referencing the
implementation of (parts of) this requirement. A requirement may add multiple
file references requirements by adding multiple ``TYPE: File``-``VALUE`` items.

**Note:** The ``TYPE: Parent`` is currently the only fully supported type of
connection. Linking requirements to files is still experimental (see also
`Traceability between requirements and source code`_).

**Note:** In the near future, adding information about external references (e.g.
company policy documents, technical specifications, regulatory requirements,
etc.) is planned.

**Note:** By design, StrictDoc will only show parent or child links if both
requirements connected with a reference have ``UID`` defined.

Title
^^^^^

The title of the requirement.
Every requirement should have its ``TITLE`` field specified.

**Observation:** Many real-world documents have requirements with statements and
titles but some documents only use statements without title in which case their
``UID`` becomes their ``TITLE`` and vice versa. Example:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: REQ-001
    STATEMENT: StrictDoc shall enable requirements management.

Statement
^^^^^^^^^

The statement of the requirement. The field can be single-line or multiline.
Every requirement shall have its ``STATEMENT`` field specified.

Rationale
^^^^^^^^^

A requirement should have a ``RATIONALE`` field that explains/justifies why
the requirement exists. Like comments, the rationale field can be single-line
or multiline.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: REQ-001
    STATEMENT: StrictDoc shall enable requirements management.
    COMMENT: Clarify the meaning or give additional information here.
    RATIONALE: The presence of the REQ-001 is justified.

Comment
^^^^^^^

A requirement can have one or more comments explaining the requirement. The
comments can be single-line or multiline.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: REQ-001
    STATEMENT: StrictDoc shall enable requirements management.
    COMMENT: Clarify the meaning or give additional information here.
    COMMENT: >>>
    This is a multiline comment.

    The content is split via \n\n.

    Each line is rendered as a separate paragraph.
    <<<

Section
~~~~~~~

The ``[SECTION]`` element is used for creating document chapters and grouping
requirements into logical groups. It is equivalent to the use of ``#``, ``##``,
``###``, etc., in Markdown and ``====``, ``----``, ``~~~~`` in RST.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [SECTION]
    TITLE: High-level requirements

    [REQUIREMENT]
    UID: HIGH-001
    STATEMENT: ...

    [/SECTION]

    [SECTION]
    TITLE: Implementation requirements

    [REQUIREMENT]
    UID: IMPL-001
    STATEMENT: ...

    [/SECTION]

Nesting sections
^^^^^^^^^^^^^^^^

Sections can be nested within each other.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [SECTION]
    TITLE: Chapter

    [SECTION]
    TITLE: Subchapter

    [REQUIREMENT]
    STATEMENT: ...

    [/SECTION]

    [/SECTION]

StrictDoc creates section numbers automatically. In the example above, the
sections will have their titles numbered accordingly: ``1 Chapter`` and
``1.1 Subchapter``.

Free text
^^^^^^^^^

A section can have a block of ``[FREETEXT]`` connected to it:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [SECTION]
    TITLE: Free text

    [FREETEXT]
    A sections can have a block of ``[FREETEXT]`` connected to it:

    ...
    [/FREETEXT]

    [/SECTION]

According to the Strict Rule #2, arbitrary content cannot be written outside
of StrictDoc's grammar structure. ``[SECTION] / [FREETEXT]`` is therefore a
designated grammar element for writing free text content.

**Note:** Free text can also be called "nonnormative" or "informative" text
because it does not contribute anything to the traceability information of the
document. The nonnormative text is there to give a context to the reader and
help with the conceptual understanding of the information. If a certain
information influences or is influenced by existing requirements, it has to be
promoted to the requirement level: the information has to be broken down into
atomic ``[REQUIREMENT]`` statements and get connected to the other requirement
statements in the document.

Section without a level
^^^^^^^^^^^^^^^^^^^^^^^

A section can have no level attached to it. To enable this behavior, the field
``LEVEL`` has to be set to ``None``.

.. code-block:: text

    [DOCUMENT]
    TITLE: Hello world doc

    [SECTION]
    TITLE: Section 1

    [/SECTION]

    [SECTION]
    LEVEL: None
    TITLE: Out-of-band Section

    [/SECTION]

    [SECTION]
    TITLE: Section 2

    [/SECTION]

The section with no level will be skipped by StrictDoc's system of automatic
numbering of the section levels (1, 1.1, 1.2, 2, ...).

The behavior of the ``LEVEL: None`` option is recursive. If a parent section
has its ``LEVEL`` set to ``None``, all its subsections' and requirements' levels
are set to ``LEVEL: None`` by StrictDoc automatically.

Composite requirement
~~~~~~~~~~~~~~~~~~~~~

A ``[COMPOSITE_REQUIREMENT]`` is a requirement that combines requirement
properties of a ``[REQUIREMENT]`` element and grouping features of a ``[SECTION]``
element. This element can be useful in lower-level specifications documents
where a given section of a document has to describe a single feature and the
description requires a one or more levels of nesting. In this case, it might be
natural to use a composite requirement that is tightly connected to a few
related sub-requirements.

.. code-block:: text

    [COMPOSITE_REQUIREMENT]
    STATEMENT: Statement

    [REQUIREMENT]
    STATEMENT: Substatement #1

    [REQUIREMENT]
    STATEMENT: Substatement #2

    [REQUIREMENT]
    STATEMENT: Substatement #3

    [/COMPOSITE_REQUIREMENT]

Special feature of ``[COMPOSITE_REQUIREMENT]``: like ``[SECTION]`` element, the
``[COMPOSITE_REQUIREMENT]`` elements can be nested within each other. However,
``[COMPOSITE_REQUIREMENT]`` cannot nest sections.

**Note:** Composite requirements should not be used in every document. Most
often, a more basic combination of nested ``[SECTION]`` and ``[REQUIREMENT]``
elements should do the job.

Include files
~~~~~~~~~~~~~

StrictDoc ``.sdoc`` files can be built-up from including other fragment documents.

The ``[FRAGMENT_FROM_FILE]`` element can be used anywhere body elements can be
used ( e.g.``[SECTION]``, ``[REQUIREMENT``, ``[COMPOSITE_REQUIREMENT]`` etc.) and will
evaluate by inserting its contents from the file referenced by its ``FILE:`` property
where it was used in the parent document. The files included must start with a ``[FRAGMENT]``
directive and cannot contain ``[FREETEXT]`` elements but are otherwise identical to
``*.sdoc`` files. They can have any filename except a``.sdoc`` extension.

Here is an example pair of files similar to examples above. First the
``.sdoc`` file has a ``[FRAGMENT_FROM_FILE]`` that references the latter file.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [FREETEXT]
    ...
    [/FREETEXT]

    [FRAGMENT_FROM_FILE]
    FILE: include.ssec

    [REQUIREMENT]

Then the referenced file, ``include.ssec``:

.. code-block:: text

    [FRAGMENT]

    [REQUIREMENT]

    [SECTION]
    TITLE: Sub section
    [/SECTION]

    [COMPOSITE_REQUIREMENT]

    [REQUIREMENT]

    [/COMPOSITE_REQUIREMENT]

Which will resolve to the following document after inclusion:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [FREETEXT]
    ...
    [/FREETEXT]

    [REQUIREMENT]

    [SECTION]
    TITLE: Sub section
    [/SECTION]

    [COMPOSITE_REQUIREMENT]

    [REQUIREMENT]

    [/COMPOSITE_REQUIREMENT]

    [REQUIREMENT]


Custom grammars
---------------

**Observation:** Different industries have their own types of requirements
documents with specialized meta information.
Examples: ``ASIL`` in the automotive industry or
``HERITAGE`` field in some of the requirements documents by NASA.

StrictDoc allows declaration of custom grammars with custom fields that are
specific to a particular document.

First, such fields have to be registered on a document level using the
``[GRAMMAR]`` field. The following example demonstrates a declaration of
a grammar with four fields including a custom ``VERIFICATION`` field.

.. code-block:: text

    [DOCUMENT]
    TITLE: How to declare a custom grammar

    [GRAMMAR]
    ELEMENTS:
    - TAG: REQUIREMENT
      FIELDS:
      - TITLE: UID
        TYPE: String
        REQUIRED: True
      - TITLE: VERIFICATION
        TYPE: String
        REQUIRED: True
      - TITLE: TITLE
        TYPE: String
        REQUIRED: True
      - TITLE: STATEMENT
        TYPE: String
        REQUIRED: True
      - TITLE: COMMENT
        TYPE: String
        REQUIRED: True

This declaration configures the parser to recognize the declared fields as
defined by a user. Declaring a special field as ``REQUIRED: True`` makes this
field mandatory for each and every requirement in the document.

When the fields are registered on the document level, it becomes possible to
declare them as the ``[REQUIREMENT]`` special fields:

.. code-block:: text

    [REQUIREMENT]
    UID: ABC-123
    VERIFICATION: Test
    STATEMENT: System A shall do B.
    COMMENT: Test comment.

**Note:** The order of fields must match the order of their declaration in the
grammar.

Supported field types
~~~~~~~~~~~~~~~~~~~~~

The supported field types are:

.. list-table:: SDoc grammar field types
   :widths: 20 80
   :header-rows: 1

   * - **Field Type**
     - **Description**

   * - ``String``
     - Simple String

   * - ``SingleChoice``
     - Enum-like behavior, one choice is possible

   * - ``MultipleChoice``
     - comma-separated words with fixed options

   * - ``Tag``
     - comma-separated list of tags/key words. Only Alphanumeric tags (a-z, A-Z, 0-9 and underscore) are supported.

   * - ``Reference``
     - comma-separated list with allowed reference types: ``ParentReqReference``, ``FileReference``

Example:

.. code-block:: text

    [DOCUMENT]
    TITLE: How to declare a custom grammar

    [GRAMMAR]
    ELEMENTS:
    - TAG: REQUIREMENT
      FIELDS:
      - TITLE: UID
        TYPE: String
        REQUIRED: True
      - TITLE: ASIL
        TYPE: SingleChoice(A, B, C, D)
        REQUIRED: True
      - TITLE: VERIFICATION
        TYPE: MultipleChoice(Review, Analysis, Inspection, Test)
        REQUIRED: True
      - TITLE: UNIT
        TYPE: Tag
        REQUIRED: True
      - TITLE: TITLE
        TYPE: String
        REQUIRED: True
      - TITLE: STATEMENT
        TYPE: String
        REQUIRED: True
      - TITLE: COMMENT
        TYPE: String
        REQUIRED: True
      - TITLE: REFS
        TYPE: Reference(ParentReqReference, FileReference)
        REQUIRED: True

    [FREETEXT]
    This document is an example of a simple SDoc custom grammar.
    [/FREETEXT]

    [REQUIREMENT]
    UID: ABC-123
    ASIL: A
    VERIFICATION: Review, Test
    UNIT: OBC, RTU
    TITLE: Function B
    STATEMENT: System A shall do B.
    COMMENT: Test comment.
    REFS:
    - TYPE: Parent
      VALUE: REQ-001
    - TYPE: File
      VALUE: /full/path/file.py


Reserved fields
~~~~~~~~~~~~~~~

While it is possible to declare a grammar with completely custom fields, there
is a fixed set of reserved fields that StrictDoc uses for the presentation of
table of contents and document structure:

.. list-table:: Reserved fields in SDoc's grammar
   :widths: 20 80
   :header-rows: 1

   * - **Reserved field**
     - **Description**

   * - UID
     - Requirement's UID.

   * - REFS
     - StrictDoc relies on this field to link requirements
       together and build traceability information.

   * - TITLE
     - Requirement's title. StrictDoc relies on this field to create
       document structure and table of contents.

   * - STATEMENT
     - Requirement's statement. StrictDoc presents this field as a long text
       block.

   * - COMMENT
     - One or more comments to a requirement.

   * - RATIONALE
     - The rationale for a requirement. Visually presented in the same way as a
       comment.

Markup
======

The Restructured Text (reST) markup is the default markup supported by
StrictDoc. The reST markup can be written inside all StrictDoc's text blocks,
such as ``[FREETEXT]``, ``STATEMENT``, ``COMMENT``, ``RATIONALE``.

See the `reST syntax documentation <https://docutils.sourceforge.io/rst.html>`_
for a full reference.

The support of Tex and HTML is planned.

Images
------

This is the example of how images are included using the reST syntax:

.. code-block:: text

    [FREETEXT]
    .. image:: _assets/sandbox1.svg
       :alt: Sandbox demo
       :class: image
    [/FREETEXT]

Export formats
==============

HTML documentation tree by StrictDoc
------------------------------------

This is a default export option supported by StrictDoc.

The following command creates an HTML export:

.. code-block:: text

    strictdoc export docs/ --formats=html --output-dir output-html

**Example:** This documentation is exported by StrictDoc to HTML:
`StrictDoc HTML export <https://strictdoc.readthedocs.io/en/latest/strictdoc-html>`_.

**Note:** The options ``--formats=html`` and ``--output-dir output-html`` can be
skipped because HTML export is a default export option and the default output
folder is ``output``.

Mathjax support
~~~~~~~~~~~~~~~

The option ``--enable-mathjax`` makes StrictDoc to include the
`Mathjax <https://www.mathjax.org/>`_ Javascript library to all of the document
templates.

.. code-block:: text

    strictdoc export docs/ --enable-mathjax --output-dir output-html

Example of using Mathjax:

.. code-block:: text

    [FREETEXT]
    .. raw:: latex html
        $$
        \mathbf{\underline{k}}_{\text{a}} =
        \mathbf{\underline{i}}_{\text{a}} \times
        \mathbf{\underline{j}}_{\text{a}}
        $$

    [/FREETEXT]

Standalone HTML pages (experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following command creates a normal HTML export with all pages having their
assets embedded into HTML using Data URI / Base64:

.. code-block:: text

    strictdoc export docs/ --formats=html-standalone --output-dir output-html

The generated document are self-contained HTML pages that can be shared via
email as single files. This option might be especially useful if you work with
a single document instead of a documentation tree with multiple documents.

HTML export via Sphinx
----------------------

The following command creates an RST export:

.. code-block:: text

    strictdoc export YourDoc.sdoc --formats=rst --output-dir output

The created RST files can be copied to a project created using Sphinx, see
`Getting Started with Sphinx <https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html>`_.

.. code-block:: text

    cp -v output/YourDoc.rst docs/sphinx/source/
    cd docs/sphinx && make html

`StrictDoc's own Sphinx/HTML documentation
<https://strictdoc.readthedocs.io/en/latest/>`_
is generated this way, see the Invoke task:
`invoke sphinx <https://github.com/strictdoc-project/strictdoc/blob/5c94aab96da4ca21944774f44b2c88509be9636e/tasks.py#L48>`_.

PDF export via Sphinx/LaTeX
---------------------------


The following command creates an RST export:

.. code-block:: text

    strictdoc export YourDoc.sdoc --formats=rst --output-dir output

The created RST files can be copied to a project created using Sphinx, see
`Getting Started with Sphinx <https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html>`_.

.. code-block:: text

    cp -v output/YourDoc.rst docs/sphinx/source/
    cd docs/sphinx && make pdf

`StrictDoc's own Sphinx/PDF documentation
<https://strictdoc.readthedocs.io/_/downloads/en/latest/pdf/>`_
is generated this way, see the Invoke task:
`invoke sphinx <https://github.com/strictdoc-project/strictdoc/blob/5c94aab96da4ca21944774f44b2c88509be9636e/tasks.py#L48>`_.

Traceability between requirements and source code
=================================================

**Note:** This feature is experimental, the documentation is incomplete.

StrictDoc allows connecting requirements to source code files. Two types of
links are supported:

1\) A basic link where a requirement links to a whole file.

.. code-block:: text

    [REQUIREMENT]
    UID: REQ-001
    REFS:
    - TYPE: File
      VALUE: file.py
    TITLE: File reference
    STATEMENT: This requirement references the file.

2\) A range-based link where a requirement links to a file and
additionally in the file, there is a reverse link that connects a source range
back to the requirement:

The requirement declaration contains a reference of the type ``File``:

.. code-block:: text

    [REQUIREMENT]
    UID: REQ-001
    REFS:
    - TYPE: File
      VALUE: file.py
    TITLE: Whole file reference
    STATEMENT: This requirement references the file.py file.
    COMMENT: >>>
    If the file.py contains a source range that is connected back to this
    requirement (REQ-001), the link becomes a link to the source range.
    <<<

The source file:

.. code-block:: py

    # [REQ-002]
    def hello_world():
        print("hello world")
    # [/REQ-002]

To activate the traceability to source files, use
``--experimental-enable-file-traceability`` option:

.. code-block:: text

    strictdoc export . --experimental-enable-file-traceability --output-dir output/

Currently, StrictDoc looks for source files in a directory from which the
``strictdoc`` command is run.

The ``tests/integration/examples`` folder contains executable examples including
the example of requirements-to-source-code traceability.

ReqIF support
=============

StrictDoc has an initial support of exporting to and importing from the ReqIF
format.

**Note:** It is not possible to implement a single export/import procedure that
works well for all ReqIF XML files produced by various requirements management
tools. The export/import workflow is therefore tool-specific. See
`ReqIF implementation details`_ for more details.

Supported formats:

- StrictDoc's "native" export/import between SDoc and ReqIF

Planned formats:

- The format recommended by the
  `ReqIF Implementation Guide <https://www.prostep.org/fileadmin/downloads/PSI_ImplementationGuide_ReqIF_V1-7.pdf>`_
  that attempts to harmonize the developments of ReqIF by requirements
  management tools.

Import flow (ReqIF -> SDoc):
----------------------------

.. code-block:: text

    strictdoc import reqif sdoc input.reqif output.sdoc

The command does the following:

1. The ReqIF is parsed from XML file to ReqIF in-memory model using the ``reqif``
   library.

2. The ReqIF in-memory model is converted to SDoc in-memory model. In this case,
   ``sdoc`` indicates that the native ReqIF-to-SDoc conversion procedure must be
   used.

3. The SDoc in-memory model is written to an .sdoc file.

Export flow (SDoc -> ReqIF)
---------------------------

.. code-block:: text

    strictdoc export --formats=reqif-sdoc %S/input.sdoc

The command does the following:

1. The SDoc file is parsed to an SDoc in-memory model.
2. The SDoc in-memory model is converted to a ReqIF in-memory model using the
   native SDoc-to-ReqIF conversion procedure as indicated by the ``reqif-sdoc``
   argument.
3. The ReqIF in-memory model is unparsed a to ReqIF XML file using ``reqif``
   library.

ReqIF implementation details
----------------------------

The ReqIF is a `standard <https://www.omg.org/spec/ReqIF>`_ which is
maintained by Object Management Group (OMG). One important feature of the
ReqIF standard is that it requires a fixed XML structure but still leaves
certain details open to the implementation by the ReqIF and requirements
management tools developers. Specifically, each tool may use it own field
names and structure to represent requirements and sections/chapters.

In order to accommodate for the differences between ReqIF files produced by
various tools, the ReqIF processing is split into two layers:

1) Parsing ReqIF from ``.reqif`` XML files into ReqIF in-memory tree of Python
objects as well as unparsing the ReqIF in-memory tree back to ReqIF XML files is
extracted to a separate library:
`strictdoc-project/reqif <https://github.com/strictdoc-project/reqif>`_.

2) Converting between in-memory trees of SDoc and ReqIF. This layer is part of
StrictDoc.

For further overview of the ReqIF format and the ``reqif`` library's
implementation details, refer to
`strictdoc-project/reqif <https://github.com/strictdoc-project/reqif>`_'s
documentation.

Excel support
=============

StrictDoc provides a support for Excel XLS on input and Excel XLSX on output.

On input, the headers of sheet1 are used to put together a custom grammar and
the requirements are imported one row per requirement. A best effort is made by
the importer to recognize names of headers and map these to strictdoc
requirement fields.

Note: A roundtrip "SDoc -> Excel -> SDoc" is not yet supported.

Import flow (Excel XLS -> SDoc):
--------------------------------

.. code-block:: text

    strictdoc import excel basic input.xls output.sdoc

The command does the following:

1. The Excel XLS is parsed to SDoc in-memory model using the ``xlrd``
   library.

2. The SDoc in-memory model is written to an .sdoc file.

Export flow (SDoc -> Excel XLSX)
--------------------------------

.. code-block:: text

    strictdoc export --formats=excel --output-dir=Output input.sdoc

The command does the following:

1. The SDoc file is parsed to an SDoc in-memory model.

2. The SDoc in-memory model is converted to an Excel XLSX file using
   the ``XlsWriter`` library

Options
=======

Project title
-------------

By default, StrictDoc generates a project tree with a project title
"Untitled Project". To specify the project title use the option
``--project-title``.

.. code-block:: text

    strictdoc export --project-title "My Project" .

Parallelization
---------------

To improve performance for the large document trees (1000+ requirements),
StrictDoc parallelizes reading and generation of the documents using
process-based parallelization: ``multiprocessing.Pool`` and
``multiprocessing.Queue``.

Parallelization improves performance but can also complicate understanding
behavior of the code if something goes wrong.

To disable parallelization use the ``--no-parallelization`` option:

.. code-block:: text

    strictdoc export --no-parallelization docs/

**Note:** Currently, only the generation of HTML documents is parallelized, so
this option will only have effect on the HTML export. All other export options
are run from the main thread. Reading of the SDoc documents is parallelized for
all export options and is disabled with this option as well.

