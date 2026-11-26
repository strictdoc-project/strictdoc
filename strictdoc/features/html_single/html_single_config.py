"""
Configuration values of the single-file HTML export (html-single).

@relation(SDOC-SRS-217, scope=file)
"""

from typing import Dict, List, Optional

HTML_SINGLE_HANDLE = "html-single"

HTML_SINGLE_DEFAULT_CDN_URL = "https://cdn.jsdelivr.net/npm"


class HTMLSingleLibraryMode:
    # Embed a library only if the exported content uses it.
    AUTO = "auto"
    # Always embed a library.
    EMBED = "embed"
    # Load a library from a CDN when the file is opened.
    CDN = "cdn"

    ALL: List[str] = [AUTO, EMBED, CDN]


class HTMLSingleFontsMode:
    # Embed StrictDoc's Noto Sans fonts.
    EMBED = "embed"
    # Use the fonts installed on the reader's system.
    SYSTEM = "system"

    ALL: List[str] = [EMBED, SYSTEM]


HTML_SINGLE_LIBRARY_NAMES: List[str] = ["mathjax", "mermaid", "plantuml"]


def validate_html_single_config(
    *,
    libraries: str,
    library_modes: Optional[Dict[str, str]],
    fonts: str,
    cdn_url: str,
    include_source_files: bool,
) -> None:
    """
    Raise a ValueError with a user-facing message for an invalid option.
    """

    if libraries not in HTMLSingleLibraryMode.ALL:
        raise ValueError(
            "config: html_single_libraries: "
            f"must be one of {HTMLSingleLibraryMode.ALL}: '{libraries}'."
        )
    if library_modes is not None:
        if not isinstance(library_modes, dict):
            raise ValueError(
                "config: html_single_library_modes: "
                f"must be a dictionary: {library_modes}."
            )
        for library_, mode_ in library_modes.items():
            if library_ not in HTML_SINGLE_LIBRARY_NAMES:
                raise ValueError(
                    "config: html_single_library_modes: "
                    f"unknown library '{library_}'. "
                    f"Expected one of: {HTML_SINGLE_LIBRARY_NAMES}."
                )
            if mode_ not in HTMLSingleLibraryMode.ALL:
                raise ValueError(
                    "config: html_single_library_modes: "
                    f"'{library_}' must be one of "
                    f"{HTMLSingleLibraryMode.ALL}: '{mode_}'."
                )
    if fonts not in HTMLSingleFontsMode.ALL:
        raise ValueError(
            "config: html_single_fonts: "
            f"must be one of {HTMLSingleFontsMode.ALL}: '{fonts}'."
        )
    if not isinstance(cdn_url, str) or not cdn_url.startswith("https://"):
        raise ValueError(
            "config: html_single_cdn_url: "
            f"must be an https:// URL: '{cdn_url}'."
        )
    if not isinstance(include_source_files, bool):
        raise ValueError(
            "config: html_single_include_source_files: "
            f"must be a True/False value: {include_source_files}."
        )
