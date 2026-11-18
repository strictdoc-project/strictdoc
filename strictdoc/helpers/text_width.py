"""
The width of text, as docutils measures it in grid tables.

A wide or full-width East Asian character, for example, a CJK character or
an emoji, takes the width of two characters (see
docutils.statemachine.StringList.pad_double_width()). Every other character
takes the width of one character, also a character outside the BMP. The
table editor of the Web UI (table_editor.js) measures text in the same way.

Docutils takes the width of a character from the unicodedata module of the
running Python, and the Unicode version of this module depends on the Python
version. The table editor gets the ranges of the double-width characters
from the server (see double_width_ranges()), so it uses the same Unicode
version as docutils.
"""

from functools import lru_cache
from typing import List, Tuple
from unicodedata import east_asian_width

LAST_CODE_POINT = 0x10FFFF


def is_double_width(character: str) -> bool:
    return east_asian_width(character) in "WF"


def text_width(text: str) -> int:
    return sum(2 if is_double_width(character_) else 1 for character_ in text)


@lru_cache(maxsize=1)
def double_width_ranges() -> List[Tuple[int, int]]:
    """
    Return the code point ranges of the double-width characters, as
    (first, last) pairs in ascending order.
    """

    ranges: List[Tuple[int, int]] = []
    first = None
    for code_point_ in range(LAST_CODE_POINT + 1):
        if is_double_width(chr(code_point_)):
            if first is None:
                first = code_point_
        elif first is not None:
            ranges.append((first, code_point_ - 1))
            first = None
    if first is not None:
        ranges.append((first, LAST_CODE_POINT))
    return ranges
