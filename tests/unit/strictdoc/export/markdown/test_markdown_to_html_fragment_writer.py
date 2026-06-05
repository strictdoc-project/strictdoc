from strictdoc.backend.markdown.markdown_to_html_fragment_writer import (
    MarkdownToHtmlFragmentWriter,
)


def test_01_writes_markdown_to_html_fragment():
    markdown_input = "This is **bold** text."

    html_output = MarkdownToHtmlFragmentWriter.write(markdown_input)

    assert html_output == "<p>This is <strong>bold</strong> text.</p>\n"


def test_02_writes_escaped_anchor_link():
    html_link = MarkdownToHtmlFragmentWriter.write_anchor_link(
        'A & B "Title"',
        'https://example.com?q=1&x="2"',
    )

    assert (
        html_link == '<a href="https://example.com?q=1&amp;x=&quot;2&quot;">'
        "🔗&nbsp;A &amp; B &quot;Title&quot;"
        "</a>"
    )


def test_03_write_with_validation_returns_html_without_error():
    html_output, error = MarkdownToHtmlFragmentWriter.write_with_validation(
        "Hello **Markdown**."
    )

    assert error is None
    assert html_output == "<p>Hello <strong>Markdown</strong>.</p>\n"


def test_04_writes_markdown_table_to_html_table():
    markdown_input = "| Col A | Col B |\n| --- | --- |\n| A1 | B1 |\n"

    html_output = MarkdownToHtmlFragmentWriter.write(markdown_input)

    assert "<table>" in html_output
    assert "<th>Col A</th>" in html_output
    assert "<th>Col B</th>" in html_output
    assert "<td>A1</td>" in html_output
    assert "<td>B1</td>" in html_output


def test_05_writes_mermaid_fence_as_mermaid_pre_block():
    markdown_input = "```mermaid\ngraph TD\n  A-->B\n```\n"

    html_output = MarkdownToHtmlFragmentWriter.write(markdown_input)

    assert html_output == (
        '<pre class="mermaid">graph TD\n  A--&gt;B\n</pre>\n'
    )


def test_06_writes_regular_fence_as_code_block():
    markdown_input = "```python\nprint(1)\n```\n"

    html_output = MarkdownToHtmlFragmentWriter.write(markdown_input)

    assert html_output == (
        '<pre><code class="language-python">print(1)\n</code></pre>\n'
    )


def test_07_renders_anchor_link_as_raw_html_not_escaped():
    markdown_input = MarkdownToHtmlFragmentWriter.write_anchor_link(
        "Title",
        "foo.bar",
    )

    html_output = MarkdownToHtmlFragmentWriter.write(markdown_input)

    assert html_output == '<p><a href="foo.bar">🔗\u00a0Title</a></p>\n'
