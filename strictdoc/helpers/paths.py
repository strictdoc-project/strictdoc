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
    A relative path in two forms: native for the file system, POSIX for URLs.

    The native path uses the separator of the operating system: "/" on Linux
    and macOS, and a backslash on Windows. The POSIX path always uses "/".
    StrictDoc uses the POSIX path for the URLs of pages, for the links between
    pages, and for matching the include and exclude path filters.

    __str__() and __repr__() raise an AssertionError, so that each caller
    chooses one of the two forms explicitly. Otherwise, a native Windows path
    could end up in a URL.

    The class does not use pathlib, for two reasons:

    - Speed: creating a PurePath takes about 1.8 us, about 9 times as long as
      creating this class. Appending a name with the "/" operator of pathlib
      takes about 1.2 us, and a string concatenation about 50 ns. An export
      without changes of the StrictDoc repository creates about 4,600
      relative paths, most of them in FileFinder.
    - Exact strings: pathlib normalizes paths, but StrictDoc depends on the
      exact strings. FileFinder stores the path of a folder with a trailing
      "/", for example "src/", so that it can append a file name and match
      the path filters without a join. PurePath("src/") drops the trailing
      "/". The relative path of the root folder is "", but PurePath("") is
      ".".
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
