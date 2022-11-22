import pytest

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from tests.unit.helpers.test_document_builder import DocumentBuilder


def test_valid_01_one_document_with_1req():
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree
    )
    parent_requirements = traceability_index.get_parent_requirements(
        requirement
    )
    assert parent_requirements == []


def test_valid_02_one_document_with_1req():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    requirement3 = document_builder.add_requirement("REQ-003")
    requirement4 = document_builder.add_requirement("REQ-004")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-004", "REQ-003")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree
    )
    requirement1_parents = traceability_index.get_parent_requirements(
        requirement1
    )
    assert requirement1_parents == []

    requirement2_parents = traceability_index.get_parent_requirements(
        requirement2
    )
    assert requirement2_parents == [requirement1]

    requirement3_parents = traceability_index.get_parent_requirements(
        requirement3
    )
    assert requirement3_parents == [requirement1, requirement2]

    requirement4_parents = traceability_index.get_parent_requirements(
        requirement4
    )
    assert requirement4_parents == [requirement3]


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
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


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
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)
