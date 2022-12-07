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

