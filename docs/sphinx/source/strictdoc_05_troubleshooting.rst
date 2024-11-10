.. _SDOC_TROUBLESHOOTING:

Troubleshooting
$$$$$$$$$$$$$$$

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 7e3481d51ad14767b5c97132cad2e0a6

This document summarizes solutions to the most common issues reported by StrictDoc users.

Caching issues
==============

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 9a32ac13510d401cbc1a608259652c78

.. note::

    **TL;DR:** If you encounter errors related to reading data, make sure to delete the StrictDoc cache folder located at ``$TMPDIR/strictdoc_cache`` or in the custom directory if specified by the ``cache_dir`` option in the ``strictdoc.toml`` configuration file.

StrictDoc caches many artifacts on disk. Some artifacts are cached using Python’s `pickle <https://docs.python.org/3/library/pickle.html>`_ module, while others are written directly to disk.

The pickle module serializes Python objects to disk. The issue with this approach is that when StrictDoc changes the schema of its objects (e.g., when SDocNode or SDocDocument objects gain a new property or a property type changes), an outdated object may be read from the cache after upgrading to a new StrictDoc version. While a more systematic solution might be implemented in the future, the current workaround is to manually delete the StrictDoc cache folder.
