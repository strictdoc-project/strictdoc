# mypy: disable-error-code="no-untyped-def"
import strictdoc


class VersionCommand:
    @staticmethod
    def execute():
        print(strictdoc.__version__)  # noqa: T201
