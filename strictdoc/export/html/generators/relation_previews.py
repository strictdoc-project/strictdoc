"""
Relation previews for the DOCUMENT screen.

Hovering or focusing a Parent/Child relation link shows the linked node's
STATEMENT in a small card (see _static/relation_preview.js). When the linked
node is on the same page, the browser copies the STATEMENT from the page. For
the other cases, a document gets a "<name>-relation-previews.js" file next to
its HTML with the rendered STATEMENT of each node that a link on another page
can point to. The file is only loaded when such a link is hovered, so the
document pages themselves do not grow.

The static export writes the file, the server renders it on request.
"""

import os
from typing import Dict, Optional

import orjson
from markupsafe import Markup

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)

RELATION_PREVIEWS_SUFFIX = "-relation-previews.js"


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


def render_relation_previews_js(previews: Dict[str, Markup]) -> bytes:
    # The map is stored under the script's own URL, so that two documents
    # with the same file name in different folders do not overwrite each
    # other. relation_preview.js reads it back by the same URL.
    return (
        b"window.StrictDoc = window.StrictDoc || {};\n"
        b"window.StrictDoc.relationPreviews = "
        b"window.StrictDoc.relationPreviews || {};\n"
        b"window.StrictDoc.relationPreviews[document.currentScript.src] = "
        + orjson.dumps({key_: str(value_) for key_, value_ in previews.items()})
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
