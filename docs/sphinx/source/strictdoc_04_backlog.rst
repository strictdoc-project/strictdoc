Backlog
$$$$$$$

**Note:** The items below are weakly sorted from top to bottom. The topmost
items are either work-in-progress or will be implemented next.

Backlog: Graphical user interface
=================================

- Requirement form:

  - ``RATIONALE``
  - ``COMMENT``
  - Edit links for table-based requirements.
  - Adding/editing parent/child requirements.

- Section form:

  - ``UID``

- All forms:

  - Contextual help about the RST markup.
  - How to edit tables conveniently?

- What to do with web content going out of sync with the server/file system state?
- Issue when adding sibling section from a nested section.
- Auto-trim all single-line fields.
- Auto-trim all text areas - all trailing whitespace shall be removed.
- Enable SeleniumBase tests on CI.
- Integration with Git repository.
- Moving node up/down/left/right. For example, move a node of level 2 to level 1.
- Expand/collapse the table of contents.

- ReqIF:
  
  - Export complete documentation tree or a single document to ReqIF.
  - Import complete documentation tree or a single document from ReqIF.

- Other: 

  - Focused editing of document sections: dedicated and focused ``/sections/`` resource.
  - Non-RST markup formats.

Backlog: Nice to have
=====================

- StrictDoc as a Python library.

  - Such a use allows a more fine-grained access to the StrictDoc's modules, such as Grammar, Import, Export classes, etc.

- Data exchange with Capella tool.

  - Note: The current plan is to implement this using ReqIF export/import features.

- Language Server Protocol.

  - The LSP can enable editing of SDoc files in IDEs like Eclipse, Visual Studio, PyCharm. A smart LSP can enable features like syntax highlighting, autocompletion and easy navigation through requirements.

  - The promising base for the implementation: https://github.com/openlawlibrary/pygls.

- StrictDoc shall support rendering text/code blocks into Markdown syntax.

- Fuzzy requirements search.

  - This feature can be implemented in the CLI as well as in the future GUI. A fuzzy requirements search can help to find existing requirements and also identify relevant requirements when creating new requirements.

- Support creation of FMEA/FMECA safety analysis documents.

- Calculation of checksums for requirements.

  - This feature is relatively easy to implement, but the implementation is postponed until the linking between requirements and files is implemented.

- Filtering of requirements by tags.

- Import/export: Excel, CSV, PlantUML, Confluence, Tex, Doorstop.

- Reading project configuration from a file.
    - TOML format looks like a good option.
    - Project title.
    - Project prefix?
    - Explicit or wildcard paths to sdoc files.
    - Paths to dirs with source files.
    - Config options for presenting requirements.
        - Include/exclude requirements in TOC


Backlog: Known issues
=====================



HTML rendering using docutils is a performance bottleneck
---------------------------------------------------------

The overall generation process is still fast enough but in case some improvements were to be made:

  - It could be measured what takes more time: parsing RST tree or actually rendering HTML
  - Simplified RST parser and rendered can be written and their performance can be compared with that of docutils API.

.. code-block:: bash

    python -m cProfile -s cumulative strictdoc/cli/main.py export --no-parallelization docs/ > report.txt

See also: https://docs.python.org/3/library/profile.html#instant-user-s-manual

Document archetypes
===================

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

Open questions
==============

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

