from typing import List


def convert_nextest_test_to_rust_canonical_paths(
    classname: str, name: str
) -> List[str]:
    """
    Map a cargo-nextest test identity to candidate Rust canonical paths, in
    resolution order; the first one the source-code index knows about wins.

    StrictDoc stores functions under ``<file_stem>::...`` while cargo-nextest
    reports ``classname`` (the binary id) and ``name`` (the in-binary test
    path) with no source file, so the stem is inferred:

    - integration-test binary (``classname`` contains ``::``) → file stem is
      the part after the last ``::``  → ``<stem>::<name>``;
    - crate unit tests (no ``::``) → ``lib::<name>`` then ``main::<name>``.

    See the cargo-nextest section of the user guide for the full rationale.
    """
    assert isinstance(classname, str)
    assert isinstance(name, str)
    assert len(classname) > 0
    assert len(name) > 0

    if "::" in classname:
        _, _, file_stem = classname.rpartition("::")
        return [f"{file_stem}::{name}"]

    return [f"lib::{name}", f"main::{name}"]
