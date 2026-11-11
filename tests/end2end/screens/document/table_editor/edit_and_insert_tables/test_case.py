"""
@relation(SDOC-SRS-61, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.table_editor import TableEditor
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

# RST: the editable table is indented under a ".. table::" directive and has
# a "|" inside a cell and a cell with two paragraphs. The second table has a
# column span, which the editor does not support: it stays not editable.
#
# Markdown: the table has column alignment, an escaped "\|" and a "<br/>"
# inside cells. The table-like lines in the fenced code block are code.

RST_FIELD_TEXT = (
    "Paragraph.\n"
    "\n"
    ".. table:: Caption\n"
    "\n"
    "   +-----+-------+\n"
    "   | Key | Value |\n"
    "   +=====+=======+\n"
    "   | a   | x | y |\n"
    "   +-----+-------+\n"
    "   | b   | 2     |\n"
    "   |     |       |\n"
    "   |     | more  |\n"
    "   +-----+-------+\n"
    "\n"
    "+-----+-----+\n"
    "| A   | B   |\n"
    "+=====+=====+\n"
    "| spanned   |\n"
    "+-----+-----+\n"
)


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            #
            # RST.
            #
            screen_project_index = Screen_ProjectIndex(self)
            # The project tree lists the documents by file name.
            screen_document = screen_project_index.do_click_on_the_document(2)
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("RST")
            form = screen_document.get_node().do_open_form_edit_requirement()
            form.assert_on_form()

            table_editor = TableEditor(self, "STATEMENT")
            table_editor.assert_highlighted_tables(1)

            table_editor.do_place_caret_after("spanned")
            table_editor.assert_button_hidden()

            # Cancel leaves the field as it was.
            table_editor.do_place_caret_after("Paragraph.")
            table_editor.do_open_insert()
            table_editor.assert_cell(2, 2, "")
            table_editor.do_click_extend("row")
            table_editor.assert_cell(3, 0, "")
            table_editor.do_fill_cell(0, 0, "Discarded")
            table_editor.do_cancel()
            table_editor.assert_field_text(RST_FIELD_TEXT)

            # Typing in the table misaligns its row; it stays editable.
            table_editor.do_place_caret_after("Value")
            table_editor.do_type_at_caret("s")
            table_editor.assert_button_hidden()
            table_editor.assert_highlighted_tables(1)

            table_editor.do_place_caret_after("x | y")
            table_editor.do_open_edit()
            table_editor.assert_cell(0, 1, "Values")
            table_editor.assert_cell(1, 1, "x | y")
            table_editor.assert_cell(2, 1, "2\n\nmore")
            table_editor.do_fill_cell(1, 0, "alpha\n\nbeta")
            table_editor.do_insert_column(1)
            table_editor.do_fill_cell(0, 1, "New")
            table_editor.do_delete_row(2)
            table_editor.do_apply()

            # The header stays empty: the table is written without one.
            table_editor.do_place_caret_after("Paragraph.")
            table_editor.do_open_insert()
            table_editor.do_fill_cell(1, 0, "first")
            table_editor.do_fill_cell(2, 1, "second")
            # Removing columns stops at the first one with content.
            table_editor.do_drag_extend("column", -2)
            table_editor.do_apply()

            table_editor.assert_field_text(
                "Paragraph.\n"
                "\n"
                "+-------+--------+\n"
                "| first |        |\n"
                "+-------+--------+\n"
                "|       | second |\n"
                "+-------+--------+\n"
                "\n"
                ".. table:: Caption\n"
                "\n"
                "   +-------+-----+--------+\n"
                "   | Key   | New | Values |\n"
                "   +=======+=====+========+\n"
                "   | alpha |     | x | y  |\n"
                "   |       |     |        |\n"
                "   | beta  |     |        |\n"
                "   +-------+-----+--------+\n"
                "\n"
                "+-----+-----+\n"
                "| A   | B   |\n"
                "+=====+=====+\n"
                "| spanned   |\n"
                "+-----+-----+\n"
            )
            table_editor.assert_highlighted_tables(2)

            form.do_form_submit()
            screen_document.assert_text("second")

            #
            # Markdown.
            #
            self.open(test_server.get_host_and_port())
            screen_document = screen_project_index.do_click_on_the_document(1)
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Markdown")
            form = screen_document.get_node().do_open_form_edit_requirement()
            form.assert_on_form()

            table_editor.assert_highlighted_tables(1)

            table_editor.do_place_caret_after("| not")
            table_editor.assert_button("insert")

            table_editor.do_place_caret_after("| and")
            table_editor.do_open_edit()
            table_editor.assert_cell(1, 1, "`a | b`")
            table_editor.assert_cell(2, 1, "`a & b`\nboth")
            table_editor.do_fill_cell(2, 0, "and\nalso")
            table_editor.do_menu_action("row", 2, "insert-below")
            table_editor.do_fill_cell(3, 0, "xor")
            table_editor.do_fill_cell(3, 1, "`a ^ b`")
            # A new column keeps its empty header cell.
            table_editor.do_insert_column(2)
            # The alignment moves with its column.
            table_editor.do_drag_column(1, before=0)
            table_editor.do_drag_row(3, before=1)
            table_editor.do_apply()

            table_editor.assert_field_text(
                "| Pattern         | Name        |     |\n"
                "| --------------: | :---------- | --- |\n"
                "| `a ^ b`         | xor         |     |\n"
                "| `a \\| b`        | or          |     |\n"
                "| `a & b`<br>both | and<br>also |     |\n"
                "\n"
                "```text\n"
                "| not | a table |\n"
                "| --- | ------- |\n"
                "```\n"
            )

            form.do_form_submit()
            screen_document.assert_text("also")

        assert test_setup.compare_sandbox_and_expected_output()
