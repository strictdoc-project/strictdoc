"""
@relation(SDOC-SRS-214, scope=file)
"""

import json
import os

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.features.static_editing.edit_data import (
    build_document_edit_data,
)
from strictdoc.helpers.cast import assert_cast

STATIC_EDITING_DATA_FILE_SUFFIX = ".edit.json"


def get_static_editing_data_path(document: SDocDocument) -> str:
    """
    The static editing data file is placed next to the document's HTML file,
    so that the document page can load it with a relative URL.
    """
    document_meta: DocumentMeta = assert_cast(document.meta, DocumentMeta)
    output_document_path_base, _ = os.path.splitext(
        document_meta.output_document_full_path
    )
    return output_document_path_base + STATIC_EDITING_DATA_FILE_SUFFIX


def export_static_editing_data(
    traceability_index: TraceabilityIndex,
) -> None:
    for document_ in traceability_index.document_tree.document_list:
        if document_.document_is_included():
            continue

        document_edit_data = build_document_edit_data(
            document_, traceability_index
        )
        output_path = get_static_editing_data_path(document_)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf8") as output_file:
            json.dump(
                document_edit_data,
                output_file,
                ensure_ascii=False,
                indent=2,
            )
