"""
@relation(SDOC-SRS-142, scope=file)
"""

import re
from typing import Match

WS = "[ \t]"


def preprocess_source_code_comment(comment: str) -> str:
    """
    Remove all Doxygen/Python/etc comment markers for processing.

    FIXME: Maybe there is a more efficient way of doing this with no two
           re.sub() calls.
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
    return re.sub(
        r"^[ \t]+$",
        "",
        replacement,
        flags=re.MULTILINE,
    )
