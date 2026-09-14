from html import unescape
from pathlib import Path

import pytest

from strictdoc.backend.asciidoc.asciidoc_format import AsciiDocFormat
from strictdoc.backend.sdoc.node_filter import NodeFilter
from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.export.export_action import ExportAction
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_system import file_open_read_utf8
from strictdoc.helpers.parallelizer import NullParallelizer


def test_rebuild_removes_stale_pages_and_preserves_adjacent_output(
    tmp_path: Path,
) -> None:
    source = tmp_path / "input"
    source.mkdir()
    original = source / "original.sdoc"
    original.write_text(_document("Original", "REQ-1"), encoding="utf-8")
    output = tmp_path / "output"
    adjacent = output / "html" / "handwritten.html"
    adjacent.parent.mkdir(parents=True)
    adjacent.write_text("keep me", encoding="utf-8")

    _action(source, output).export()
    exported = output / "asciidoc" / "original.adoc"
    first_export = _read(exported)
    assert "UID:: REQ-1" in first_export
    _action(source, output).export()
    assert _read(exported) == first_export

    original.rename(source / "renamed.sdoc")
    _action(source, output).export()
    assert not exported.exists()
    assert _read(output / "asciidoc" / "renamed.adoc") == first_export
    assert _read(adjacent) == "keep me"
    assert not list(output.glob(".asciidoc-*"))


def test_conversion_failure_preserves_previous_export(tmp_path: Path) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "valid.sdoc").write_text(
        _document("Valid", "REQ-VALID"), encoding="utf-8"
    )
    output = tmp_path / "output"
    _action(source, output).export()
    exported = output / "asciidoc" / "valid.adoc"
    original = _read(exported)
    (source / "invalid.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Invalid\n\n[TEXT]\nSTATEMENT: >>>\n"
        ".. note:: Unsupported content.\n<<<\n",
        encoding="utf-8",
    )

    with pytest.raises(StrictDocException, match="unsupported RST"):
        _action(source, output).export()

    assert _read(exported) == original
    assert not (output / "asciidoc" / "invalid.adoc").exists()


def test_filtered_reference_fails_without_publishing_broken_link(
    tmp_path: Path,
) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "input.sdoc").write_text(
        _document("Filtered", "TARGET")
        + "\n[TEXT]\nSTATEMENT: >>>\nRefer to [LINK: TARGET].\n<<<\n",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    action = _action(source, output)
    target = action.traceability_index.get_linkable_node_by_uid("TARGET")
    action.traceability_index.node_filter = NodeFilter({target})

    with pytest.raises(StrictDocException, match="filtered out"):
        action.export()
    assert not (output / "asciidoc").exists()


def test_cross_directory_links_encode_path_characters(tmp_path: Path) -> None:
    source = tmp_path / "input"
    nested = source / "space directory"
    nested.mkdir(parents=True)
    (source / "index.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Same title\n\n[TEXT]\nSTATEMENT: >>>\n"
        "See [LINK: REQ-1].\n<<<\n",
        encoding="utf-8",
    )
    (nested / "spec.v1.sdoc").write_text(
        _document("Same title", "REQ-1"), encoding="utf-8"
    )
    output = tmp_path / "output"
    _action(source, output).export()
    assert (output / "asciidoc" / "space directory" / "spec.v1.adoc").exists()
    assert "xref:space%20directory/spec.v1.adoc#REQ-1[Requirement]" in _read(
        output / "asciidoc" / "index.adoc"
    )


def test_owned_output_symlink_does_not_modify_external_directory(
    tmp_path: Path,
) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "input.sdoc").write_text(
        _document("Example", "REQ-1"), encoding="utf-8"
    )
    external = tmp_path / "external"
    external.mkdir()
    marker = external / "handwritten.adoc"
    marker.write_text("keep me", encoding="utf-8")
    output = tmp_path / "output"
    output.mkdir()
    try:
        (output / "asciidoc").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks are unavailable on this system.")

    with pytest.raises(StrictDocException, match="symlink"):
        _action(source, output).export()
    assert _read(marker) == "keep me"
    assert list(external.iterdir()) == [marker]


@pytest.mark.parametrize(
    ("uid", "anchor"),
    [
        ("REQ-1", "REQ-1"),
        ("ID_", "ID_"),
        ("req:1", "sd_uid_7265713a31"),
        ("日本語", "sd_uid_e697a5e69cace8aa9e"),
        ("sd_uid_61", "sd_uid_73645f7569645f3631"),
    ],
)
def test_uid_mapping_retains_literal_identifier(
    tmp_path: Path, uid: str, anchor: str
) -> None:
    source = tmp_path / "input.sdoc"
    source.write_text(_document("Identifier", uid), encoding="utf-8")
    output = tmp_path / "output"
    _action(source, output).export()
    exported = _read(output / "asciidoc" / "input.adoc")
    assert f"[[{anchor}]]" in exported
    assert uid in unescape(exported)


def test_duplicate_page_anchor_fails(tmp_path: Path) -> None:
    source = tmp_path / "input.sdoc"
    source.write_text(_document("Repeated", "REQ-1"), encoding="utf-8")
    output = tmp_path / "output"
    action = _action(source, output)
    document = action.traceability_index.document_tree.document_list[0]
    document.section_contents.append(document.section_contents[0])
    with pytest.raises(StrictDocException, match="duplicate anchor"):
        action.export()
    assert not (output / "asciidoc").exists()


def _action(source: Path, output: Path) -> ExportAction:
    formats = [
        format_
        for format_ in ProjectConfig.default_formats()
        if "asciidoc" not in format_.handles()
    ]
    config = ProjectConfig(formats=[*formats, AsciiDocFormat()])
    config.input_paths = [str(source)]
    config.output_dir = str(output)
    config.export_output_html_root = str(output / "html")
    config.dir_for_sdoc_cache = str(output / "_cache")
    config.export_formats = ["asciidoc"]
    return ExportAction(config, NullParallelizer())


def _document(title: str, uid: str) -> str:
    return (
        f"[DOCUMENT]\nTITLE: {title}\n\n"
        f"[REQUIREMENT]\nUID: {uid}\nTITLE: Requirement\n"
        "STATEMENT: The system shall preserve its source content.\n"
    )


def _read(path: Path) -> str:
    with file_open_read_utf8(str(path)) as source:
        return source.read()
