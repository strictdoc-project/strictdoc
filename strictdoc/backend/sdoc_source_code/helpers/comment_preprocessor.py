"""
@relation(SDOC-SRS-142, scope=file)
"""

import re
from typing import Match

WS = "[ \t]"


def preprocess_source_code_comment(comment: str) -> str:
    """
    Replace all Doxygen/Python/etc comment markers with spaces for easier processing.

    Note that the replacement does not change the size of the input string. This is
    important for the use case when StrictDoc writes the mutated code comments
    back to source files.
    """

    def replace_with_spaces(match: Match[str]) -> str:
        # Return a string of spaces with the same length as the matched text.
        return " " * len(match.group(0))

    replacement = re.sub(
        rf"(^/\*\*)|^{WS}*\*/?|(^///)|(^//)|(^#+)",
        replace_with_spaces,
        comment,
        flags=re.MULTILINE,
    )
    return replacement
