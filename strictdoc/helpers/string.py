import re
from typing import Optional

REGEX_TRAILING_WHITESPACE_SINGLELINE = re.compile(r"\s{2,}")
REGEX_TRAILING_WHITESPACE_MULTILINE = re.compile(r" +\n")


def get_lines_count(string):
    # TODO: Windows strings
    count = string.count("\n")
    if string[-1] != "\n":
        count += 1
    return count


# https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
# https://stackoverflow.com/a/6117124/598057
def multireplace(string, replacements):
    # Place longer ones first to keep shorter substrings from matching where the
    # longer ones should take place. For instance, given the replacements:
    # {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)

    pattern = re.compile("|".join(rep_escaped), 0)
    return pattern.sub(lambda match: replacements[match.group(0)], string)


def escape(string: str) -> str:
    return string.encode("unicode_escape").decode("utf-8")


def unescape(string: str) -> str:
    return string.encode("utf-8").decode("unicode_escape")


def sanitize_html_form_field(
    field: Optional[str], multiline: bool
) -> Optional[str]:
    if field is not None:
        assert isinstance(field, str), field
        if len(field) > 0:
            sanitized_field: str = field.strip()
            if len(sanitized_field) > 0:
                if multiline:
                    return REGEX_TRAILING_WHITESPACE_MULTILINE.sub(
                        "\n", sanitized_field
                    )
                sanitized_field = sanitized_field.replace("\r\n", "")
                return REGEX_TRAILING_WHITESPACE_SINGLELINE.sub(
                    " ", sanitized_field
                )

    return None
