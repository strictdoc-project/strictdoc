.. _SDOC_DD:

Design Document
$$$$$$$$$$$$$$$

This document describes the architecture and the implementation details of StrictDoc.

Overview
========

StrictDoc consists of two applications:

1. StrictDoc command-line application (CLI).
2. StrictDoc Web application.

Both applications share a significant subset of the backend and frontend logic. The backend logic is written in Python, the frontend logic is written using HTML/CSS, Jinja templates, and a combination of Turbo.js/Stimulus.js.

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

StrictDoc command-line application
==================================

StrictDoc command-line application is at the core of StrictDoc. The command-line interface contains commands for exporting/importing SDoc content from/to other formats and presenting documentation content to a user.

The command-line application can be seen as a Model-View-Controller application:

- A command entered by a user gets recognized by the CLI arguments parser.
- Depending on the type of command, a responsible Action (Controller layer) processes the command (export action, import action, etc.).
- The input of the command is transformed by the action using the backend (Model layer) (SDoc, ReqIF, Excel, etc.).
- The resulting output is written back to HTML or other formats (View layer).

StrictDoc Web application
=========================

StrictDoc Web application is based on FastAPI / Uvicorn. The end-to-end usage cycle of the web application is as follows:

- A browser requests documents from a FastAPI server.
- The FastAPI web server parses the SDoc files into memory and converts them into HTML using Jinja templates. The resulting HTML output is given back to the user.
- The Jinja templates are extended with JavaScript logic that allows a user to edit the documents and send the updated content back to the server.
- The server writes the updated content back to the SDoc files stored on a user's file system.

The HTML Over the Wire (Hotwire) architecture
---------------------------------------------

StrictDoc uses the `Hotwire architecture <https://hotwired.dev>`_.

The JavaScript framework used by StrictDoc is minimized to Turbo.js/Stimulus.js which helps to avoid the complexity of the larger JS frameworks such as React, Vue, Angular, etc. In accordance with the Hotwire approach, most of the StrictDoc's business logic is done on a server, while Turbo and Stimulus provide a thin layer of JS and AJAX to connect the almost static HTML with the server.

The Hotwire approach helps to reduce the differences between the static HTML produced by the StrictDoc command-line application and the StrictDoc web application. In both cases, the core content of StrictDoc is a statically generated website with documents. The Web application extends the static HTML content with Turbo/Stimulus to turn it into a dynamic website.

Currently, the Web server renders the HTML documents using the same generators that are used by the static HTML export, so the static HTML documentation and the Web application interface look identical. The Web interface adds the action buttons and other additional UI elements for editing the content.

Implementation details
======================

This section documents some non-obvious implementation details.

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
