"""This module provides a helper removeprefix. (compatibility with python 3.8)"""

import sys


# TODO: Once requires_python is set to 3.9, replace with str.removeprefix() and remove this helper.
def removeprefix(s: str, prefix: str) -> str:
    if sys.version_info >= (3, 9):
        return s.removeprefix(prefix)
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s
