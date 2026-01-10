import re
from typing import List

REGEX_NAME_PART = r"[A-Za-z0-9-_\. ]*"
REGEX_FILENAME = rf"{REGEX_NAME_PART}"
REGEX_FOLDER = rf"{REGEX_NAME_PART}"

REGEX_WILDCARD = REGEX_FILENAME
# FIXME: This does the job but most probably could be simplified.
REGEX_DOUBLE_WILDCARD = (
    rf"(\\|\/)?({REGEX_NAME_PART})?((\\|\/){REGEX_NAME_PART})*(\\|\/)?"
)

REGEX_MASK_VALIDATION = rf"[^(\\|\/)]{REGEX_DOUBLE_WILDCARD}"

DISALLOWED_CHARACTERS = ("..", "{", "}", "?", "+", "!")

# "~"" comes from Windows.
ALLOWED_FIRST_CHARACTERS = ("*", "/", ".", "_", "~")


def validate_mask(mask: str) -> None:
    if mask == "":
        raise SyntaxError("Path mask must not be empty.")

    if not mask[0].isalnum() and mask[0] not in ALLOWED_FIRST_CHARACTERS:
        raise SyntaxError(
            "Path mask must start with an alphanumeric character or one of "
            f"these characters: {ALLOWED_FIRST_CHARACTERS}. Provided mask: '{mask}'."
        )

    if "//" in mask or "\\\\" in mask:
        raise SyntaxError("Path mask must not contain double slashes.")

    if "***" in mask:
        raise SyntaxError("Invalid wildcard: '***'.")

    for regex_symbol in DISALLOWED_CHARACTERS:
        if regex_symbol in mask:
            raise SyntaxError(
                f"Path mask must not contain any of the special characters: "
                f"{DISALLOWED_CHARACTERS}."
            )


def compile_regex_mask(path_mask: str) -> str:
    regex_mask = path_mask
    # $ can happen on Windows paths, escape it to not be mixed with $-endings.
    regex_mask = regex_mask.replace("$", r"\$")
    regex_mask = regex_mask.replace(".", "\\.")
    regex_mask = regex_mask.replace("**", "XXXX")
    regex_mask = regex_mask.replace("*", REGEX_WILDCARD)
    regex_mask = regex_mask.replace("XXXX", REGEX_DOUBLE_WILDCARD)
    regex_mask = "^" + regex_mask + "$"  # noqa: ISC003
    return regex_mask


class PathFilter:
    def __init__(
        self, filtered_paths: List[str], positive_or_negative: bool
    ) -> None:
        self.filtered_paths: List[str] = filtered_paths
        self.positive_or_negative: bool = positive_or_negative

        compiled_masks: List[re.Pattern[str]] = []
        for filtered_path_ in filtered_paths:
            filtered_path = filtered_path_

            validate_mask(filtered_path)

            filtered_path = filtered_path.replace("(", r"\(")
            filtered_path = filtered_path.replace(")", r"\)")

            if filtered_path.startswith("/"):
                filtered_path = filtered_path.lstrip("/")
            else:
                if not filtered_path.startswith("**"):
                    filtered_path = "(**/)?" + filtered_path

            if filtered_path.endswith("/"):
                filtered_path += "**"
            else:
                if not filtered_path.endswith("*"):
                    filtered_path += "(/**)?"

            regex = compile_regex_mask(filtered_path)
            compiled_masks.append(re.compile(regex))

        self.compiled_masks: List[re.Pattern[str]] = compiled_masks

    def match(self, found_path: str) -> bool:
        # If this is an empty positive filter, we want to match everything
        # positively. If this is an empty negative filter, we want to match
        # everything negatively.
        if len(self.filtered_paths) == 0:
            return self.positive_or_negative

        for rx in self.compiled_masks:
            if rx.match(found_path):
                return True

        return False

    def dump(self) -> str:
        return "\n".join(
            str(m_).replace("\\\\", "\\") for m_ in self.compiled_masks
        )
