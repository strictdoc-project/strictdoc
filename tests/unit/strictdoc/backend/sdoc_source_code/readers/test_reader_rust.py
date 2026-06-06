"""
@relation(SDOC-SRS-142, scope=file)
"""

from pathlib import Path

from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_rust import (
    SourceFileTraceabilityReader_Rust,
    rust_canonical_crate_segments,
    rust_crate_root_and_name,
    rust_module_segments_within_crate,
)


def _read(source: bytes, file_path: str) -> SourceFileTraceabilityInfo:
    return SourceFileTraceabilityReader_Rust().read(source, file_path=file_path)


def _function_named(info: SourceFileTraceabilityInfo, name: str):
    matches = [function for function in info.functions if function.name == name]
    assert len(matches) == 1, (
        f"expected exactly one function named {name!r}, got "
        f"{[function.name for function in info.functions]}"
    )
    return matches[0]


def _crate(root: Path, package_name: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "Cargo.toml").write_text(
        f'[package]\nname = "{package_name}"\n'
        'version = "0.1.0"\nedition = "2024"\n',
        encoding="utf-8",
    )
    return root


def _read_one(file_path: str, source_body: bytes, fn_name: str):
    source = b"/// @relation(REQ-1, scope=function)\n" + source_body
    info = _read(source, file_path=file_path)
    return _function_named(info, fn_name)


def test_module_segments_within_crate_mapping():
    f = rust_module_segments_within_crate
    assert f(()) == []
    assert f(("src", "lib.rs")) == []
    assert f(("src", "main.rs")) == []
    assert f(("src", "model.rs")) == ["model"]
    assert f(("src", "model", "mod.rs")) == ["model"]
    assert f(("src", "a", "b", "c.rs")) == ["a", "b", "c"]
    assert f(("src", "model", "tests.rs")) == ["model", "tests"]
    assert f(("tests", "it.rs")) == ["it"]
    assert f(("tests", "it", "helper.rs")) == ["it", "helper"]
    assert f(("tests", "it", "main.rs")) == ["it"]


def test_crate_root_and_name_finds_enclosing_package(tmp_path):
    _crate(tmp_path, "my_crate")
    found = rust_crate_root_and_name(str(tmp_path / "src"))
    assert found == (str(tmp_path), "my_crate")


def test_crate_root_and_name_keeps_hyphenated_package_name(tmp_path):
    _crate(tmp_path, "weird-pkg-name")
    found = rust_crate_root_and_name(str(tmp_path / "src"))
    assert found == (str(tmp_path), "weird-pkg-name")


def test_crate_root_and_name_skips_workspace_only_manifest(tmp_path):
    (tmp_path / "Cargo.toml").write_text(
        '[workspace]\nmembers = ["crates/foo"]\n', encoding="utf-8"
    )
    assert rust_crate_root_and_name(str(tmp_path / "src")) is None


def test_crate_root_and_name_returns_none_without_manifest(tmp_path):
    assert rust_crate_root_and_name(str(tmp_path / "src")) is None


def test_canonical_segments_crate_qualified(tmp_path):
    _crate(tmp_path, "my_crate")
    assert rust_canonical_crate_segments(str(tmp_path / "src" / "lib.rs")) == [
        "my_crate"
    ]
    assert rust_canonical_crate_segments(
        str(tmp_path / "src" / "a" / "b" / "c.rs")
    ) == ["my_crate", "a", "b", "c"]


def test_canonical_segments_fall_back_to_stem_without_cargo(tmp_path):
    flat = tmp_path / "forward_relations.rs"
    assert rust_canonical_crate_segments(str(flat)) == ["forward_relations"]


def test_canonical_segments_none_path():
    assert rust_canonical_crate_segments(None) == []


def test_empty_file():
    info = _read(b"", file_path="src/lib.rs")
    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_relation_marker_is_attached_to_function(tmp_path):
    _crate(tmp_path, "my_crate")
    source = b"""\
/// @relation(REQ-1, scope=function)
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
"""
    info = _read(source, file_path=str(tmp_path / "src" / "lib.rs"))
    function = _function_named(info, "my_crate::add")
    assert function.markers[0].reqs == ["REQ-1"]


def test_function_range_folds_in_leading_attributes_and_doc_comment():
    source = b"""\
#[cfg(test)]
mod tests {
    /// @relation(REQ-1, scope=function)
    #[test]
    fn add_works() {
        assert_eq!(2 + 2, 4);
    }
}
"""
    info = _read(source, file_path="lib.rs")
    # doc comment = 3, #[test] = 4, fn = 5, closing brace = 7.
    fn = _function_named(info, "lib::tests::add_works")
    assert fn.line_begin == 3
    assert fn.line_end == 7
    module = _function_named(info, "lib::tests")
    assert module.line_begin == 1


def test_canonical_path_crate_root_lib(tmp_path):
    _crate(tmp_path, "my_crate")
    fn = _read_one(
        str(tmp_path / "src" / "lib.rs"), b"pub fn add() {}\n", "my_crate::add"
    )
    assert fn.markers[0].reqs == ["REQ-1"]


def test_canonical_path_crate_root_main(tmp_path):
    _crate(tmp_path, "my_crate")
    _read_one(
        str(tmp_path / "src" / "main.rs"),
        b"pub fn helper() {}\n",
        "my_crate::helper",
    )


def test_canonical_path_top_level_module_file(tmp_path):
    _crate(tmp_path, "my_crate")
    _read_one(
        str(tmp_path / "src" / "model.rs"),
        b"pub fn parse() {}\n",
        "my_crate::model::parse",
    )


def test_canonical_path_nested_module_file(tmp_path):
    _crate(tmp_path, "my_crate")
    _read_one(
        str(tmp_path / "src" / "a" / "b" / "c.rs"),
        b"pub fn run() {}\n",
        "my_crate::a::b::c::run",
    )


def test_canonical_path_mod_rs_uses_directory_name(tmp_path):
    _crate(tmp_path, "my_crate")
    _read_one(
        str(tmp_path / "src" / "model" / "mod.rs"),
        b"pub fn run() {}\n",
        "my_crate::model::run",
    )


def test_canonical_path_submodule_file(tmp_path):
    _crate(tmp_path, "my_crate")
    _read_one(
        str(tmp_path / "src" / "model" / "tests.rs"),
        b"pub fn round_trips() {}\n",
        "my_crate::model::tests::round_trips",
    )


def test_canonical_path_inline_mod_nesting(tmp_path):
    _crate(tmp_path, "my_crate")
    source = b"""\
mod tests {
    /// @relation(REQ-3, scope=function)
    pub fn it_works() {}
}
"""
    info = _read(source, file_path=str(tmp_path / "src" / "element_id.rs"))
    fn = _function_named(info, "my_crate::element_id::tests::it_works")
    assert fn.markers[0].reqs == ["REQ-3"]


def test_canonical_path_integration_test_root(tmp_path):
    _crate(tmp_path, "my_crate")
    _read_one(
        str(tmp_path / "tests" / "it.rs"),
        b"fn it_runs() {}\n",
        "my_crate::it::it_runs",
    )


def test_canonical_path_integration_test_submodule(tmp_path):
    _crate(tmp_path, "my_crate")
    _read_one(
        str(tmp_path / "tests" / "it" / "helper.rs"),
        b"fn helps() {}\n",
        "my_crate::it::helper::helps",
    )


def test_canonical_path_non_cargo_flat_file_uses_stem(tmp_path):
    fn = _read_one(
        str(tmp_path / "forward_relations.rs"),
        b"pub fn parse() {}\n",
        "forward_relations::parse",
    )
    assert fn.markers[0].reqs == ["REQ-1"]


def test_canonical_path_non_cargo_nested_modules(tmp_path):
    source = b"""\
mod foo_module {
    mod foo {
        /// @relation(REQ-2, scope=function)
        pub fn bar() {}
    }
}
"""
    info = _read(source, file_path=str(tmp_path / "forward_relations.rs"))
    fn = _function_named(info, "forward_relations::foo_module::foo::bar")
    assert fn.markers[0].reqs == ["REQ-2"]


def test_canonical_path_workspace_members_stay_distinct(tmp_path):
    (tmp_path / "Cargo.toml").write_text(
        '[workspace]\nmembers = ["crates/foo", "crates/bar"]\n',
        encoding="utf-8",
    )
    _crate(tmp_path / "crates" / "foo", "foo-crate")
    _crate(tmp_path / "crates" / "bar", "bar-crate")
    body = b"""\
mod tests {
    /// @relation(REQ-1, scope=function)
    pub fn common_test() {}
}
"""
    foo = _read(
        body, file_path=str(tmp_path / "crates" / "foo" / "src" / "lib.rs")
    )
    bar = _read(
        body, file_path=str(tmp_path / "crates" / "bar" / "src" / "lib.rs")
    )
    _function_named(foo, "foo-crate::tests::common_test")
    _function_named(bar, "bar-crate::tests::common_test")
