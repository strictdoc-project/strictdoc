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
    assert '<table border="1"' in html_output


def test_02_parsing_with_validation():
    rst_input = """
- Broken RST markup

  - AAA
  ---
""".lstrip()

    html_output, error = RstToHtmlFragmentWriter.write_with_validation(
        rst_input
    )
    assert html_output is None
    assert error == (
        "RST markup syntax error on line 4: "
        "Bullet list ends without a blank line; unexpected unindent."
    )
