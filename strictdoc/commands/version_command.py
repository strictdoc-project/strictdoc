import strictdoc


class VersionCommand:
    @staticmethod
    def execute() -> None:
        print(strictdoc.__version__)  # noqa: T201
