import os
import re
from typing import List, Optional


def path_to_posix_path(path: str) -> str:
    return path.replace("\\", "/")


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


def calculate_document_root_assets_path(
    include_doc_paths: Optional[List[str]],
    doc_posix_path: str,
    file_tree_mount_folder: str,
) -> SDocRelativePath:
    """
    Calculates the Document Root Asset Directory based on include paths.

    @relation(SDOC-LLR-211, scope=function)
    """
    doc_root_rel_path = ""
    if include_doc_paths:
        longest_prefix = ""

        for include_path in include_doc_paths:
            # Get the static prefix
            match = re.search(r"[*?\[]", include_path)
            if match:
                static_part = include_path[: match.start()]
                static_prefix = os.path.dirname(static_part).rstrip("/")
            else:
                static_prefix = include_path.rstrip("/")

            clean_static_prefix = static_prefix.strip("/")

            # Check if the document falls under this prefix
            if clean_static_prefix == "":
                # Project root ("") is always a valid fallback match
                if len(longest_prefix) == 0:
                    longest_prefix = clean_static_prefix
            else:
                # Append slash to ensure precise folder matching
                prefix_with_slash = clean_static_prefix + "/"
                if (
                    doc_posix_path.startswith(prefix_with_slash)
                    or doc_posix_path == clean_static_prefix
                ):
                    # We keep the longest match
                    if len(clean_static_prefix) > len(longest_prefix):
                        longest_prefix = clean_static_prefix

        doc_root_rel_path = longest_prefix

    # Construct the final path
    if len(doc_root_rel_path) > 0:
        doc_root_assets_path = os.path.join(
            file_tree_mount_folder, doc_root_rel_path, "_assets"
        )
    else:
        doc_root_assets_path = "/".join((file_tree_mount_folder, "_assets"))

    return SDocRelativePath(doc_root_assets_path)
