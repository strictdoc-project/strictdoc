from strictdoc.helpers.cargo_nextest import (
    convert_nextest_test_to_rust_canonical_paths,
)


def test_unit_test_in_library_yields_lib_and_main_candidates():
    assert convert_nextest_test_to_rust_canonical_paths(
        "my_crate", "tests::add_works"
    ) == ["lib::tests::add_works", "main::tests::add_works"]


def test_integration_test_uses_test_target_name_as_stem():
    assert convert_nextest_test_to_rust_canonical_paths(
        "my_crate::integration", "integration_add"
    ) == ["integration::integration_add"]


def test_nested_module_test_path_is_passed_through():
    assert convert_nextest_test_to_rust_canonical_paths(
        "my_crate", "tests::nested::nested_module_test"
    ) == [
        "lib::tests::nested::nested_module_test",
        "main::tests::nested::nested_module_test",
    ]
