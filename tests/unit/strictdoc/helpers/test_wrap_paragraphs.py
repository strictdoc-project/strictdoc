"""
Tests for RST and Markdown text formatters.
"""

from strictdoc.backend.rst.formatter import wrap_rst_text


def test_short_text_unchanged():
    text = "Short line."
    assert wrap_rst_text(text, 80) == text


def test_long_paragraph_wrapped():
    text = "word " * 20  # ~100 chars
    result = wrap_rst_text(text.strip(), 80)
    for line in result.split("\n"):
        assert len(line) <= 80


def test_paragraph_boundary_preserved():
    text = "First paragraph.\n\nSecond paragraph."
    result = wrap_rst_text(text, 80)
    assert "\n\n" in result
    assert "First paragraph." in result
    assert "Second paragraph." in result


def test_unordered_list_long_item_wrapped():
    long_item = "- " + "word " * 20
    text = long_item.strip()
    result = wrap_rst_text(text, 80)
    assert result != text
    lines = result.split("\n")
    assert len(lines) > 1
    # Continuation must be indented to align with item content (2 spaces for "- ")
    assert lines[1].startswith("  ")
    for line in lines:
        assert len(line) <= 80


def test_ordered_list_long_item_wrapped():
    long_item = "1. " + "word " * 20
    text = long_item.strip()
    result = wrap_rst_text(text, 80)
    assert result != text
    lines = result.split("\n")
    assert len(lines) > 1
    # Continuation must be indented to align with item content (3 spaces for "1. ")
    assert lines[1].startswith("   ")
    for line in lines:
        assert len(line) <= 80


def test_indented_block_not_wrapped():
    long_item = "    " + "word " * 20
    text = long_item.rstrip()
    result = wrap_rst_text(text, 80)
    assert result == text


def test_rst_directive_not_wrapped():
    text = ".. note:: " + "word " * 15
    text = text.strip()
    result = wrap_rst_text(text, 80)
    assert result == text


def test_multiple_long_paragraphs():
    para1 = "word " * 20
    para2 = "text " * 20
    text = para1.strip() + "\n\n" + para2.strip()
    result = wrap_rst_text(text, 80)
    assert "\n\n" in result
    for line in result.split("\n"):
        assert len(line) <= 80


def test_empty_string():
    assert wrap_rst_text("", 80) == ""


def test_link_keyword_not_split():
    # [LINK: some_uid] must never be broken at the space after the colon.
    prefix = "word " * 14  # ~70 chars — pushes the keyword near the limit
    text = prefix.rstrip() + " [LINK: SOME_UID]"
    result = wrap_rst_text(text, 80)
    assert "[LINK: SOME_UID]" in result
    for line in result.split("\n"):
        assert "[LINK:" not in line or "SOME_UID]" in line


def test_anchor_keyword_not_split():
    prefix = "word " * 14
    text = prefix.rstrip() + " [ANCHOR: MY_ANCHOR]"
    result = wrap_rst_text(text, 80)
    assert "[ANCHOR: MY_ANCHOR]" in result
    for line in result.split("\n"):
        assert "[ANCHOR:" not in line or "MY_ANCHOR]" in line


def test_link_keyword_not_split_real_world():
    # Real paragraph from the user guide where [LINK: SECTION-UG-Host-and-port]
    # was previously broken across two lines by textwrap.
    text = (
        "StrictDoc uses ``127.0.0.1`` as a default host and ``5111`` as a"
        " default port. When running within Docker, the host argument"
        " ``--host`` can be specified, for example, ``--host 0.0.0.0`` or a"
        " more specific host or IP address. The host and port can be also"
        " configured in the Python config file, see"
        " [LINK: SECTION-UG-Host-and-port]."
    )
    result = wrap_rst_text(text, 80)
    assert "[LINK: SECTION-UG-Host-and-port]" in result
    for line in result.split("\n"):
        assert "[LINK:" not in line or "SECTION-UG-Host-and-port]" in line


def test_rst_hyperlink_not_split():
    # RST hyperlink `text <url>`_ must not be broken at the space or at a
    # hyphen inside the URL.
    text = (
        "For a more comprehensive example, check the source file of this"
        " documentation which is written using StrictDoc:"
        " `strictdoc_01_user_guide.sdoc"
        " <https://github.com/strictdoc-project/strictdoc/blob/main/docs/strictdoc_01_user_guide.sdoc>`_."
    )
    result = wrap_rst_text(text, 80)
    for line in result.split("\n"):
        # The RST link must appear intact on a single line — never broken
        # at the space between link text and URL, or at a hyphen in the URL.
        assert (
            "`_" not in line
            or line.endswith("`_.")
            or line.strip().startswith("`")
        )


def test_markdown_link_not_split():
    # Markdown inline link [text](url) must not be broken mid-link.
    text = (
        "See the full documentation at"
        " [StrictDoc user guide](https://strictdoc-project.github.io/strictdoc/strictdoc_01_user_guide.html)"
        " for details."
    )
    result = wrap_rst_text(text, 80)
    for line in result.split("\n"):
        # Opening bracket must not appear on a line without its closing paren.
        if "[StrictDoc" in line:
            assert ")" in line


def test_list_item_starting_with_rst_link_stays_on_marker_line():
    # When an RST hyperlink is the FIRST content of a list item, it must stay
    # on the same line as the list marker even if the line exceeds line_width.
    long_link = "`StrictDoc user guide <https://strictdoc-project.github.io/strictdoc/strictdoc_01_user_guide.html>`_"
    text = f"- {long_link}"
    result = wrap_rst_text(text, 80)
    lines = result.split("\n")
    # The link must be on the first line together with "- ", not pushed down.
    assert lines[0].startswith("- `")
    assert lines[0].endswith("`_")


def test_list_item_starting_with_link_then_prose_wraps_prose():
    # When an RST link opens the list item and prose follows, the prose after
    # the link must be wrapped with proper continuation indentation.
    long_link = "`Guide <https://strictdoc-project.github.io/strictdoc/strictdoc_01_user_guide.html>`_"
    prose = "word " * 15  # enough to exceed 80 chars when combined
    text = f"- {long_link} {prose.strip()}"
    result = wrap_rst_text(text, 80)
    lines = result.split("\n")
    # First line: marker + link (may exceed width — that is the allowed exception)
    assert lines[0].startswith("- `")
    # Continuation lines must be indented by 2 spaces (the "- " marker width)
    for line in lines[1:]:
        assert line.startswith("  ")
