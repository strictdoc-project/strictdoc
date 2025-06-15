from typing import Optional

from fixit import LintRule
from libcst import Expr, SimpleString
from libcst.metadata import ParentNodeProvider, PositionProvider

RESERVED_STRINGS = ["@relation", "FIXME", "http"]


def find_first_significant_char_index(text: str) -> Optional[int]:
    for i, char in enumerate(text):
        if char not in {'"', " ", "\t", "#", "\n"}:
            return i
    return None


def should_check_string(string: str) -> bool:
    return not any(rs in string for rs in RESERVED_STRINGS)


def find_last_significant_char_index(text: str) -> Optional[int]:
    for i in range(len(text) - 1, -1, -1):
        if text[i] not in {'"', " ", "\t", "#", "\n"}:
            return i
    return None


class StrictDoc_CheckDocStringsRule(LintRule):
    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        PositionProvider,
    )

    def visit_SimpleString(self, node: "SimpleString") -> Optional[bool]:
        parent = self.get_metadata(ParentNodeProvider, node)

        if isinstance(parent, Expr):
            node_strings = node.value.splitlines(keepends=False)
            if len(node_strings) == 0:
                return True

            assert node_strings[0].startswith('"""')

            position = self.get_metadata(PositionProvider, node)
            column = position.start.column

            if node_strings[0] != '"""':
                node_strings[0] = " " * column + node_strings[0][3:]
                node_strings.insert(0, '"""')

            if node_strings[-1].strip(" ") != '"""':
                node_strings[-1] = node_strings[-1][:-3]
                node_strings.append(" " * column + '"""')

            if (
                node_strings[2].strip() not in ('"""', "")
                and "FIXME" not in node_strings[1]
            ):
                self.report(
                    node,
                    "The first line of a docstring must be separated "
                    "with an empty line from the rest of the docstring comment.",
                )
                return True

            if (should_check_string(node_strings[1])) and not node_strings[
                1
            ].endswith("."):
                node_strings[1] += "."

            first_index = find_first_significant_char_index(node_strings[0])
            if first_index is not None:
                if node.value[first_index].islower():
                    node_strings[0] = (
                        node_strings[0][:first_index]
                        + node_strings[0][first_index].upper()
                        + node_strings[0][first_index + 1 :]
                    )

            if len(node_strings) > 3 and should_check_string(node_strings[-2]):
                last_index = find_last_significant_char_index(node_strings[-2])
                if last_index is not None:
                    if node_strings[-2].rstrip()[last_index] not in (
                        ".",
                        ")",
                        "]",
                    ):
                        node_strings[-2] = (
                            node_strings[-2][:last_index]
                            + node_strings[-2][last_index]
                            + "."
                            + node_strings[-2][last_index + 1 :]
                        )

            patched_value = "\n".join(node_strings)

            if patched_value != node.value:
                self.report(
                    node,
                    (
                        "The docstring comment's first sentence must start with "
                        "a capital letter and end with a dot. Additionally, "
                        "and extended comment that follows the first line must "
                        "be separated from the first sentence with an empty line. "
                        "The last sentence must end with a dot."
                    ),
                    replacement=SimpleString(patched_value),
                )

        return True
