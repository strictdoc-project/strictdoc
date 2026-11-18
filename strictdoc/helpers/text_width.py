"""
The width of text, as docutils measures it in grid tables.

A wide or full-width East Asian character, for example, a CJK character or
an emoji, takes the width of two characters (see
docutils.statemachine.StringList.pad_double_width()). Every other character
takes the width of one character, also a character outside the BMP. The
table editor of the Web UI (table_editor.js) measures text in the same way.
"""

from unicodedata import east_asian_width


def is_double_width(character: str) -> bool:
    return east_asian_width(character) in "WF"


def text_width(text: str) -> int:
    return sum(2 if is_double_width(character_) else 1 for character_ in text)
