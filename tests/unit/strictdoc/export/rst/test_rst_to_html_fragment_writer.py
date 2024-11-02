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

    project_config = ProjectConfig.default_config(environment=environment)
    html_output = RstToHtmlFragmentWriter(
        context_document=None, project_config=project_config
    ).write(rst_input)
    assert '<table border="1"' in html_output


def test_02():
    rst_input = """\
- First item is a bullet point.
""".lstrip()

    project_config = ProjectConfig.default_config(environment=environment)
    html_output = RstToHtmlFragmentWriter(
        context_document=None, project_config=project_config
    ).write(rst_input)
    assert "<li>First item is a bullet point.</li>" in html_output


def test_with_validation_01_tables():
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

    project_config = ProjectConfig.default_config(environment=environment)
    html_output, _ = RstToHtmlFragmentWriter(
        context_document=None, project_config=project_config
    ).write_with_validation(rst_input)
    assert '<table border="1"' in html_output


def test_with_validation_02_warning_message():
    rst_input = """
- Broken RST markup

  - AAA
  ---
""".lstrip()

    project_config = ProjectConfig.default_config(environment=environment)
    html_output, error = RstToHtmlFragmentWriter(
        context_document=None, project_config=project_config
    ).write_with_validation(rst_input)
    assert html_output is None
    assert error == (
        "RST markup syntax error on line 4: "
        "Bullet list ends without a blank line; unexpected unindent."
    )


def test_with_validation_03_severe_errors():
    rst_input = """
This is an **introduction**.

Hello. What nex?
- dfasdf

  - a sdfasdfasdf
  ----
""".lstrip()

    project_config = ProjectConfig.default_config(environment=environment)
    html_output, error = RstToHtmlFragmentWriter(
        context_document=None, project_config=project_config
    ).write_with_validation(rst_input)
    assert html_output is None
    assert error == (
        "RST markup syntax error on line 7: "
        "Unexpected section title or transition."
    )
