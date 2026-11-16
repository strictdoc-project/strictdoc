from strictdoc.backend.rst.rst_inline_link_placeholders import (
    RstInlineLinkPlaceholders,
)

LINK_HTML = '<a href="#UID-1">UID-1</a>'


def test_01_placeholder_has_source_length():
    placeholders = RstInlineLinkPlaceholders(["Text."])

    placeholder = placeholders.create_placeholder(
        source_length=len("[LINK: UID-1]"),
        link_html=LINK_HTML,
        text_after=" text.",
    )

    assert placeholder == "Lka0xxxxxxxxx"
    assert len(placeholder) == len("[LINK: UID-1]")


def test_02_placeholder_followed_by_letter_is_not_escaped():
    placeholders = RstInlineLinkPlaceholders([])

    placeholder = placeholders.create_placeholder(
        source_length=9, link_html=LINK_HTML, text_after="s text."
    )

    assert placeholder == "Lka0xxxxx"


def test_03_placeholder_followed_by_markup_character_is_escaped():
    placeholders = RstInlineLinkPlaceholders([])

    placeholder = placeholders.create_placeholder(
        source_length=9, link_html=LINK_HTML, text_after="_ text."
    )

    assert placeholder == "Lka0xxxx\\"
    assert len(placeholder) == 9


def test_04_prefix_does_not_occur_in_text():
    placeholders = RstInlineLinkPlaceholders(["Lka and Lkb are in the text."])

    placeholder = placeholders.create_placeholder(
        source_length=9, link_html=LINK_HTML, text_after=""
    )

    assert placeholder == "Lkc0xxxxx"


def test_05_replace_placeholders():
    placeholders = RstInlineLinkPlaceholders([])
    placeholder_1 = placeholders.create_placeholder(
        source_length=9, link_html='<a href="#A">A</a>', text_after=""
    )
    placeholder_2 = placeholders.create_placeholder(
        source_length=9, link_html='<a href="#B">B</a>', text_after=""
    )

    html = placeholders.replace_placeholders(
        f"<p>{placeholder_1} and {placeholder_2}s.</p>"
    )

    assert html == '<p><a href="#A">A</a> and <a href="#B">B</a>s.</p>'
