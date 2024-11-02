import os

from strictdoc import environment
from strictdoc.core.project_config import ProjectConfig
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

    project_config = ProjectConfig.default_config(environment=environment)
    html_output = RstToHtmlFragmentWriter(
        project_config=project_config, context_document=None
    ).write(rst_input, use_cache=False)
    assert (
        html_output
        == """\
<div class="document">
<p><a href="foo.bar">LINK</a></p>
</div>
"""
    )
