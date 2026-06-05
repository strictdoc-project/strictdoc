from strictdoc.backend.gcov.helpers import (
    convert_function_name_to_gcovr_style,
    normalize_gcovr_file_path,
)


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
