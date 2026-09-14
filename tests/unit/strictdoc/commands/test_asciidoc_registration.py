import argparse

import pytest

from strictdoc.backend.asciidoc.asciidoc_format import AsciiDocFormat
from strictdoc.commands.convert import _check_output_format
from strictdoc.commands.export import EXPORT_FORMATS, _check_formats
from strictdoc.core.project_config import ProjectConfig


def test_asciidoc_is_discovered_without_project_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["strictdoc", "export"])
    assert _check_formats("asciidoc") == ["asciidoc"]
    assert EXPORT_FORMATS.count("asciidoc") == 1
    registered_formats = [
        format_
        for format_ in ProjectConfig.default_formats()
        if "asciidoc" in format_.handles()
    ]
    assert len(registered_formats) == 1
    assert isinstance(registered_formats[0], AsciiDocFormat)


def test_unknown_export_format_reports_asciidoc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["strictdoc", "export"])
    with pytest.raises(argparse.ArgumentTypeError, match="asciidoc"):
        _check_formats("unknown-format")


def test_asciidoc_capabilities_are_export_only() -> None:
    assert AsciiDocFormat.supports_export()
    assert AsciiDocFormat.supported_extensions() == [".adoc"]
    assert not AsciiDocFormat.supports_import()
    assert not AsciiDocFormat.supports_read()
    assert not AsciiDocFormat.supports_edit()
    assert not AsciiDocFormat.supports_grammar()
    assert not AsciiDocFormat.supports_convert_output()


def test_convert_rejects_asciidoc_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["strictdoc", "convert"])
    with pytest.raises(argparse.ArgumentTypeError, match="invalid choice"):
        _check_output_format("asciidoc")
