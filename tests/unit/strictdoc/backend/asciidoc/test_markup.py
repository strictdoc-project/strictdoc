import shutil
import subprocess
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import pytest
from lxml import etree

from strictdoc.backend.asciidoc.markup import MarkupRenderer, escape_text
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNodeField
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_system import file_open_read_utf8


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("ZEP-SRS-26-1", "ZEP-SRS-26-1"),
        ("32-bit", "32-bit"),
        ("- list item", "&#45; list item"),
        ("--", "&#45;&#45;"),
        ("----", "&#45;&#45;&#45;&#45;"),
        ("word--word", "word&#45;&#45;word"),
        ("-REQ-", "&#45;REQ&#45;"),
    ],
)
def test_escape_text_preserves_only_internal_single_hyphens(
    source: str, expected: str
) -> None:
    assert escape_text(source) == expected


def test_escape_text_prevents_asciidoc_macro_interpretation() -> None:
    assert escape_text("include::secret.adoc[]") == (
        "include&#58;&#58;secret&#46;adoc&#91;&#93;"
    )


def test_render_rst_preserves_text_with_informational_diagnostic() -> None:
    source = (
        "See ZEP104\n+\n"
        "When the power state is changed I want to get an notification "
        "in order for specific parts of my application to react accordingly."
    )
    output = _renderer().render(
        _field([source]),
        "RST",
        "power_management.sdoc: ZEP-SRS-13-1 USER_STORY occurrence 1",
    )

    assert unescape(output) == source + "\n"
    assert "&#43;" in output


@pytest.mark.parametrize("source", ["**unfinished", ".. unknown:: content"])
def test_render_rst_still_rejects_parser_warnings_and_errors(
    source: str,
) -> None:
    with pytest.raises(StrictDocException, match="RST parsing failed"):
        _renderer().render(
            _field([source]),
            "RST",
            "input.sdoc: REQ-1 STATEMENT occurrence 1",
        )


def test_render_rst_preserves_formatting_around_strictdoc_link() -> None:
    output = _renderer().render(
        _field(["**Before ", InlineLink(None, "TARGET"), " after**"]),
        "RST",
        "input.sdoc: REQ-1 STATEMENT occurrence 1",
    )

    assert output == "**Before xref:#TARGET[Target title] after**\n"


def test_render_rst_literal_code_does_not_execute_asciidoc_directives() -> None:
    output = _renderer().render(
        _field(
            [
                (
                    ".. code-block:: text\n\n"
                    "   include::secret.adoc[]\n"
                    "   ifdef::secret[]\n"
                )
            ]
        ),
        "RST",
        "input.sdoc: REQ-1 STATEMENT occurrence 1",
    )

    assert '[source,text,subs="specialchars,replacements"]' in output
    assert "include&#58;&#58;secret&#46;adoc&#91;&#93;" in output
    assert "ifdef&#58;&#58;secret&#91;&#93;" in output


def test_render_text_keeps_newlines_and_escapes_asciidoc_syntax() -> None:
    output = _renderer().render(
        _field(["first line\ninclude::secret.adoc[]\nlast line"]),
        "Text",
        "input.sdoc: TEXT STATEMENT occurrence 1",
    )
    assert output == (
        '[verse,subs="specialchars,macros,replacements"]\n'
        "____\n"
        "first line\n"
        "include&#58;&#58;secret&#46;adoc&#91;&#93;\n"
        "last line\n"
        "____\n"
    )


def test_render_anchor_only_field_uses_a_persistent_anchor_macro() -> None:
    field = _field([])
    field.parts = [Anchor(field, "ANCHOR-1", None)]

    assert (
        _renderer().render(
            field,
            "RST",
            "input.sdoc: REQ-1 STATEMENT occurrence 1",
        )
        == "anchor:ANCHOR-1[]\n"
    )


def test_render_rejects_unsupported_markup_with_source_context() -> None:
    with pytest.raises(StrictDocException) as exception:
        _renderer().render(
            _field(["# Heading"]),
            "Markdown",
            "input.sdoc: REQ-1 STATEMENT occurrence 1",
        )

    assert str(exception.value) == (
        "AsciiDoc export: input.sdoc: REQ-1 STATEMENT occurrence 1: "
        "unsupported source markup: Markdown"
    )


@pytest.mark.skipif(
    shutil.which("asciidoctor") is None,
    reason="Asciidoctor is not installed",
)
def test_rendered_code_keeps_hostile_asciidoc_text_literal(
    tmp_path: Path,
) -> None:
    source = _renderer().render(
        _field(
            [
                (
                    ".. code-block:: text\n\n"
                    "   include::secret.adoc[]\n"
                    "   eval::[1+1]\n"
                    "   ----\n"
                    "   {docname}\n"
                    "   \\include::secret.adoc[]\n"
                    "   &amp; <b>literal</b>\n"
                )
            ]
        ),
        "RST",
        "input.sdoc: REQ-1 STATEMENT occurrence 1",
    )
    source_path = tmp_path / "input.adoc"
    output_path = tmp_path / "output.html"
    source_path.write_text(source, encoding="utf-8")
    subprocess.run(
        [
            "asciidoctor",
            "--failure-level",
            "WARN",
            "-o",
            str(output_path),
            str(source_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    parser = _CodeTextParser()
    with file_open_read_utf8(str(output_path)) as rendered_file:
        parser.feed(rendered_file.read())
    assert parser.text == (
        "include::secret.adoc[]\neval::[1+1]\n----\n{docname}\n"
        "\\include::secret.adoc[]\n&amp; <b>literal</b>"
    )


@pytest.mark.parametrize(
    "content",
    [
        "* Outer\n\n  * Nested\n\n  Continuation.\n",
        "* Outer\n\n  * Middle\n\n    * Deep\n\n    Continuation.\n",
        "* Outer\n\n  Paragraph.\n\n  * Nested\n",
        "* Outer\n\n  * Nested\n\n  1. Another nested list\n",
    ],
)
def test_reject_nested_list_arrangements_that_change_item_structure(
    content: str,
) -> None:
    with pytest.raises(StrictDocException, match="a nested list must"):
        _renderer().render(
            _field([content]),
            "RST",
            "input.sdoc: REQ-1 STATEMENT occurrence 1",
        )


@pytest.mark.skipif(
    shutil.which("asciidoctor") is None,
    reason="Asciidoctor is not installed",
)
def test_rendered_adjacent_list_types_remain_siblings(tmp_path: Path) -> None:
    source = _renderer().render(
        _field(["* Bullet\n\n1. Numbered\n"]),
        "RST",
        "input.sdoc: REQ-1 STATEMENT occurrence 1",
    )
    source_path = tmp_path / "input.adoc"
    output_path = tmp_path / "output.html"
    source_path.write_text(source, encoding="utf-8")
    subprocess.run(
        [
            "asciidoctor",
            "--failure-level",
            "WARN",
            "-o",
            str(output_path),
            str(source_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    with file_open_read_utf8(str(output_path)) as rendered_file:
        document = etree.HTML(rendered_file.read())
    assert document is not None
    assert document.xpath("count(//ol/ancestor::li)") == 0
    assert document.xpath("//ol/li/p/text()") == ["Numbered"]
    assert document.xpath("//ul/li/p/text()") == ["Bullet"]


class _CodeTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_pre = False
        self.text = ""

    def handle_starttag(
        self, tag: str, _attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag == "pre":
            self.in_pre = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre":
            self.in_pre = False

    def handle_data(self, data: str) -> None:
        if self.in_pre:
            self.text += data


def _renderer() -> MarkupRenderer:
    return MarkupRenderer(
        resolve_link=lambda link_: (f"#{link_.link}", "Target title"),
        resolve_anchor=lambda anchor_: anchor_.value,
        resolve_image=lambda path_: f"_assets/{path_}",
    )


def _field(parts: list[object]) -> SDocNodeField:
    return SDocNodeField(
        parent=None,
        field_name="STATEMENT",
        parts=parts,
        multiline__="multiline",
    )
