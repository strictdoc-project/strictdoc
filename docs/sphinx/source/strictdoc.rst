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
- Special fields support. The StrictDoc's grammar can be extended to support
  arbitrary special fields, such as ``PRIORITY``, ``OWNER``, or even more
  specialized fields, such as ``Automotive Safety Integrity Level (ASIL)`` or
  ``ECSS verification method``.
- Good performance of the `textX <https://github.com/textX/textX>`_
  parser and parallelized incremental generation of documents: generation of
  document trees with up to 2000-3000 requirements into HTML pages stays within
  a few seconds. From the second run, only changed documents are regenerated.
  Further performance tuning should be possible.

**Warning:** The StrictDoc project is alpha quality. See the
`Backlog`_ section to get an idea of the overall project direction.

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

StrictDoc uses Poetry, so `Poetry <https://python-poetry.org>`_ has to be
installed. To install Poetry, read the instructions here:
`Poetry / Installation <https://python-poetry.org/docs/#installation>`_.

When Poetry is installed, clone StrictDoc:

.. code-block:: text

    git clone https://github.com/strictdoc-project/strictdoc.git && cd strictdoc
    poetry install
    poetry run strictdoc
    poetry run invoke test

StrictDoc can also be developed and run without Poetry:

.. code-block:: text

    git clone https://github.com/strictdoc-project/strictdoc.git && cd strictdoc
    pip install -r requirements.txt
    python3 strictdoc/cli/main.py
    # for running tests:
    pip install invoke pytest pytidylib html5lib
    invoke test

Installing StrictDoc into a Docker container
--------------------------------------------

StrictDoc can be invoked inside of a Docker container. To make data available
to the Docker container (here: ``strictdoc:0.0.18``) as well as the host system
one needs to mount a volume via ``-v`` option.

In the host operating system terminal:

.. code-block:: text

    docker build . -t strictdoc:0.0.18
    docker run --name strictdoc --rm -v "$(pwd)/docs:/data" -i -t strictdoc:0.0.18

In the container terminal:

.. code-block:: text

    bash-5.1# strictdoc export .
    bash-5.1# exit

The documentation resides in ``./docs/output/html``.

Installing StrictDoc as a snap package
--------------------------------------

This installation variant is available in UNIX operating systems with support
of the `snap package format <https://snapcraft.io/docs/snap-format>`_.

.. code-block:: text

    wget https://github.com/strictdoc-project/strictdoc/raw/developer/snap/snap/strictdoc_0.0.18_amd64.snap
    sudo snap install strictdoc_*.snap --devmode --dangerous

Installing StrictDoc as a brew package
--------------------------------------

This installation variant is available in Mac OS and UNIX operating systems with
support of the `brew package format <https://brew.sh/>`_. This includes the Linux
operating systems CentOS, Debian, Fedora, Red Hat and Ubuntu.

.. code-block:: text

    brew tap strictdoc-project/strictdoc
    brew install strictdoc-project/strictdoc

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

  - ``FREE_TEXT``

- ``REQUIREMENT`` and ``COMPOSITE_REQUIREMENT``

- ``SECTION``

  - ``FREE_TEXT``

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

Supported configuration fields:

``SPECIAL_FIELDS`` (see Requirement / Special fields below).

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
- ``SPECIAL_FIELDS``
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

Special fields
^^^^^^^^^^^^^^

**Observation:** Different industries have their own types of requirements
documents. These documents often have specialized meta information which is
different from industry to industry. Example: ``ECSS_VERIFICATION`` field in the
European space industry or ``ASIL`` in the automotive industry.

StrictDoc allows extending its grammar with custom fields that are specific to
a particular document.

First, such fields have to be registered on a document level using the
``SPECIAL_FIELDS`` field:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc
    SPECIAL_FIELDS:
    - NAME: ASIL
      TYPE: String
    - NAME: ECSS_VERIFICATION
      TYPE: String
      REQUIRED: Yes

This registration adds these fields to the parser that will recognize them
as special fields defined by a user. Declaring a special field as
``REQUIRED: Yes`` makes this field mandatory for each and every requirement in
the document.

When the fields are registered on the document level, it becomes possible to
declare them as the ``[REQUIREMENT]`` special fields:

.. code-block:: text

    [DOCUMENT]
    TITLE: StrictDoc

    [REQUIREMENT]
    UID: REQ-001
    SPECIAL_FIELDS:
      ASIL: D
      ECSS_VERIFICATION: R,A,I,T
    STATEMENT: StrictDoc shall enable requirements management.

**Note:** The ``TYPE: String`` is the only supported type of a special field. In
the future, more specialized types are envisioned, such as ``Int``, ``Enum``,
``Tag``.

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
- `fmStudio <http://formalmind.com/studio>`_'s ReqIF. Only import from ReqIF to
  SDoc is supported.

Planned formats:

- The format recommended by the
  `ReqIF Implementation Guide <https://www.prostep.org/fileadmin/downloads/PSI_ImplementationGuide_ReqIF_V1-7.pdf>`_
  that attempts to harmonize the developments of ReqIF by requirements
  management tools.
- `ProR <http://pror.org>`_
- Doors
- Enterprise Architect
- and others

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
implementation details, refer to the
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

StrictDoc Requirements
======================

Project goals
-------------

.. _GOAL-1-TOOL-SUPPORT:

Software support for writing requirements and specifications documents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~

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

High-level requirements
-----------------------

.. _SDOC-HIGH-REQS-MANAGEMENT:

Requirements management
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-REQS-MANAGEMENT

StrictDoc shall enable requirements management.

**Parents:**

- ``[GOAL-1-TOOL-SUPPORT]`` :ref:`GOAL-1-TOOL-SUPPORT`

**Children:**

- ``[SDOC-DM-MODEL]`` :ref:`SDOC-DM-MODEL`

.. _SDOC-HIGH-DATA-MODEL:

Data model
~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-DATA-MODEL

StrictDoc shall be based on a well-defined data model.

**Comment:** StrictDoc is a result of several attempts to find a solution for working with
text-based requirements:

- StrictDoc, first generation: Markdown-based C++ program. Custom requirements
  metadata in YAML.
- StrictDoc, second generation: RST/Sphinx-based Python program. Using Sphinx
  extensions to manage meta information.

The result of these efforts was the realization that a text-based requirements
and specifications management tool could be built on top of a domain-specific
language (DSL) created specifically for the purpose of writing requirements and
specifications documents. Such a language allows an explicit definition of a
document data model which is called "grammar".

**Children:**

- ``[SDOC-DM-MODEL]`` :ref:`SDOC-DM-MODEL`
- ``[SDOC-FMT-GRAMMAR]`` :ref:`SDOC-FMT-GRAMMAR`

Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall provide a command-line interface.

Platform support
~~~~~~~~~~~~~~~~

StrictDoc shall work on all major platforms.

macOS support
^^^^^^^^^^^^^

StrictDoc shall work on macOS systems.

Linux support
^^^^^^^^^^^^^

StrictDoc shall work on Linux systems.

Windows support
^^^^^^^^^^^^^^^

StrictDoc shall work on Windows systems.

.. _SDOC-HIGH-VALIDATION:

Requirements validation
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-VALIDATION

StrictDoc shall allow validation of requirement documents.

**Children:**

- ``[SDOC-VALIDATION-UNIQUE-UID]`` :ref:`SDOC-VALIDATION-UNIQUE-UID`
- ``[SDOC-VALIDATION-NO-CYCLES]`` :ref:`SDOC-VALIDATION-NO-CYCLES`
- ``[SDOC-VALIDATION-VALID-HTML]`` :ref:`SDOC-VALIDATION-VALID-HTML`

Requirements text format
~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall allow storage of requirements in a plain-text human readable form.

Linking requirements
~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support linking requirements to each other.

Scalability
~~~~~~~~~~~

StrictDoc shall allow working with large documents and document trees containing at least 10000 requirement items.

.. _SDOC-HIGH-REQS-TRACEABILITY:

Traceability
~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-HIGH-REQS-TRACEABILITY

StrictDoc shall support traceability of requirements.

Visualization
~~~~~~~~~~~~~

StrictDoc shall provide means for visualization of requirement documents.

Open source software
~~~~~~~~~~~~~~~~~~~~

StrictDoc shall always be free and open source software.

Implementation requirements
---------------------------

.. _SDOC-IMPL-PARAL:

Parallelization
~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-IMPL-PARAL

StrictDoc shall enable parallelization of the time-consuming parts of the code.

.. _SDOC-IMPL-INCREMENTAL:

Incremental generation
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-IMPL-INCREMENTAL

StrictDoc shall enable incremental generation of the documents.

**Comment:** When exporting documentation tree, StrictDoc shall regenerate only changed
documents and files.

Data model
----------

.. _SDOC-DM-MODEL:

Modeling capability
~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-DM-MODEL

StrictDoc's Data Model shall accommodate for maximum possible standard requirement document formats.

**Comment:** Examples of standard requirements documents include but are not limited to:

- Non-nested requirement lists split by categories
  (e.g., Functional Requirements, Interface Requirements, Performance Requirements, etc.)

**Parents:**

- ``[SDOC-HIGH-REQS-MANAGEMENT]`` :ref:`SDOC-HIGH-REQS-MANAGEMENT`
- ``[SDOC-HIGH-DATA-MODEL]`` :ref:`SDOC-HIGH-DATA-MODEL`

**Children:**

- ``[SDOC-FMT-PRIMARY]`` :ref:`SDOC-FMT-PRIMARY`

Project
~~~~~~~

StrictDoc shall support the "Project" concept as a top-level entity that serves
for grouping of SDoc documents into a single project documentation tree.

Project title
^^^^^^^^^^^^^

Project shall have a "Title" property.

**Comment:** Currently, the project title aspect is not part of the SDoc grammar. It is
simply specified via the ``--project-title`` command-line option. This might
change when the project title will be configured as part of the project-level
config file (TOML or SDoc-like grammar).

Document
~~~~~~~~

TBD

Section
~~~~~~~

TBD

Requirement item
~~~~~~~~~~~~~~~~

Statement
^^^^^^^^^

Requirement item shall have a statement.

Content body
^^^^^^^^^^^^

Requirement item might have an content body.

UID identifier
^^^^^^^^^^^^^^

Requirement item might have an UID identifier.

UID identifier format
"""""""""""""""""""""

StrictDoc shall not impose any restrictions on the UID field format.

**Comment:** Conventions used for requirement UIDs can be very different. And there seems to
be no way to define a single rule.

Some examples:

- FUN-003
- cES1008, cTBL6000.1 (NASA cFS)
- Requirements without a number, e.g. SDOC-HIGH-DATA-MODEL (StrictDoc)
- SAVOIR.OBC.PM.80 (SAVOIR)

Title
^^^^^

Requirement item might have an title.

References
^^^^^^^^^^

Requirement item might have one or more references.

Comments
^^^^^^^^

Requirement item might have one or more comments.

Special fields
^^^^^^^^^^^^^^

StrictDoc shall support customization of the default Requirement's grammar with special fields.

**Comment:** Examples:

- RAIT compliance fields (Review of design, analysis, inspection, testing)
- Automotive Safety Integrity Level level (ASIL).

Composite Requirement item
~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

Links
~~~~~

StrictDoc's data model shall support linking document content nodes to each other.

Parent links
^^^^^^^^^^^^

StrictDoc's data model shall support linking a requirement to another requirement using PARENT link.

SDoc file format
----------------

.. _SDOC-FMT-PRIMARY:

Primary text implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-FMT-PRIMARY

The SDoc format shall support encoding the Strict Doc Data Model in a plain-text human readable form.

**Parents:**

- ``[SDOC-DM-MODEL]`` :ref:`SDOC-DM-MODEL`

.. _SDOC-FMT-GRAMMAR:

Grammar
~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-FMT-GRAMMAR

The SDoc format shall be based on a fixed grammar.

**Parents:**

- ``[SDOC-HIGH-DATA-MODEL]`` :ref:`SDOC-HIGH-DATA-MODEL`

No indentation
^^^^^^^^^^^^^^

The SDoc grammar's building blocks shall not allow any indentation.

**Comment:** Rationale: Adding indentation to any of the fields does not scale well when the
documents have deeply nested section structure as well as when the size of the
paragraphs becomes sufficiently large. Keeping every keyword like [REQUIREMENT]
or [COMMENT] with no indentation ensures that one does not have to think about
possible indentation issues.

Type safety
~~~~~~~~~~~

The SDoc format shall allow type-safe encoding of requirement documents.

Export and import capabilities
------------------------------

General
~~~~~~~

Generated file names
^^^^^^^^^^^^^^^^^^^^

StrictDoc shall preserve original document file names when generating to all
export formats.

HTML Export
~~~~~~~~~~~

Single document: Normal form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export single document pages in a normal document-like form.

Single document: Tabular form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export single document pages in a tabular form.

Single document: 1-level traceability
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export 1-level traceability document.

**Parents:**

- ``[SDOC-HIGH-REQS-TRACEABILITY]`` :ref:`SDOC-HIGH-REQS-TRACEABILITY`

Single document: Deep traceability
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export deep traceability document.

**Parents:**

- ``[SDOC-HIGH-REQS-TRACEABILITY]`` :ref:`SDOC-HIGH-REQS-TRACEABILITY`

Left panel: Table of contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall export all HTML pages with Table of Contents.

PDF Export
~~~~~~~~~~

Sphinx documentation generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support exporting documents to Sphinx/RST format.

.. _SDOC-GEN-EXCEL-EXPORT:

Excel Export
~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-GEN-EXCEL-EXPORT

StrictDoc shall support exporting documents to Excel format.

ReqIF import/export
~~~~~~~~~~~~~~~~~~~

StrictDoc shall support the ReqIF format.

Validation
----------

.. _SDOC-VALIDATION-UNIQUE-UID:

Uniqueness of UID identifiers in a document tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-VALIDATION-UNIQUE-UID

StrictDoc shall ensure that each UID used in a document tree is unique.

**Comment:** This is implemented but the error message shall be made more readable.

**Parents:**

- ``[SDOC-HIGH-VALIDATION]`` :ref:`SDOC-HIGH-VALIDATION`

.. _SDOC-VALIDATION-NO-CYCLES:

No cycles in a document tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-VALIDATION-NO-CYCLES

StrictDoc shall ensure that no requirements in document tree reference each other.

**Parents:**

- ``[SDOC-HIGH-VALIDATION]`` :ref:`SDOC-HIGH-VALIDATION`

.. _SDOC-VALIDATION-VALID-HTML:

Valid HTML markup
~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC-VALIDATION-VALID-HTML

StrictDoc's HTML export tests shall validate the generated HTML markup.

**Comment:** First candidate: Table of contents and its nested ``<ul>/<li>`` items.

**Parents:**

- ``[SDOC-HIGH-VALIDATION]`` :ref:`SDOC-HIGH-VALIDATION`

Design decisions
================

Building blocks
---------------

TextX
~~~~~

TextX shall be used for StrictDoc grammar definition and parsing of the sdoc files.

**Comment:** TextX is an easy-to-install Python tool. It is fast, works out of the box.

Jinja2
~~~~~~

Jinja2 shall be used for rendering HTML templates.

Sphinx and Docutils
~~~~~~~~~~~~~~~~~~~

Sphinx and Docutils shall be used for the following capabilities:

- Support of Restructured Text (reST) format
- Generation of RST documents into HTML
- Generation of RST documents into PDF using LaTeX
- Generating documentation websites using Sphinx

Backlog
=======

**Note:** The items below are weakly sorted from top to bottom. The topmost
items are either work-in-progress or will be implemented next.

Work in progress
----------------

Traceability and coverage
~~~~~~~~~~~~~~~~~~~~~~~~~

Linking with implementation artifacts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall support linking requirements to files.

Validation: Broken links from requirements to source files
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

StrictDoc shall warn a user about all requirements whose links reference source
files that do not exist.

Validation: Broken links from source files to requirements
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

StrictDoc shall warn a user about all source files whose links reference
requirements that do not exist.

Requirements coverage
^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall generate requirements coverage information.

**Comment:** Requirements coverage screen shows how requirements are linked with source files.

Source coverage
^^^^^^^^^^^^^^^

StrictDoc shall generate source coverage information.

**Comment:** Source coverage screen shows how source files are linked with requirements.

Document archetypes
-------------------

StrictDoc shall support the following document archetypes: **requirements document**
and **specification** document. For both archetypes, StrictDoc shall further
support the following options.

.. list-table:: Table: Requirements and specification document
   :widths: 20 40 40
   :header-rows: 1

   * -
     - Requirements document
     - Specification document
   * - Examples
     - Most typical: requirements lists split by categories (e.g., Functional
       Requirements, Interface Requirements, Performance Requirements, etc.)
     - Often: a standard document
   * - Structure
     - Not nested or not too deeply nested
     - Nested
   * - Visual presentation
     - Requirements are often presented as table cells. Cells can be standalone
       or the whole section or document can be a long table with cells.
     - Requirements are rather presented as header + text
   * - Unique requirement identifiers (UID)
     - Most always
     - - Present or not
       - **NOT SUPPORTED YET:** Can be missing, the chapter headers are used instead.
         The combination "Number + Title" becomes a reference-able identifier.
         A possible intermediate solution when modeling such a document is to
         make the UIDs map to the section number.
   * - Requirement titles
     - - Often
       - **NOT SUPPORTED YET:** But maybe absent (ex: NASA cFS SCH). If absent,
         the grouping is provided by sections.
     - Requirement titles are most often section titles
   * - Real-world examples
     - - NASA cFE Functional Requirements
       - MISRA C coding guidelines,
       - NASA Software Engineering Requirements NPR 7150.2
     - - ECSS Software ECSS-E-ST-40C

**Comment:** This draft requirement is the first attempt to organize this information.

Project-level configuration file
--------------------------------

StrictDoc shall support reading project configuration from a file.

**Comment:** - TOML format looks like a good option.

- Project title.

- Project prefix?

- Explicit or wildcard paths to sdoc files.

- Paths to dirs with source files.

- Config options for presenting requirements.

  - Include/exclude requirements in TOC

Further export and import capabilities
--------------------------------------

CSV import/export
~~~~~~~~~~~~~~~~~

StrictDoc shall support exporting documents to CSV format.

PlantUML export
~~~~~~~~~~~~~~~

StrictDoc shall support exporting documents to PlantUML format.

Confluence import/export
~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support importing/exporting documents from/to Confluence HTML storage format.

Tex export
~~~~~~~~~~

StrictDoc shall support exporting documents to Tex format.

Doorstop import/export
~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support import and exporting documents from/to
`Doorstop <https://github.com/doorstop-dev/doorstop>`_ format.

Markdown support for text and code blocks
-----------------------------------------

StrictDoc shall support rendering text/code blocks into Markdown syntax.

StrictDoc as library
--------------------

StrictDoc shall support it use as a Python library.

**Comment:** Such a use allows a more fine-grained access to the StrictDoc's modules, such
as Grammar, Import, Export classes, etc.

.. _BACKLOG-FUZZY-SEARCH:

Fuzzy requirements search
-------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - BACKLOG-FUZZY-SEARCH

StrictDoc shall support finding relevant requirements.

**Comment:** This feature can be implemented in the CLI as well as in the future GUI. A fuzzy
requirements search can help to find existing requirements and also identify
relevant requirements when creating new requirements.

**Parents:**

- ``[GOAL-4-CHANGE-MANAGEMENT]`` :ref:`GOAL-4-CHANGE-MANAGEMENT`

Filtering by tags
-----------------

StrictDoc shall support filtering filtering by tags.

Advanced
--------

Requirement checksumming
~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support calculation of checksums for requirements.

**Comment:** This feature is relatively easy to implement but the implementation is postponed
until the linking between requirements and files is implemented.

Graphical User Interface (GUI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall provide a Graphical User Interface (GUI).

**Comment:** Several trade-offs to consider:

- Desktop vs Web. Rather web-based, i.e. Python backend and JS frontend, but
  which technology?
- Still keep the current behavior of a statically generated website?

Web server and editable HTML pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

StrictDoc shall provide a web server that serves as a StrictDoc backend for
reading and writing SDoc files.

Facts table. Invariants calculation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StrictDoc shall support creation of fact tables and allow calculation of
invariants for constraints enforcement.

FMEA/FMECA tables
~~~~~~~~~~~~~~~~~

StrictDoc shall support creation of FMEA/FMECA safety analysis documents.

Open questions
--------------

One or many input sdoc trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

