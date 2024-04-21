# mypy: disable-error-code="no-untyped-call,no-untyped-def"
class DocumentTreeError(Exception):
    def __init__(self, problem_uid, cycled_uids):
        super().__init__()
        self.problem_uid = problem_uid
        self.cycled_uids = cycled_uids

    @staticmethod
    def cycle_error(problem_uid, cycled_uids):
        return DocumentTreeError(problem_uid, cycled_uids)

    def to_print_message(self):
        cycled_uids = ", ".join(self.cycled_uids)
        message = (
            "error: document tree: "
            "a cycle detected: requirements in the document tree must not "
            "reference each other.\n"
            f"Problematic UID: {self.problem_uid}.\nCycle: {cycled_uids}.\n"
        )
        return message

    def to_validation_message(self):
        return (
            "A cycle detected: requirements in the document tree must not "
            "reference each other. "
            f"Problematic UID: {self.problem_uid}, cycle: {self.cycled_uids}."
        )
