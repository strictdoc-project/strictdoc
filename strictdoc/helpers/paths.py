# mypy: disable-error-code="no-untyped-def"
import os


class SDocRelativePath:
    """
    This rel path will be used for lookups of URL pages that are
    always "/"-based, even on Windows.
    """

    def __init__(self, relative_path: str):
        assert isinstance(relative_path, str), relative_path
        self.relative_path = relative_path
        self.relative_path_posix = relative_path.replace("\\", "/")

    @staticmethod
    def from_url(url: str):
        return SDocRelativePath(os.path.normpath(url).replace("/", os.sep))

    def length(self) -> int:
        return len(self.relative_path)

    def __str__(self):
        raise AssertionError("Must not be used")

    def __repr__(self):
        raise AssertionError("Must not be used")
