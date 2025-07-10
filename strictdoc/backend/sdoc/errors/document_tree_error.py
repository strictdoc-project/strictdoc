"""
@relation(SDOC-SRS-30, scope=file)
"""

from typing import List


class DocumentTreeError(Exception):
    def __init__(self, problem_uid: str, cycled_uids: List[str]) -> None:
        super().__init__()
        self.problem_uid: str = problem_uid
        self.cycled_uids: List[str] = cycled_uids

    @staticmethod
    def cycle_error(
        problem_uid: str, cycled_uids: List[str]
    ) -> "DocumentTreeError":
        return DocumentTreeError(problem_uid, cycled_uids)

    def to_print_message(self) -> str:
        cycled_uids = ", ".join(self.cycled_uids)
        message = (
            "error: document tree: "
            "a cycle detected: requirements in the document tree must not "
            "reference each other.\n"
            f"Problematic UID: {self.problem_uid}.\nCycle: {cycled_uids}.\n"
        )
        return message

    def to_validation_message(self) -> str:
        return (
            "A cycle detected: requirements in the document tree must not "
            "reference each other. "
            f"Problematic UID: {self.problem_uid}, cycle: {self.cycled_uids}."
        )
