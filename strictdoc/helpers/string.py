import re
from typing import Callable, Match, Optional

REGEX_TRAILING_WHITESPACE_SINGLELINE = re.compile(r"\s{2,}")
REGEX_TRAILING_WHITESPACE_MULTILINE = re.compile(r" +\n")


# WIP: Check if this is used.
def escape(string: str) -> str:
    return string.encode("unicode_escape").decode("utf-8")


# WIP: Check if this is used.
def unescape(string: str) -> str:
    return string.encode("utf-8").decode("unicode_escape")


def sanitize_html_form_field(field: str, multiline: bool) -> str:
    assert isinstance(field, str)
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
    return ""


def is_uppercase_underscore_string(string: str) -> bool:
    first_word = r"[A-Z][A-Z0-9]*"
    other_word = r"[A-Z0-9]+"
    pattern = re.compile(rf"^{first_word}(_{other_word})*$")
    return pattern.match(string) is not None


def is_safe_alphanumeric_string(string: str) -> bool:
    pattern = re.compile(r"^[\w.]+([/\\][\w.]+?)*$")
    return pattern.match(string) is not None


def create_safe_acronym(string: str) -> str:
    words = re.split(r"[\W+]", string)
    acronym = ""
    for word in words:
        if len(word) == 0:
            continue
        if word[0].isalpha():
            acronym += word[0].upper()
    return acronym


def create_safe_title_string(string: str) -> str:
    return re.sub(r"[^\w0-9]+", "-", string).rstrip("-")


def extract_last_numeric_part(string: str) -> str:
    regex_match = re.match(".*?([0-9]+)$", string)
    if regex_match is not None:
        return regex_match.group(1)
    raise ValueError(f"Cannot extract the numeric part of UID: {string}")


def extract_numeric_uid_prefix_part(string: str) -> Optional[str]:
    regex_match = re.match(r"^([A-Za-z].*?\D)[0-9]+$", string)
    if regex_match is not None:
        return regex_match.group(1)
    return None


def create_safe_requirement_tag_string(string: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", string).rstrip("_").upper()


def create_safe_document_file_name(string: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", string).rstrip("_")


def ensure_newline(text: str) -> str:
    return text.rstrip() + "\n"


def interpolate_at_pattern_lazy(
    template: str, value_resolver: Callable[[str], str]
) -> str:
    pattern = r"@(\w+)"

    def replace_variable(match: Match[str]) -> str:
        variable_name = match.group(1)
        return value_resolver(variable_name)

    return re.sub(pattern, replace_variable, template)
