from strictdoc.backend.gcov.helpers import (
    convert_function_name_to_gcovr_style,
    create_gcovr_html_details_link,
    normalize_gcovr_file_path,
)

FUNCTIONS_CPP_HASH = "c5e71015e270864c89a8b6e26afb227b"


def test_create_gcovr_html_details_link_from_url():
    assert create_gcovr_html_details_link(
        gcovr_html_report="https://ci.example.com/coverage/index.html",
        source_file_path="src/functions.cpp",
        export_output_html_root="/project/output/html",
        document_level=1,
    ) == (
        "https://ci.example.com/coverage/"
        f"index.functions.cpp.{FUNCTIONS_CPP_HASH}.html"
    )


def test_create_gcovr_html_details_link_from_path():
    assert create_gcovr_html_details_link(
        gcovr_html_report="/project/build/coverage.html",
        source_file_path="src/functions.cpp",
        export_output_html_root="/project/output/html",
        document_level=1,
    ) == (f"../../../build/coverage.functions.cpp.{FUNCTIONS_CPP_HASH}.html")


def test_create_gcovr_html_details_link_from_path_for_nested_document():
    assert create_gcovr_html_details_link(
        gcovr_html_report="/project/output/html/gcovr/coverage.html",
        source_file_path="src/functions.cpp",
        export_output_html_root="/project/output/html",
        document_level=3,
    ) == (f"../../../gcovr/coverage.functions.cpp.{FUNCTIONS_CPP_HASH}.html")


def test_normalize_gcovr_file_path():
    assert normalize_gcovr_file_path("src\\functions.cpp") == (
        "src/functions.cpp"
    )
    assert normalize_gcovr_file_path("src/functions.cpp") == (
        "src/functions.cpp"
    )
    assert (
        normalize_gcovr_file_path(
            "D:\\a\\strictdoc\\strictdoc\\docs\\src\\functions.cpp",
            source_root_path="D:\\a\\strictdoc\\strictdoc\\docs",
        )
        == "src/functions.cpp"
    )


def test_convert_function_name_to_gcovr_style():
    assert (
        convert_function_name_to_gcovr_style(
            "test::Adder::add(const int& a, const int& b)"
        )
        == "test::Adder::add(int const&, int const&)"
    )
    assert (
        convert_function_name_to_gcovr_style(
            "test::Multiplier::multiply(int a, const int& b)"
        )
        == "test::Multiplier::multiply(int, int const&)"
    )
