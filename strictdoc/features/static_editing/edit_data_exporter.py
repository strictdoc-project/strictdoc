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
    compute_next_uid_numbers,
)
from strictdoc.helpers.cast import assert_cast

STATIC_EDITING_DATA_FILE_SUFFIX = ".edit.json"
STATIC_EDITING_SCRIPT_FILE_SUFFIX = ".edit.js"
STATIC_EDITING_SCRIPT_GLOBAL = "StrictDocStaticEditingData"


def get_static_editing_data_path(document: SDocDocument) -> str:
    """
    The static editing data file is placed next to the document's HTML file,
    so that the document page can load it with a relative URL.
    """
    return _get_output_path_base(document) + STATIC_EDITING_DATA_FILE_SUFFIX


def get_static_editing_script_path(document: SDocDocument) -> str:
    """
    The script file contains the same data as the data file. The document
    page loads the script with a <script> tag because a browser blocks
    fetch() between file:// URLs.
    """
    return _get_output_path_base(document) + STATIC_EDITING_SCRIPT_FILE_SUFFIX


def export_static_editing_data(
    traceability_index: TraceabilityIndex,
) -> None:
    # The next free UID numbers are counted over all documents.
    next_uid_numbers = compute_next_uid_numbers(traceability_index)
    for document_ in traceability_index.document_tree.document_list:
        if document_.document_is_included():
            continue

        document_edit_data = build_document_edit_data(
            document_, traceability_index, next_uid_numbers
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

        serialized_data = json.dumps(
            document_edit_data, ensure_ascii=False, separators=(",", ":")
        )
        with open(
            get_static_editing_script_path(document_), "w", encoding="utf8"
        ) as output_file:
            output_file.write(
                f"window.{STATIC_EDITING_SCRIPT_GLOBAL} = {serialized_data};\n"
            )


def _get_output_path_base(document: SDocDocument) -> str:
    document_meta: DocumentMeta = assert_cast(document.meta, DocumentMeta)
    output_document_path_base, _ = os.path.splitext(
        document_meta.output_document_full_path
    )
    return output_document_path_base
