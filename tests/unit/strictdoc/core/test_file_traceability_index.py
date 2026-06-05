from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)
from strictdoc.core.file_traceability_index import FileTraceabilityIndex


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
