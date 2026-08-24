from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.features.tree_map_html.data_generator import (
    TreeMapDataGenerator,
)
from tests.unit.helpers.document_builder import DocumentBuilder


def test_generates_the_three_default_tree_maps() -> None:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    document = document_builder.build()
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree,
        project_config=document_builder.project_config,
    )

    tree_map_data = TreeMapDataGenerator.generate(
        project_config=document_builder.project_config,
        traceability_index=traceability_index,
    )

    assert tuple(tree_map_.title for tree_map_ in tree_map_data.tree_maps) == (
        "Document tree map",
        "Requirements coverage with source",
        "Requirements coverage with test",
    )

    document_tree_map = tree_map_data.tree_maps[0]
    assert document_tree_map.root.label == "Untitled Project"
    assert len(document_tree_map.root.children) == 1
    document_node = document_tree_map.root.children[0]
    assert document_node.label == "Test Document (2)"
    assert tuple(node_.label for node_ in document_node.children) == (
        "Requirement title",
        "Requirement title",
    )

    source_coverage_tree_map = tree_map_data.tree_maps[1]
    source_document_node = source_coverage_tree_map.root.children[0]
    assert source_document_node.label == "Test Document (2)"
    assert source_document_node.color == "#ffaaaa"
    assert tuple(node_.color for node_ in source_document_node.children) == (
        "#ffaaaa",
        "#ffaaaa",
    )

    test_coverage_tree_map = tree_map_data.tree_maps[2]
    test_document_node = test_coverage_tree_map.root.children[0]
    assert test_document_node.color == "#ffaaaa"
    assert tuple(node_.color for node_ in test_document_node.children) == (
        "#ffaaaa",
        "#ffaaaa",
    )


def test_distinguishes_source_and_test_coverage() -> None:
    document_builder = DocumentBuilder()
    source_requirement = document_builder.add_requirement("REQ-SOURCE")
    test_requirement = document_builder.add_requirement("REQ-TEST")
    document = document_builder.build()
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree,
        project_config=document_builder.project_config,
    )
    file_traceability_index = traceability_index.get_file_traceability_index()
    source_path = "src/module.py"
    test_path = "tests/test_module.py"
    file_traceability_index.map_paths_to_source_file_traceability_info[
        source_path
    ] = SourceFileTraceabilityInfo([])
    file_traceability_index.map_paths_to_source_file_traceability_info[
        test_path
    ] = SourceFileTraceabilityInfo([])
    file_traceability_index.connect_sdoc_node_with_file_path(
        source_requirement,
        source_path,
    )
    file_traceability_index.connect_sdoc_node_with_file_path(
        test_requirement,
        test_path,
    )

    tree_map_data = TreeMapDataGenerator.generate(
        project_config=document_builder.project_config,
        traceability_index=traceability_index,
    )

    source_document_node = tree_map_data.tree_maps[1].root.children[0]
    assert source_document_node.color == "#ffffaa"
    assert tuple(node_.color for node_ in source_document_node.children) == (
        "#aaffaa",
        "#ffaaaa",
    )

    test_document_node = tree_map_data.tree_maps[2].root.children[0]
    assert test_document_node.color == "#ffffaa"
    assert tuple(node_.color for node_ in test_document_node.children) == (
        "#ffaaaa",
        "#aaffaa",
    )


def test_inherits_coverage_from_child_requirements() -> None:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-PARENT")
    child_requirement = document_builder.add_requirement("REQ-CHILD")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-CHILD",
        target_requirement_id="REQ-PARENT",
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
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree,
        project_config=document_builder.project_config,
    )
    file_traceability_index = traceability_index.get_file_traceability_index()
    source_path = "src/module.py"
    file_traceability_index.map_paths_to_source_file_traceability_info[
        source_path
    ] = SourceFileTraceabilityInfo([])
    file_traceability_index.connect_sdoc_node_with_file_path(
        child_requirement,
        source_path,
    )

    tree_map_data = TreeMapDataGenerator.generate(
        project_config=document_builder.project_config,
        traceability_index=traceability_index,
    )

    source_document_node = tree_map_data.tree_maps[1].root.children[0]
    assert source_document_node.color == "#aaffaa"
    assert tuple(node_.color for node_ in source_document_node.children) == (
        "#aaffaa",
        "#aaffaa",
    )
