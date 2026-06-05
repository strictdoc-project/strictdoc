from strictdoc.helpers.cargo_nextest import (
    convert_nextest_test_to_rust_canonical_paths,
)


def test_unit_test_is_qualified_by_crate_name():
    assert convert_nextest_test_to_rust_canonical_paths(
        "my_crate", "tests::add_works"
    ) == ["my_crate::tests::add_works"]


def test_integration_test_keeps_package_and_binary_qualifier():
    assert convert_nextest_test_to_rust_canonical_paths(
        "my_crate::integration", "integration_add"
    ) == ["my_crate::integration::integration_add"]


def test_nested_module_test_path_is_passed_through():
    assert convert_nextest_test_to_rust_canonical_paths(
        "my_crate", "tests::nested::nested_module_test"
    ) == ["my_crate::tests::nested::nested_module_test"]


def test_workspace_members_with_same_test_name_stay_distinct():
    assert convert_nextest_test_to_rust_canonical_paths(
        "foo-crate", "tests::common_test"
    ) == ["foo-crate::tests::common_test"]
    assert convert_nextest_test_to_rust_canonical_paths(
        "bar-crate", "tests::common_test"
    ) == ["bar-crate::tests::common_test"]
