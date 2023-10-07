import pytest

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from tests.unit.helpers.test_document_builder import DocumentBuilder


def test_invalid_01_2_reqs_cycled():
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")
    document_builder.add_requirement_parent("REQ-001", "REQ-002")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test_invalid_02_4_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")
    document_builder.add_requirement_parent("REQ-004", "REQ-003")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")
    document_builder.add_requirement_parent("REQ-001", "REQ-004")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test_invalid_03_3_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    document_builder.add_requirement_parent("REQ-003", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-002", "REQ-003")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test_invalid_04_5_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")
    _ = document_builder.add_requirement("REQ-005")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-004", "REQ-003")
    document_builder.add_requirement_parent("REQ-005", "REQ-004")
    document_builder.add_requirement_parent("REQ-003", "REQ-005")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError) as exc_info:
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)

    exception: DocumentTreeError = exc_info.value
    assert exception.problem_uid == "REQ-003"
    assert exception.cycled_uids == [
        "REQ-001",
        "REQ-002",
        "REQ-003",
        "REQ-004",
        "REQ-005",
    ]


def test_invalid_05_4_reqs_good_then_3_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")

    document_builder.add_requirement_parent("REQ-004", "REQ-003")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")

    _ = document_builder.add_requirement("REQ-005")
    _ = document_builder.add_requirement("REQ-006")
    _ = document_builder.add_requirement("REQ-007")

    document_builder.add_requirement_parent("REQ-006", "REQ-005")
    document_builder.add_requirement_parent("REQ-007", "REQ-006")
    document_builder.add_requirement_parent("REQ-005", "REQ-007")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test__adding_parent_link__03__two_requirements_disallow_cycle():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.update_requirement_parent_uid(
        requirement2, "REQ-001", None
    )
    with pytest.raises(DocumentTreeError) as exc_info:
        traceability_index.update_requirement_parent_uid(
            requirement1, "REQ-002", role=None
        )

    exception: DocumentTreeError = exc_info.value
    assert exception.problem_uid == "REQ-001"
    assert exception.cycled_uids == ["REQ-001", "REQ-002"]
