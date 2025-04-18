import re
from typing import Match

WS = "[ \t]"


def preprocess_source_code_comment(comment: str) -> str:
    """
    Remove all Doxygen/Python/etc comment markers for processing.
    """

    def replace_with_spaces(match: Match[str]) -> str:
        # Return a string of spaces with the same length as the matched text.
        return " " * len(match.group(0))

    return re.sub(
        rf"(^/\*\*)|^{WS}*\*/?|(^///)|(^//)|(^#+)",
        replace_with_spaces,
        comment,
        flags=re.MULTILINE,
    )
