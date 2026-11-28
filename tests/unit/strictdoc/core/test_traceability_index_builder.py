"""
@relation(SDOC-SRS-32, scope=file)
"""

from typing import Any, Iterator, List

import pytest

from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from tests.unit.helpers.document_builder import DocumentBuilder


def test_01_document_tree_is_walked_once_per_document(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    document_builder.add_requirement("REQ-003")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-003",
        target_requirement_id="REQ-002",
        role=None,
    )
    document = document_builder.build()
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )

    walks: List[SDocDocumentIterator] = []
    all_content = SDocDocumentIterator.all_content

    def all_content_(
        self: SDocDocumentIterator, *args: Any, **kwargs: Any
    ) -> Iterator[Any]:
        walks.append(self)
        return all_content(self, *args, **kwargs)

    monkeypatch.setattr(SDocDocumentIterator, "all_content", all_content_)

    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
    )

    assert len(walks) == 1
    # The later passes still resolve the relations of all nodes.
    requirement_2 = traceability_index.get_node_by_uid("REQ-002")
    assert [
        node_.reserved_uid
        for node_ in traceability_index.get_parent_requirements(requirement_2)
    ] == ["REQ-001"]
    assert [
        node_.reserved_uid
        for node_ in traceability_index.get_children_requirements(requirement_2)
    ] == ["REQ-003"]
