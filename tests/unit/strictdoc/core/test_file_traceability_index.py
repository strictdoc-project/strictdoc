from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_traceability_index import FileTraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from tests.unit.helpers.document_builder import DocumentBuilder


def test_get_req_uids_by_function_names_matches_gcovr_name():
    file_traceability_index = FileTraceabilityIndex()
    file_traceability_index.map_file_function_names_to_reqs_uids[
        "functions.cpp"
    ] = {
        "test::Adder::add(int const&, int const&)": [
            (
                "GCOV:functions.cpp:test::Adder::add(int const&, int const&)",
                None,
            )
        ]
    }

    assert file_traceability_index.get_req_uids_by_function_names(
        "functions.cpp",
        [
            "test::Adder::add",
            "test::Adder::add(const int& a, const int& b)",
            "test::Adder::add(int const&, int const&)",
        ],
    ) == [("GCOV:functions.cpp:test::Adder::add(int const&, int const&)", None)]


def test_get_function_matching_names_includes_gcovr_style_cpp_name():
    source_file_traceability_info = SourceFileTraceabilityReader_C().read(
        b"""\
namespace test {

int Adder::add(const int& a, const int& b) {
  return a + b;
}
}
""",
        file_path="functions.cpp",
    )

    assert FileTraceabilityIndex.get_function_matching_names(
        source_file_traceability_info.functions[0]
    ) == [
        "test::Adder::add",
        "test::Adder::add(const int& a, const int& b)",
        "test::Adder::add(int const&, int const&)",
    ]


def test_calculate_code_coverage_counts_non_empty_covered_lines():
    """
    Lines 1-5 are covered, and line 3 is empty, so 4 of the 5 non-empty lines
    are covered.
    """
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document_builder.build()],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
    )
    traceability_info = SourceFileTraceabilityReader().read(
        "# @relation(REQ-001, scope=range_start)\n"
        "CONTENT 1\n"
        "\n"
        "CONTENT 2\n"
        "# @relation(REQ-001, scope=range_end)\n"
        "CONTENT 3\n"
    )
    file_traceability_index = FileTraceabilityIndex()
    file_traceability_index.map_paths_to_source_file_traceability_info[
        "file.txt"
    ] = traceability_info

    file_traceability_index.calculate_code_coverage_and_sort_nodes(
        traceability_index
    )

    assert traceability_info.merged_ranges == [[1, 5]]
    assert traceability_info.ng_lines_covered == 4
    assert traceability_info.get_coverage() == 80.0
