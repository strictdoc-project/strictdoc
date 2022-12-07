Developer Guide
$$$$$$$$$$$$$$$

This section contains everything that a StrictDoc developer/contributor should know to get the job done.

Getting started
===============

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

Invoke for development tasks
============================

Make sure to familiarize yourself with the available developer tasks by running:

.. code-block:: bash

    invoke --list

Frontend development
====================

The shortest path to run the server when the StrictDoc's source code is cloned:

.. code-block:: bash

    invoke server

Running integration tests
=========================

The integration tests are run using Invoke:

.. code-block:: bash

    invoke test-integration

The ``--focus`` parameter can be used to run only selected tests that match a given substring. This helps to avoid running all tests all the time.

.. code-block:: bash

    invoke test-integration --focus <keyword>


Generating documentation locally
================================

The following Invoke task generates StrictDoc's documentation to StrictDoc and Sphinx:

.. code-block:: bash

    invoke sphinx

