"""
@relation(SDOC-SRS-149, scope=file)
"""

import string
from typing import Dict, List

from strictdoc.helpers.rst import VALID_AFTER_INLINE_MARKUP


class RstInlineLinkPlaceholders:
    """
    Keeps the inline links of an RST field out of the docutils input.

    Docutils must see each [LINK: ...] as text of the same length as in the
    source. A grid table is valid only if its "|" and "+" characters stand at
    the same columns in all lines. A link that is rendered in place, for
    example as a :rawhtml: role with the full <a> tag, is longer than its
    source text. It moves the cell borders, and docutils rejects the table
    as malformed.

    So a link goes into the docutils input as a placeholder: a plain word of
    letters and digits with the length of the link source text. Docutils
    renders the placeholder as text, and replace_placeholders() then puts
    the link HTML in its place.

    A placeholder is a word, so a letter or a digit after it only makes the
    word longer, which is harmless. Other characters can form markup
    together with the word, for example "_" makes it a hyperlink reference.
    Such a character is escaped with a backslash, and the placeholder is one
    character shorter to keep the length.
    """

    def __init__(self, text_parts: List[str]) -> None:
        self.prefix: str = self._select_prefix(text_parts)
        self.html_by_placeholder: Dict[str, str] = {}

    def create_placeholder(
        self, source_length: int, link_html: str, text_after: str
    ) -> str:
        escape = self._needs_escape(text_after)
        placeholder_length = source_length - 1 if escape else source_length

        # The "x" after the index ends the index, so no placeholder is a
        # part of another placeholder.
        index = len(self.html_by_placeholder)
        placeholder = f"{self.prefix}{index}x".ljust(placeholder_length, "x")
        self.html_by_placeholder[placeholder] = link_html

        return placeholder + "\\" if escape else placeholder

    def replace_placeholders(self, html: str) -> str:
        for placeholder_, link_html_ in self.html_by_placeholder.items():
            html = html.replace(placeholder_, link_html_)
        return html

    @staticmethod
    def _needs_escape(text_after: str) -> bool:
        if len(text_after) == 0:
            return False
        first_character = text_after[0]
        return (
            first_character not in VALID_AFTER_INLINE_MARKUP
            and not first_character.isalnum()
        )

    @staticmethod
    def _select_prefix(text_parts: List[str]) -> str:
        """
        Select a prefix that does not occur in the field text.

        The shortest link source text, "[LINK: X]", has 9 characters, so the
        prefix is short: it leaves room for the index and its end marker.
        """
        text = "".join(text_parts)
        for letter_ in string.ascii_letters:
            prefix = f"Lk{letter_}"
            if prefix not in text:
                return prefix
        raise AssertionError(
            "Could not find an inline link placeholder prefix that does not "
            "occur in the field text."
        )
