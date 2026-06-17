from strictdoc.export.html.renderers.html_fragment_writer import (
    HTMLFragmentWriter,
)


def test_write_anchor_link():
    result = HTMLFragmentWriter.write_anchor_link(
        "REQ-001", "../requirements/REQ-001.html#REQ-001"
    )
    assert (
        result
        == '<a href="../requirements/REQ-001.html#REQ-001">🔗&nbsp;REQ-001</a>'
    )
