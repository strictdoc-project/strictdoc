import os


def path_to_posix_path(path: str) -> str:
    return path.replace("\\", "/")


def shorten_path(path: str) -> str:
    """
    Collapse a deep relative path down to its first and last segments, e.g.
    "tests/integration/features/.../file.py" -> "tests/.../file.py", so that
    progress lines stay readable instead of being dominated by long paths.
    """
    parts = path_to_posix_path(path).split("/")
    if len(parts) <= 5:
        return path
    return f"{parts[0]}/.../{parts[-1]}"


class SDocRelativePath:
    """
    Class to encapsulate a path as both a native OS path and a POSIX path.

    A native OS path can be with forward slashes on Linux and macOS and with
    backward slashes on Windows. The POSIX path is always with forward slashes.

    This rel path will be used for lookups of URL pages that are
    always "/"-based, even on Windows.
    """

    def __init__(self, relative_path: str) -> None:
        assert isinstance(relative_path, str), relative_path
        self.relative_path: str = relative_path
        self.relative_path_posix: str = path_to_posix_path(relative_path)

    @staticmethod
    def from_url(url: str) -> "SDocRelativePath":
        return SDocRelativePath(os.path.normpath(url).replace("/", os.sep))

    def length(self) -> int:
        return len(self.relative_path)

    def __str__(self) -> str:
        raise AssertionError("Must not be used")

    def __repr__(self) -> str:
        raise AssertionError("Must not be used")
