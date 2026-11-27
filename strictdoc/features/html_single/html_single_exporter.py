"""
The single-file HTML export (html-single).

The exporter packs the files of the HTML export into one HTML file. The file
contains every exported file as gzip-compressed, base64-encoded data and a
loader script. When a reader opens the file, the loader shows each exported
page in an iframe and resolves the links between pages and assets inside the
file.

@relation(SDOC-SRS-217, scope=file)
"""

import base64
import gzip
import html
import json
import mimetypes
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import orjson

from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.html_single.html_single_config import (
    HTMLSingleFontsMode,
    HTMLSingleLibraryMode,
)
from strictdoc.features.html_single.html_single_libraries import (
    HTML_SINGLE_LIBRARIES,
    HTMLSingleLibrary,
)
from strictdoc.helpers.file_system import (
    file_open_read_bytes,
    file_open_read_utf8,
)
from strictdoc.helpers.string import create_safe_document_file_name

HTML_SINGLE_LOADER_FILE_NAME = "html_single_loader.js"
HTML_SINGLE_OUTPUT_FOLDER = "html-single"
HTML_SINGLE_START_PAGE = "index.html"

# The HTML export writes the pages of the requirements-to-source
# traceability to this folder.
SOURCE_FILES_FOLDER = "_source_files/"

# The static editing feature writes each document's edit data twice. The
# HTML page loads the .edit.js file. The .edit.json file is for tools.
STATIC_EDITING_DATA_SUFFIX = ".edit.json"

CHUNK_FILE_PATTERN = re.compile(r"-chunk-\d+\.js$")
CHUNK_PAYLOAD_PATTERN = re.compile(
    rb"window\.StrictDoc\.chunks\[[^\]]*\] = (.*);\s*$", re.DOTALL
)
FONT_FACE_RULE_PATTERN = re.compile(r"@font-face\s*\{[^}]*\}")

MIME_TYPES_BY_EXTENSION: Dict[str, str] = {
    ".css": "text/css",
    ".html": "text/html",
    ".ico": "image/x-icon",
    ".js": "text/javascript",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".ttf": "font/ttf",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}

SHELL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="StrictDoc (html-single)">
<title>{title}</title>
<style>
html, body {{ margin: 0; height: 100%; overflow: hidden; }}
iframe.strictdoc-html-single-frame {{
  display: block; width: 100%; height: 100%; border: 0;
}}
</style>
</head>
<body>
<noscript>This document requires JavaScript.</noscript>
<script type="application/json" id="strictdoc-html-single-data">{data}</script>
<script>{loader}</script>
</body>
</html>
"""


@dataclass
class HTMLSingleExportResult:
    output_path: str
    file_count: int
    embedded_libraries: List[str] = field(default_factory=list)
    cdn_libraries: List[str] = field(default_factory=list)
    stubbed_libraries: List[str] = field(default_factory=list)


def export_html_single(project_config: ProjectConfig) -> HTMLSingleExportResult:
    """
    Pack the HTML export of the project into one HTML file.
    """

    html_root = project_config.export_output_html_root
    static_folder = project_config.dir_for_sdoc_assets.strip("/") + "/"

    file_paths = _collect_file_paths(project_config, html_root, static_folder)

    manifest_scripts: Dict[str, Dict[str, Optional[str]]] = {}
    excluded_prefixes: List[str] = []
    result = HTMLSingleExportResult(output_path="", file_count=0)

    used_libraries = find_used_libraries(html_root, file_paths)
    for library_ in HTML_SINGLE_LIBRARIES:
        mode = project_config.get_html_single_library_mode(library_.name)
        if mode == HTMLSingleLibraryMode.EMBED or (
            mode == HTMLSingleLibraryMode.AUTO
            and library_.name in used_libraries
        ):
            result.embedded_libraries.append(library_.name)
            continue

        excluded_prefixes.extend(
            static_folder + static_path_
            for static_path_ in library_.static_paths
        )
        if mode == HTMLSingleLibraryMode.CDN:
            result.cdn_libraries.append(library_.name)
        else:
            result.stubbed_libraries.append(library_.name)
        manifest_scripts.update(
            _create_script_entries(
                project_config, library_, static_folder, mode
            )
        )

    if project_config.html_single_fonts == HTMLSingleFontsMode.SYSTEM:
        excluded_prefixes.append(static_folder + "fonts/")

    files: Dict[str, List[str]] = {}
    for file_path_ in file_paths:
        if any(file_path_.startswith(prefix_) for prefix_ in excluded_prefixes):
            continue
        content = _read_file(html_root, file_path_)
        if (
            project_config.html_single_fonts == HTMLSingleFontsMode.SYSTEM
            and file_path_.startswith(static_folder)
            and file_path_.endswith(".css")
        ):
            content = remove_font_faces(content)
        files[file_path_] = [
            _get_mime_type(file_path_),
            base64.b64encode(
                gzip.compress(content, compresslevel=9, mtime=0)
            ).decode("ascii"),
        ]

    mathjax_fonts_folder: Optional[str] = None
    if "mathjax" in result.embedded_libraries:
        mathjax_fonts_folder = (
            static_folder + "mathjax/output/chtml/fonts/woff-v2/"
        )

    manifest = {
        "version": 1,
        "start": HTML_SINGLE_START_PAGE,
        "static_folder": static_folder,
        "project_map": static_folder + "project_map.js",
        "mathjax_fonts_folder": mathjax_fonts_folder,
        "scripts": manifest_scripts,
        "files": files,
    }

    loader_path = os.path.join(
        html_root, static_folder, HTML_SINGLE_LOADER_FILE_NAME
    )
    with file_open_read_utf8(loader_path) as loader_file:
        loader = loader_file.read()

    shell = SHELL_TEMPLATE.format(
        title=html.escape(project_config.project_title),
        data=_serialize_for_script(manifest),
        loader=loader,
    )

    output_folder = os.path.join(
        project_config.output_dir, HTML_SINGLE_OUTPUT_FOLDER
    )
    os.makedirs(output_folder, exist_ok=True)
    output_file_name = create_safe_document_file_name(
        project_config.project_title
    )
    if len(output_file_name) == 0:
        output_file_name = "index"
    output_path = os.path.join(output_folder, output_file_name + ".html")
    with open(output_path, "w", encoding="utf8") as output_file:
        output_file.write(shell)

    result.output_path = output_path
    result.file_count = len(files)

    size_in_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(  # noqa: T201
        "Single-file HTML export: libraries:\n"
        f"  embedded: {_format_names(result.embedded_libraries)}\n"
        f"  loaded from CDN: {_format_names(result.cdn_libraries)}\n"
        f"  left out: {_format_names(result.stubbed_libraries)}\n"
        f"Single-file HTML export: fonts: {project_config.html_single_fonts}\n"
        "Single-file HTML export completed "
        f"({result.file_count} files, {size_in_mb:.1f} MB):\n"
        f"{output_path}"
    )
    return result


def find_used_libraries(html_root: str, file_paths: List[str]) -> List[str]:
    """
    Find the libraries whose markup appears in the exported pages, including
    the lazily loaded chunks of large documents.
    """

    used_libraries: List[str] = []
    remaining_libraries = list(HTML_SINGLE_LIBRARIES)
    for file_path_ in file_paths:
        if len(remaining_libraries) == 0:
            break
        page_content: Optional[str] = None
        if file_path_.endswith(".html"):
            page_content = _read_file(html_root, file_path_).decode(
                "utf-8", errors="replace"
            )
        elif CHUNK_FILE_PATTERN.search(file_path_) is not None:
            page_content = read_chunk_html(_read_file(html_root, file_path_))
        if page_content is None:
            continue
        for library_ in list(remaining_libraries):
            if library_.content_marker.search(page_content) is not None:
                used_libraries.append(library_.name)
                remaining_libraries.remove(library_)
    return used_libraries


def read_chunk_html(chunk_content: bytes) -> Optional[str]:
    match = CHUNK_PAYLOAD_PATTERN.search(chunk_content)
    if match is None:
        return None
    payload = orjson.loads(match.group(1))
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict) and "z" in payload:
        return gzip.decompress(base64.b64decode(payload["z"])).decode(
            "utf-8", errors="replace"
        )
    return None


def remove_font_faces(css_content: bytes) -> bytes:
    css = css_content.decode("utf-8")

    def remove_if_font_file(match: re.Match[str]) -> str:
        if "fonts/" in match.group(0):
            return ""
        return match.group(0)

    return FONT_FACE_RULE_PATTERN.sub(remove_if_font_file, css).encode("utf-8")


def _collect_file_paths(
    project_config: ProjectConfig, html_root: str, static_folder: str
) -> List[str]:
    file_paths: List[str] = []
    for folder_, _, file_names_ in os.walk(html_root):
        for file_name_ in file_names_:
            file_path = os.path.relpath(
                os.path.join(folder_, file_name_), html_root
            ).replace(os.sep, "/")
            if file_path == static_folder + HTML_SINGLE_LOADER_FILE_NAME:
                continue
            if file_path.endswith(STATIC_EDITING_DATA_SUFFIX):
                continue
            if (
                file_path.startswith(SOURCE_FILES_FOLDER)
                and not project_config.html_single_include_source_files
            ):
                continue
            file_paths.append(file_path)
    return sorted(file_paths)


def _create_script_entries(
    project_config: ProjectConfig,
    library: HTMLSingleLibrary,
    static_folder: str,
    mode: str,
) -> Dict[str, Dict[str, Optional[str]]]:
    entries: Dict[str, Dict[str, Optional[str]]] = {}
    for script_ in library.scripts:
        if mode == HTMLSingleLibraryMode.CDN:
            entries[static_folder + script_.static_path] = {
                "library": library.name,
                "action": "cdn",
                "url": project_config.html_single_cdn_url
                + "/"
                + script_.cdn_path,
                "integrity": script_.cdn_integrity,
                "module_global": script_.module_global,
            }
        else:
            entries[static_folder + script_.static_path] = {
                "library": library.name,
                "action": "stub",
                "url": None,
                "integrity": None,
                "module_global": script_.module_global,
            }
    return entries


def _read_file(html_root: str, file_path: str) -> bytes:
    with file_open_read_bytes(
        os.path.join(html_root, *file_path.split("/"))
    ) as file_:
        return file_.read()


def _format_names(names: List[str]) -> str:
    if len(names) == 0:
        return "-"
    return ", ".join(names)


def _get_mime_type(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()
    mime_type = MIME_TYPES_BY_EXTENSION.get(extension)
    if mime_type is not None:
        return mime_type
    guessed_type, _ = mimetypes.guess_type(file_path)
    if guessed_type is not None:
        return guessed_type
    return "application/octet-stream"


def _serialize_for_script(data: Dict[str, object]) -> str:
    # The JSON is embedded in a <script> element. Escaping "<" prevents a
    # file path from closing the element.
    return json.dumps(data, separators=(",", ":")).replace("<", "\\u003c")
