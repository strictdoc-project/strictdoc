from strictdoc.helpers.html import prettify_html_fragment


def test_01():
    # Line also contains trailing whitespace
    node = """<content>


    Text outside tag <div>Text <em>inside</em> tag</div>
    
    </content>
    """.rstrip()  # noqa: W293

    expected_pretty_html = """
<content>
  Text outside tag
  <div>
    Text
    <em>
      inside
    </em>
    tag
  </div>
</content>
    """.strip()

    prettified_html = prettify_html_fragment(node)

    assert prettified_html == expected_pretty_html
