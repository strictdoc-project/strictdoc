"""
Relation previews for the DOCUMENT and TRACE screens.

Hovering or focusing a relation link shows a small card (see
_static/relation_preview.js). For a link to a node, the card shows the linked
node's STATEMENT. When the linked node is on the same page, the browser copies
the STATEMENT from the page. For the other cases, a document gets a
"<name>-relation-previews.js" file next to its HTML with the rendered
STATEMENT of each node that a link on another page can point to.

For a File relation link, the card shows the first lines of the linked range.
Each source file page "_source_files/<path>.html" gets a
"<path>-relation-previews.js" file with the highlighted lines that start each
range of that file, at most SOURCE_PREVIEW_MAX_LINES per range.

The files are only loaded when such a link is hovered, so the pages
themselves do not grow. The static export writes the files, the server
renders them on request.
"""

import os
from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Sequence

import orjson
from markupsafe import Markup

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)

if TYPE_CHECKING:
    from strictdoc.backend.sdoc_source_code.models.source_file_info import (
        SourceFileTraceabilityInfo,
    )
    from strictdoc.core.file_system.source_tree import SourceFile
    from strictdoc.features.source_file_view.view_object import (
        SourceLineEntry,
    )

RELATION_PREVIEWS_SUFFIX = "-relation-previews.js"
SOURCE_PREVIEW_MAX_LINES = 15


def relation_previews_file_name(document: SDocDocument) -> str:
    assert document.meta is not None
    return f"{document.meta.document_filename_base}{RELATION_PREVIEWS_SUFFIX}"


def document_url_for_relation_previews(previews_url: str) -> Optional[str]:
    """
    Map "folder/doc-relation-previews.js" to "folder/doc.html", the URL of
    the document the previews belong to.
    """
    if not previews_url.endswith(RELATION_PREVIEWS_SUFFIX):
        return None
    return previews_url[: -len(RELATION_PREVIEWS_SUFFIX)] + ".html"


def collect_relation_previews(
    view_object: DocumentScreenViewObject,
) -> Dict[str, Markup]:
    """
    Rendered STATEMENT per node anchor, for the nodes of this document that a
    relation link on another page can point to.

    A node whose related nodes are all on this same page is left out: the
    browser reads it from the page. In a chunked document, any node may sit
    in a chunk that has not loaded yet, so every node with a relation is kept.
    """
    traceability_index = view_object.traceability_index
    is_chunked = view_object.is_chunked_rendering()

    previews: Dict[str, Markup] = {}
    for node_, _ in view_object.document_content_iterator():
        if (
            not isinstance(node_, SDocNode)
            or not node_.has_reserved_statement()
        ):
            continue

        related_nodes = traceability_index.get_parent_requirements(
            node_
        ) + traceability_index.get_children_requirements(node_)
        if len(related_nodes) == 0:
            continue

        if not is_chunked:
            page_document = node_.get_parent_or_including_document()
            if all(
                related_node_.get_parent_or_including_document()
                is page_document
                for related_node_ in related_nodes
            ):
                continue

        previews[view_object.render_local_anchor(node_)] = (
            view_object.render_node_statement(node_)
        )
    return previews


def collect_source_relation_previews(
    pygmented_lines: Sequence["SourceLineEntry"],
    trace_info: "SourceFileTraceabilityInfo",
) -> Dict[str, List[str]]:
    """
    Highlighted lines per first line number of each range in a source file,
    up to the range end and at most SOURCE_PREVIEW_MAX_LINES of them. Ranges
    that start on the same line share the entry of the longest one. The
    browser cuts the list at the end of the hovered range and marks a longer
    range as truncated.
    """
    previews: Dict[str, List[str]] = {}
    for marker_ in trace_info.markers:
        begin = marker_.ng_range_line_begin
        end = marker_.ng_range_line_end
        if begin is None or end is None:
            continue
        if not 1 <= begin <= len(pygmented_lines):
            continue
        key = str(begin)
        length = min(max(end - begin + 1, 1), SOURCE_PREVIEW_MAX_LINES)
        if key in previews and len(previews[key]) >= length:
            continue
        previews[key] = [
            str(getattr(line_, "source_line", line_))
            for line_ in pygmented_lines[begin - 1 : begin - 1 + length]
        ]
    return previews


def source_relation_previews_file_path(source_file: "SourceFile") -> str:
    output_file = source_file.output_file_full_path
    assert output_file.endswith(".html"), output_file
    return output_file[: -len(".html")] + RELATION_PREVIEWS_SUFFIX


def render_relation_previews_js(previews: Mapping[str, object]) -> bytes:
    # The map is stored under the script's own URL, so that two documents
    # with the same file name in different folders do not overwrite each
    # other. relation_preview.js reads it back by the same URL.
    return (
        b"window.StrictDoc = window.StrictDoc || {};\n"
        b"window.StrictDoc.relationPreviews = "
        b"window.StrictDoc.relationPreviews || {};\n"
        b"window.StrictDoc.relationPreviews[document.currentScript.src] = "
        + orjson.dumps(previews)
        + b";\n"
    )


def export_relation_previews(view_object: DocumentScreenViewObject) -> None:
    previews = collect_relation_previews(view_object)
    if len(previews) == 0:
        return

    document = view_object.document
    assert document.meta is not None
    output_file = os.path.join(
        document.meta.output_document_dir_full_path,
        relation_previews_file_name(document),
    )
    with open(output_file, "wb") as file:
        file.write(render_relation_previews_js(previews))
