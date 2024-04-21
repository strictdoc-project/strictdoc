# mypy: disable-error-code="no-untyped-def"
import re
from typing import List

REGEX_NAME_PART = r"[A-Za-z0-9-_\.]+"
REGEX_FILENAME = rf"{REGEX_NAME_PART}"
REGEX_FOLDER = rf"{REGEX_NAME_PART}"

REGEX_WILDCARD = REGEX_FILENAME
# FIXME: This does the job but most probably could be simplified.
REGEX_DOUBLE_WILDCARD = (
    rf"(\\|\/)?({REGEX_NAME_PART})?((\\|\/){REGEX_NAME_PART})*(\\|\/)?"
)

REGEX_MASK_VALIDATION = rf"[^(\\|\/)]{REGEX_DOUBLE_WILDCARD}"

MOST_COMMON_CHARACTERS = ("[", "]", "(", ")", "{", "}", "?", "+", "!")


def validate_mask(mask: str):
    if mask == "":
        raise SyntaxError("Path mask must not be empty.")

    if not mask[0].isalnum() and mask[0] != "*":
        raise SyntaxError(
            "Path mask must start with an alphanumeric character or "
            "a wildcard symbol '*'."
        )

    if "//" in mask or "\\\\" in mask:
        raise SyntaxError("Path mask must not contain double slashes.")

    if "***" in mask:
        raise SyntaxError("Invalid wildcard: '***'.")

    for regex_symbol in MOST_COMMON_CHARACTERS:
        if regex_symbol in mask:
            raise SyntaxError(
                f"Path mask must not contain any of the special characters: "
                f"{MOST_COMMON_CHARACTERS}."
            )


def compile_regex_mask(path_mask: str) -> str:
    regex_mask = path_mask
    regex_mask = regex_mask.replace(".", "\\.")
    regex_mask = regex_mask.replace("**", "XXXX")
    regex_mask = regex_mask.replace("*", REGEX_WILDCARD)
    regex_mask = regex_mask.replace("XXXX", REGEX_DOUBLE_WILDCARD)
    # Support files like "file1.py" and "./file1.py"
    regex_mask = "^" + "(\\.\\/)?" + regex_mask + "$"  # noqa: ISC003
    return regex_mask


class PathFilter:
    def __init__(self, filtered_paths: List[str], positive_or_negative: bool):
        self.filtered_paths: List[str] = filtered_paths
        self.compiled_regex_masks: List[str] = []
        for filtered_path in filtered_paths:
            validate_mask(filtered_path)
            self.compiled_regex_masks.append(compile_regex_mask(filtered_path))
        self.positive_or_negative: bool = positive_or_negative

    def match(self, found_path: str) -> bool:
        # If this is an empty positive filter, we want to match everything
        # positively. If this is an empty negative filter, we want to match
        # everything negatively.
        if len(self.filtered_paths) == 0:
            return self.positive_or_negative

        portable_found_path = found_path.replace("\\", "/")
        for regex_mask in self.compiled_regex_masks:
            regex_match = re.match(regex_mask, portable_found_path)
            if regex_match is not None:
                return True

        return False
