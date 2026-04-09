"""Thin wrapper to launch the Tk-based StrictDoc launcher.

This keeps the actual implementation inside the ``strictdoc`` package so
it is also available when StrictDoc is installed (like via PyPI or something else).
"""

from strictdoc.launcher import main


if __name__ == "__main__":
    main()
