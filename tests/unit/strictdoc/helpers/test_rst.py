from strictdoc.helpers.rst import truncated_statement_with_no_rst


def test_01_when_text_with_multiple_paragraphs_takes_first_paragraph():
    input_string = """
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren.

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren.

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren.
""".strip()  # noqa: E501

    truncated_string = truncated_statement_with_no_rst(input_string)
    assert truncated_string == (
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed "
        "diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam "
        "erat, sed diam voluptua. At vero eos et accusam et justo duo dolores "
        "et ea rebum. Stet clita kasd gubergren. <...>"
    )


def test_02_when_text_starts_with_rst_directive_truncates_to_dots():
    input_string = """
.. list-table:: Table Example
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
""".strip()

    truncated_string = truncated_statement_with_no_rst(input_string)
    assert truncated_string == "<...>"
