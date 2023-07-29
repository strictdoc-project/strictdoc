import os

from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)

FIXTURES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)


def test_01():
    rst_input = """\
:rawhtml:`<a href="foo.bar">LINK</a>`\
"""

    html_output = RstToHtmlFragmentWriter(
        path_to_output_dir="NOT_RELEVANT", context_document=None
    ).write(rst_input)
    assert (
        html_output
        == """\
<div class="document">
<p><a href="foo.bar">LINK</a></p>
</div>
"""
    )
