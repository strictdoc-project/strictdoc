class ErrorMessage:
    @staticmethod
    def inline_link_uid_not_exist(uid):
        return (
            "error: DocumentIndex: "
            "the inline link references an "
            "object with an UID "
            "that does not exist: "
            f"{uid}."
        )
