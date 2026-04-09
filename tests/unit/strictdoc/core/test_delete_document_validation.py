"""
@relation(SDOC-SRS-28, scope=file)
"""

from types import SimpleNamespace

import pytest

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.core.transforms.validation_error import (
    MultipleValidationErrorAsList,
)
from tests.unit.helpers.document_builder import DocumentBuilder


def _build_traceability_index(document_list, project_config):
    document_tree = DocumentTree(
        file_tree=[],
        document_list=document_list,
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    return TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=project_config
    )


def test_validate_can_remove_document_with_incoming_link():
    document_builder = DocumentBuilder("DOC-1")
    requirement_1 = document_builder.add_requirement("REQ-001")
    requirement_2 = document_builder.add_requirement("REQ-002")
    document = document_builder.build()

    traceability_index = _build_traceability_index(
        [document], document_builder.project_config
    )
    traceability_index.create_inline_link(
        InlineLink(
            parent=SimpleNamespace(parent=requirement_1),
            value=requirement_2.reserved_uid,
        )
    )

    with pytest.raises(MultipleValidationErrorAsList):
        traceability_index.validate_can_remove_document(document)


def test_validate_can_remove_document_with_parent_relation():
    document_builder = DocumentBuilder("DOC-1")
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    document = document_builder.build()

    traceability_index = _build_traceability_index(
        [document], document_builder.project_config
    )

    with pytest.raises(MultipleValidationErrorAsList):
        traceability_index.validate_can_remove_document(document)


def test_validate_can_remove_document_included_elsewhere():
    document_builder_1 = DocumentBuilder("DOC-1")
    document_1 = document_builder_1.build()

    document_builder_2 = DocumentBuilder("DOC-2")
    document_2 = document_builder_2.build()

    document_2.ng_including_document_reference = DocumentReference()
    document_2.ng_including_document_reference.set_document(document_1)
    document_1.included_documents.append(document_2)

    traceability_index = _build_traceability_index(
        [document_1, document_2], document_builder_1.project_config
    )

    with pytest.raises(MultipleValidationErrorAsList):
        traceability_index.validate_can_remove_document(document_2)