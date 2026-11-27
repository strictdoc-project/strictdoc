"""
@relation(SDOC-SRS-217, scope=file)
"""

import base64
import gzip
import hashlib
import os
from typing import Any, Dict, Optional

import pytest

from strictdoc.core.environment import HTML_STATIC_DIRS
from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.html_single.html_single_config import (
    validate_html_single_config,
)
from strictdoc.features.html_single.html_single_exporter import (
    read_chunk_html,
    remove_font_faces,
)
from strictdoc.features.html_single.html_single_libraries import (
    HTML_SINGLE_LIBRARIES,
    HTMLSingleLibrary,
)

PATH_TO_STRICTDOC_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)


def _find_vendored_file(static_path: str) -> Optional[str]:
    for static_dir_ in HTML_STATIC_DIRS:
        path = os.path.join(PATH_TO_STRICTDOC_ROOT, static_dir_, static_path)
        if os.path.isfile(path):
            return path
    return None


def _get_library(name: str) -> HTMLSingleLibrary:
    return next(
        library_ for library_ in HTML_SINGLE_LIBRARIES if library_.name == name
    )


def test_cdn_integrity_matches_vendored_libraries() -> None:
    # The CDN must serve the same version as the multi-file export. A module
    # (PlantUML) is re-bundled for StrictDoc and differs from the CDN file.
    for library_ in HTML_SINGLE_LIBRARIES:
        for script_ in library_.scripts:
            vendored_path = _find_vendored_file(script_.static_path)
            assert vendored_path is not None, script_.static_path
            if script_.module_global is not None:
                continue
            with open(vendored_path, "rb") as vendored_file:
                digest = hashlib.sha384(vendored_file.read()).digest()
            integrity = "sha384-" + base64.b64encode(digest).decode("ascii")
            assert script_.cdn_integrity == integrity, script_.static_path


@pytest.mark.parametrize(
    "library_name,html,expected_match",
    [
        ("mermaid", '<pre class="mermaid">graph TD</pre>', True),
        ("mermaid", '<div class="content mermaid">x</div>', True),
        ("mermaid", '<p class="mermaid-like">x</p>', False),
        ("mermaid", "<p>mermaid</p>", False),
        ("plantuml", '<pre class="plantuml">@startuml</pre>', True),
        ("plantuml", "<p>PlantUML</p>", False),
        ("mathjax", '<span class="math notranslate">a^2</span>', True),
        ("mathjax", "<p>Inline \\(a^2\\) math.</p>", True),
        ("mathjax", "<p>$$a^2$$</p>", True),
        ("mathjax", '<p class="mathematics">x</p>', False),
    ],
)
def test_content_markers(
    library_name: str, html: str, expected_match: bool
) -> None:
    library = _get_library(library_name)
    assert (library.content_marker.search(html) is not None) == expected_match


def test_read_chunk_html_from_compressed_and_plain_chunks() -> None:
    chunk_html = '<turbo-frame id="document-chunk-1">Text</turbo-frame>'
    compressed = base64.b64encode(
        gzip.compress(chunk_html.encode("utf-8"), mtime=0)
    ).decode("ascii")
    compressed_chunk = (
        b"window.StrictDoc = window.StrictDoc || {};\n"
        b'window.StrictDoc.chunks["doc-chunk-1"] = {"z":"'
        + compressed.encode("ascii")
        + b'"};\n'
    )
    plain_chunk = (
        b'window.StrictDoc.chunks["doc-chunk-1"] = '
        b'"<turbo-frame id=\\"document-chunk-1\\">Text</turbo-frame>";\n'
    )

    assert read_chunk_html(compressed_chunk) == chunk_html
    assert read_chunk_html(plain_chunk) == chunk_html
    assert read_chunk_html(b"console.log(1);") is None


def test_remove_font_faces_keeps_other_rules() -> None:
    css = (
        "@font-face { font-family: 'Noto Sans'; "
        "src: url('./fonts/NotoSans.ttf'); }\n"
        "@font-face { font-family: 'Other'; src: url('other.woff'); }\n"
        "body { font-family: 'Noto Sans', sans-serif; }\n"
    )

    result = remove_font_faces(css.encode("utf-8")).decode("utf-8")

    assert "NotoSans.ttf" not in result
    assert "other.woff" in result
    assert "body { font-family: 'Noto Sans', sans-serif; }" in result


def test_library_mode_falls_back_to_the_mode_of_all_libraries() -> None:
    project_config = ProjectConfig(
        html_single_libraries="cdn",
        html_single_library_modes={"plantuml": "embed"},
    )

    assert project_config.get_html_single_library_mode("plantuml") == "embed"
    assert project_config.get_html_single_library_mode("mermaid") == "cdn"


@pytest.mark.parametrize(
    "options,message",
    [
        ({"libraries": "sometimes"}, "config: html_single_libraries:"),
        (
            {"library_modes": {"graphviz": "cdn"}},
            "unknown library 'graphviz'",
        ),
        (
            {"library_modes": {"mermaid": "sometimes"}},
            "'mermaid' must be one of",
        ),
        ({"fonts": "cdn"}, "config: html_single_fonts:"),
        (
            {"cdn_url": "http://cdn.example.com"},
            "config: html_single_cdn_url:",
        ),
    ],
)
def test_invalid_options_raise_value_errors(
    options: Dict[str, Any],
    message: str,
) -> None:
    arguments: Dict[str, Any] = {
        "libraries": "auto",
        "library_modes": None,
        "fonts": "embed",
        "cdn_url": "https://cdn.jsdelivr.net/npm",
        "include_source_files": False,
    }
    arguments.update(options)

    with pytest.raises(ValueError, match=message):
        validate_html_single_config(**arguments)
