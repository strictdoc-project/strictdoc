Design Document
$$$$$$$$$$$$$$$

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

Graphical user interface
========================

- Web interface is based on FastAPI / Uvicorn serving Jinja templates.
- The Javascript is minimized to Turbo/Stimulus to avoid the complexity of JS frameworks such as React, Vue, Angular, etc.
- Uvicorn web server that serves as a StrictDoc backend for reading and writing SDoc files.

- Several trade-offs to consider:

  - Desktop vs Web. Rather web-based, i.e. Python backend and JS frontend, but which technology?

- Keep the current behavior of a statically generated website.

