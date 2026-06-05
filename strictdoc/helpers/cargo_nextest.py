from typing import List


def convert_nextest_test_to_rust_canonical_paths(
    classname: str, name: str
) -> List[str]:
    """
    The Rust canonical path of a cargo-nextest test: ``classname::name``.

    ``classname`` is the crate's ``[package]`` name (optionally ``::<binary>``
    for an integration test); ``name`` is the in-binary test path. See the
    cargo-nextest section of the user guide.
    """
    assert isinstance(classname, str)
    assert isinstance(name, str)
    assert len(classname) > 0
    assert len(name) > 0

    return [f"{classname}::{name}"]
