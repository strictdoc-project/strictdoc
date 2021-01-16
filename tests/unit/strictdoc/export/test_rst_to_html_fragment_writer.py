import os

from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)

FIXTURES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)


def test_01():
    rst_input = """
.. list-table:: Title
   :widths: 25 25 50
   :header-rows: 1

   * - Heading row 1, column 1
     - Heading row 1, column 2
     - Heading row 1, column 3
   * - Row 1, column 1
     -
     - Row 1, column 3
   * - Row 2, column 1
     - Row 2, column 2
     - Row 2, column 3
""".lstrip()

    html_output = RstToHtmlFragmentWriter.write(rst_input)
    assert '<table border="1" class="colwidths-given docutils">' in html_output
