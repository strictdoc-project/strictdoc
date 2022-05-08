StrictDoc Design Document
$$$$$$$$$$$$$$$$$$$$$$$$$

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

