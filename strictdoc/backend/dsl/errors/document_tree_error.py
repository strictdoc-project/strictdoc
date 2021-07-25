class DocumentTreeError(Exception):
    def __init__(self, title, message):
        self.title = title
        self.message = message

    @staticmethod
    def cycle_error(problem_uid, requirement, cycled_uids):
        return DocumentTreeError(
            (
                "a cycle detected: requirements in the document tree must not "
                "reference each other."
            ),
            (
                f"problematic UID: {problem_uid}\n"
                f"requirement: {requirement}\n"
                f"Cycle: {', '.join(cycled_uids)}"
            ),
        )

    def to_print_message(self):
        message = f"error: document tree: {self.title}\n" f"{self.message}\n"
        return message
