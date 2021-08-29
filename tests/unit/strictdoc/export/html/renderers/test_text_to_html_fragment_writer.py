from strictdoc.export.html.renderers.text_to_html_writer import TextToHtmlWriter


def test_01_escapes_html_tags():
    text_input = """
<a href="url">link</a>
""".strip()

    html_output = TextToHtmlWriter.write(text_input)
    assert "&lt;a href=&quot;url&quot;&gt;link&lt;/a&gt;" == html_output


def test_02_replaces_newlines_with_br():
    text_input = """
Line1
Line2
""".lstrip()

    html_output = TextToHtmlWriter.write(text_input)
    assert "Line1<br/>\nLine2<br/>\n" == html_output
