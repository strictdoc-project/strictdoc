from typing import List, Optional, Tuple

from fixit import LintRule
from libcst import Comment, Module
from libcst.metadata import ParentNodeProvider, PositionProvider

RESERVED_STRINGS = [
    "fmt:",
    "http",
    "mypy:",
    "noqa",
    "pragma",
    "pylint",
    "@relation",
    "type:",
]


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


class StrictDoc_CheckCommentsRule(LintRule):
    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        PositionProvider,
    )

    def __init__(self) -> None:
        super().__init__()
        self.comments_so_far: List[Tuple[int, int, Comment]] = []

    def leave_Module(self, original_node: "Module") -> None:  # noqa: ARG002
        self.comments_so_far.sort(key=lambda x: x[0])

        current_line, current_column = -1, -1
        for comment_index_, (
            comment_line_,
            comment_column_,
            comment_,
        ) in enumerate(self.comments_so_far):
            if (
                comment_column_ != current_column
                or comment_line_ != (current_line + 1)
            ) and should_check_string(comment_.value):
                first_index = find_first_significant_char_index(comment_.value)
                if first_index is not None:
                    if comment_.value[first_index].islower():
                        patched_node_value = (
                            comment_.value[:first_index]
                            + comment_.value[first_index].upper()
                            + comment_.value[first_index + 1 :]
                        )
                        patched_comment = Comment(patched_node_value)
                        self.report(
                            comment_,
                            (
                                "The comments first sentence must start with "
                                "a capital letter."
                            ),
                            replacement=patched_comment,
                        )
                if comment_index_ > 0:
                    last_comment = self.comments_so_far[comment_index_ - 1][2]
                    self._patch_last_comment_sentence_if_needed(last_comment)

            current_column = comment_column_
            current_line = comment_line_

        if len(self.comments_so_far) > 0:
            self._patch_last_comment_sentence_if_needed(
                self.comments_so_far[-1][2]
            )

    def visit_Comment(self, node: "Comment") -> Optional[bool]:
        position = self.get_metadata(PositionProvider, node)
        line = position.start.line
        column = position.start.column
        self.comments_so_far.append((line, column, node))

    def _patch_last_comment_sentence_if_needed(self, comment: Comment):
        last_index = find_last_significant_char_index(comment.value)
        if last_index is not None and should_check_string(comment.value):
            if comment.value[last_index] != ".":
                patched_node_value = (
                    comment.value[:last_index]
                    + comment.value[last_index]
                    + "."
                    + comment.value[last_index + 1 :]
                )
                self.report(
                    comment,
                    ("The comment's last sentence must end with a dot."),
                    replacement=Comment(patched_node_value),
                )
