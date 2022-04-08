StrictDoc User Manual
$$$$$$$$$$$$$$$$$$$$$

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

Join us in Discord. Here is the invitation link: https://discord.gg/j8AC8qFp

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
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/main/docs/strictdoc.sdoc>`_.

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

Installing StrictDoc from GitHub (developer mode)
-------------------------------------------------

**Note:** Use this way of installing StrictDoc only if you want to make changes
in StrictDoc's source code. Otherwise, install StrictDoc as a Pip package
(see above).

.. code-block::

    git clone https://github.com/strictdoc-project/strictdoc.git && cd strictdoc
    pip install -r requirements.txt
    python3 strictdoc/cli/main.py

All development tasks are managed using
`Invoke <https://www.pyinvoke.org/>`_ in the ``tasks.py`` file. On macOS and
Linux, all tasks run in dedicated virtual environments. On Windows, invoke uses
the parent pip environment which can be a system environment or a user's virtual
environment.

.. code-block::

    pip install invoke  # macOS and Linux
    invoke setup-development-deps  # macOS and Linux
    pip install -r requirements.development.txt  # Windows only
    invoke --list  # See the available tasks

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
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/main/docs/strictdoc.sdoc>`_.

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

``[DOCUMENT]`` element must always be present in an SDoc document. It is a root
of an SDoc document graph.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc
    (newline)

``DOCUMENT`` declaration must always have a ``TITLE`` field. It can have
optional configuration fields and an optional ``[FREETEXT]`` block.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [FREETEXT]
    StrictDoc is software for writing technical requirements and specifications.
    [/FREETEXT]


Requirement
~~~~~~~~~~~

Minimal "Hello World" program with 3 empty requirements:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]

    [REQUIREMENT]

    [REQUIREMENT]

Supported fields:

- ``UID`` (unique identifier)
- ``REFS``
- ``TITLE``
- ``STATEMENT``
- ``RATIONALE``
- ``COMMENT`` (multiple comments are possible)

Currently, all ``[REQUIREMENT]``'s are optional but most of the time at least
the ``STATEMENT:`` field must be present as well as the ``TITLE:`` field.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    TITLE: Requirements management
    STATEMENT: StrictDoc shall enable requirements management.

**Observation:** Many real-world documents have requirements with statements and
titles but some documents only use statements without title in which case their
title becomes their UID. Example:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: REQ-001
    STATEMENT: StrictDoc shall enable requirements management.

UID
^^^

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

References
^^^^^^^^^^

The ``[REQUIREMENT]`` / ``REFS:`` field is used to connect requirements to each
other:

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
    TITLE: Requirement #2's title
    STATEMENT: Requirement #2 statement

**Note:** The ``TYPE: Parent`` is the only supported type of connection. In the
future, linking requirements to files will be possible.

**Note:** By design, StrictDoc will only show parent or child links if both
requirements connected with a reference have ``UID`` defined.

Comment
^^^^^^^

A requirement can have one or more comments explaining this requirement. The
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

Rationale
^^^^^^^^^

A requirement can have a ``RATIONALE:`` field that explains why such a
requirement exists. Like comments, the rationale field can be single-line or
multiline.

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: REQ-001
    STATEMENT: StrictDoc shall enable requirements management.
    COMMENT: Clarify the meaning or give additional information here.
    RATIONALE: The presence of the REQ-001 is justified.

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

- ``String``

- ``SingleChoice`` (Enum-like behavior, one choice is possible)
- ``MultipleChoice`` (comma-separated words with fixed options)
- ``Tag`` (comma-separated words with no fixed options)

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
    $$
    \\mathbf{\\underline{k}}_{\\text{a}} =
    \\mathbf{\\underline{i}}_{\\text{a}} \\times
    \\mathbf{\\underline{j}}_{\\text{a}}
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

StrictDoc and other tools
=========================

StrictDoc and Doorstop
----------------------

The StrictDoc project is a close successor of another project called
`Doorstop <https://github.com/doorstop-dev/doorstop>`_.

    Doorstop is a requirements management tool that facilitates the storage of
    textual requirements alongside source code in version control.

The author of Doorstop has published a `paper about Doorstop <http://www.scirp.org/journal/PaperInformation.aspx?PaperID=44268#.UzYtfWRdXEZ>`_
where the rationale behind text-based requirements management is provided.

The first version of StrictDoc had started as a fork of the Doorstop project.
However, after a while, the StrictDoc was started from scratch as a separate
project. At this point, StrictDoc and Doorstop do not share any code but
StrictDoc still shares with Doorstop their common underlying design principles:

- Both Doorstop and StrictDoc are written using Python. Both are pip packages which are easy-to-install.
- Both Doorstop and StrictDoc provide a command-line interface.
- Both Doorstop and StrictDoc use text files for requirements management.
- Both Doorstop and StrictDoc encourage collocation of code and documentation.
  When documentation is hosted close to code it has less chances of diverging
  from the actual implementation or becoming outdated.
- As the free and open source projects, both Doorstop and StrictDoc seem to
  struggle to find resources for development of specialized GUI interfaces this
  is why both tools give a preference to supporting exporting documentation
  pages to HTML format as the primary export feature.

StrictDoc differs from Doorstop in a number of aspects:

- Doorstop stores requirements in YAML files, one separate file per requirement
  (`example <https://github.com/doorstop-dev/doorstop/blob/804153c67c7c5466ee94e9553118cc3df03a56f9/reqs/REQ001.yml>`_).
  The document in Doorstop is assembled from the requirements files into a
  single logical document during the document generation process.
  StrictDoc's documentation unit is one document stored in an .sdoc file. Such a
  document can have multiple requirements grouped by sections.
- In YAML files, Doorstop stores requirements properties such as
  ``normative: true`` or ``level: 2.3`` for which Doorstop provides validations.
  Such a design decision, in fact, assumes an existence of implicitly-defined
  grammar which is encoded "ad-hoc" in the parsing and validation rules of
  Doorstop.
  StrictDoc takes a different approach and defines its grammar explicitly using
  a tool for creating Domain-Specific Languages called `textX <https://github.com/textX/textX>`_.
  TextX support allows StrictDoc to encode a strict type-safe grammar in a
  `single grammar file <https://github.com/strictdoc-project/strictdoc/blob/93486a0e9fb30b141187587eae9e995cd86c6cbf/strictdoc/backend/dsl/grammar.py>`_
  that StrictDoc uses to parse the documentation files
  using the parsing capabilities provided by textX out of the box.

The roadmap of StrictDoc contains a work item for supporting the export/import
to/from Doorstop format.

StrictDoc and Sphinx
--------------------

Both Sphinx and StrictDoc are both documentation generators but StrictDoc is at
a higher level of abstraction: StrictDoc's specialization is requirements and
specifications documents. StrictDoc can generate documentation to a number of
formats including HTML format as well as the RST format which is a default
input format for Sphinx. A two stage generation is therefore possible:
StrictDoc generates RST documentation which then can be generated to HTML, PDF,
and other formats using Sphinx.

If you are reading this documentation at
https://strictdoc.readthedocs.io/en/latest
then you are already looking at the example: this documentation stored in
`strictdoc.sdoc <https://github.com/strictdoc-project/strictdoc/blob/main/docs/strictdoc.sdoc>`_
is converted to RST format by StrictDoc which is further converted to the HTML
website by readthedocs which uses Sphinx under the hood. The
``StrictDoc -> RST -> Sphinx -> PDF`` example is also generated using readthedocs:
`StrictDoc <https://strictdoc.readthedocs.io/_/downloads/en/latest/pdf/>`_.

StrictDoc and Sphinx-Needs
--------------------------

`Sphinx-Needs <https://sphinxcontrib-needs.readthedocs.io/en/latest/>`_ is a
text-based requirements management system based on Sphinx. It is implemented
as a Sphinx extension that extends the
`reStructuredText (RST)
<https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_
markup language with additional syntax for writing requirements documents.

Sphinx-Needs was a great source of inspiration for the second version of
StrictDoc which was first implemented as a Sphinx extension and then as a more
independent library on top of `docutils <https://docutils.sourceforge.io/>`_
that Sphinx uses for the underlying RST syntax processing work.

The similarities between Sphinx-Needs and StrictDoc:

- In contrast to Doorstop, both Sphinx-Needs and StrictDoc do not split a
  document into many small files, one file per single requirement (see
  discussion
  `doorstop#401 <https://github.com/doorstop-dev/doorstop/issues/401>`_). Both
  tools follow the "file per document" approach.
- Sphinx-Needs has a
  `well-developed language
  <https://sphinxcontrib-needs.readthedocs.io/en/latest/directives/index.html>`_
  based on custom RST directives, such
  as ``req::``, ``spec::``, ``needtable::``, etc. The RST document is parsed
  by Sphinx/docutils into RST abstract syntax tree (AST) which allows creating
  an object graph out for the documents and their requirements from the RST
  document. StrictDoc uses textX for building an AST from a SDoc document.
  Essentially, both Sphinx-Needs and StrictDoc works in a similar way but use
  different markup languages and tooling for the job.

The difference between Sphinx-Needs and StrictDoc:

- RST tooling provided by Sphinx/docutils is very powerful, yet it can also be
  rather limiting. The RST syntax and underlying docutils tooling do not allow
  much flexibility needed for creating a language for defining requirements
  using a custom and explicit grammar, a feature that became a cornerstone of
  StrictDoc. This was a major reason why the third generation of
  StrictDoc started with a migration from docutils to
  `textX <https://github.com/textX/textX>`_ which is a
  dedicated tool for creating custom Domain-Specific Languages. After the
  migration to textX, StrictDoc is no longer restricted to the limitations of
  the RST document, while it is still possible to generate SDoc files to RST
  using StrictDoc and then further generate RST to HTML/PDF and other formats
  using Sphinx.
- Sphinx-Needs has an impressive list of config options and features that
  StrictDoc is missing. Examples: Customizing the look of the requirements,
  `Roles <https://sphinxcontrib-needs.readthedocs.io/en/latest/roles.html>`_,
  `Services
  <https://sphinxcontrib-needs.readthedocs.io/en/latest/services/index.html>`_
  and
  `others
  <https://sphinxcontrib-needs.readthedocs.io/en/latest/index.html>`_.

