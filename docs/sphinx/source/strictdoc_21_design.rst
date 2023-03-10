Design Document
$$$$$$$$$$$$$$$

Building blocks
===============

StrictDoc is based on the following open-source libraries and tools:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - **Library/tool**
     - **Description**

   * - TextX
     - Used for StrictDoc grammar definition and parsing of the sdoc files.

   * - Jinja
     - Rendering HTML templates.

   * - Sphinx and Docutils
     - - Support of Restructured Text (reST) format
       - Generation of RST documents into HTML
       - Generation of RST documents into PDF using LaTeX
       - Generating documentation websites using Sphinx.

   * - FastAPI
     - Server used for StrictDoc's Web-based user interface.

   * - Turbo and Stimulus
     - Javascript frameworks used for StrictDoc's Web-based user interface.

   * - Selenium and SeleniumBase
     - Used for end-to-end testing of StrictDoc's Web-based user interface.

Graphical user interface
========================

- Web interface is based on FastAPI / Uvicorn serving Jinja templates.
- The Javascript is minimized to Turbo/Stimulus to avoid the complexity of JS frameworks such as React, Vue, Angular, etc.
- Uvicorn web server that serves as a StrictDoc backend for reading and writing SDoc files.

- Several trade-offs to consider:

  - Desktop vs Web. Rather web-based, i.e. Python backend and JS frontend, but which technology?

- Keep the current behavior of a statically generated website.

Implementation details
======================

SDOC_IMPL_1: Exporting document free text to ReqIF and vice versa
-----------------------------------------------------------------

ReqIF format does not seem to provide a dedicated convention for a text node to be distinguished from a requirement or a section. StrictDoc implements a workaround: the document's free text is converted to a section with a ``ChapterName`` field that equals "Abstract". And the other way round: when a ReqIF-to-SDoc converter encounters the first section of a document to be "Abstract", it is converted to a free text.

.. _SDOC_IMPL_2:

SDOC_IMPL_2: Running out of semaphores on macOS
-----------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - SDOC_IMPL_2

This an edge case on macOS: Python crashes in the Parallelizer class when
creating an output queue:

.. code-block:: py

    self.output_queue = multiprocessing.Queue()

The fragment of the crash:

.. code-block:: text

    sl = self._semlock = _multiprocessing.SemLock(
    OSError: [Errno 28] No space left on device
