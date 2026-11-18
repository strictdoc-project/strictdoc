"""
@relation(SDOC-SRS-61, scope=file)
"""

from strictdoc.helpers.text_width import double_width_ranges
from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.table_editor import TableEditor
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

RST_ALIGNED_TABLE = (
    "+------+-------+\n"
    "| Name | Value |\n"
    "+======+=======+\n"
    "| 中文 | x     |\n"
    "+------+-------+\n"
    "| 😀   | y     |\n"
    "+------+-------+\n"
)

MARKDOWN_ALIGNED_TABLE = (
    "| Name | Value |\n| ---- | ----- |\n| 中文 | x     |\n| 😀   | y     |\n"
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

            # The server writes the double-width ranges of its Python into
            # the page, and the table editor reads them from there.
            page_ranges = self.execute_script(
                "return JSON.parse(document.getElementById("
                "'table-editor-double-width-ranges').textContent);"
            )
            assert [tuple(range_) for range_ in page_ranges] == (
                double_width_ranges()
            )

            # In docutils, a CJK character and an emoji take the width of two
            # characters each. The editor measures the table in the same way,
            # so the table is aligned.
            table_editor.do_place_caret_after("| x")
            table_editor.assert_extra_button_hidden()

            # A typed space misaligns a row. The Format table button aligns
            # the table with the same text width, so docutils accepts the
            # table.
            table_editor.do_type_at_caret(" ")
            table_editor.do_place_caret_after("| y")
            table_editor.assert_extra_button("Format table")
            table_editor.do_click_extra_button()
            table_editor.assert_field_text("Paragraph.\n\n" + RST_ALIGNED_TABLE)
            table_editor.assert_extra_button_hidden()

            form.do_form_submit()
            screen_document.assert_text("Requirement title")

            #
            # Markdown.
            #
            self.open(test_server.get_host_and_port())
            screen_document = screen_project_index.do_click_on_the_document(1)
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Markdown")
            form = screen_document.get_node().do_open_form_edit_requirement()
            form.assert_on_form()

            # A Markdown table uses the same text width as an RST table.
            table_editor.do_place_caret_after("| x")
            table_editor.assert_extra_button_hidden()

            table_editor.do_type_at_caret(" ")
            table_editor.do_place_caret_after("| y")
            table_editor.assert_extra_button("Format table")
            table_editor.do_click_extra_button()
            table_editor.assert_field_text(
                "Paragraph.\n\n" + MARKDOWN_ALIGNED_TABLE
            )
            table_editor.assert_extra_button_hidden()

            form.do_form_submit()
            screen_document.assert_text("Markdown requirement")

        assert test_setup.compare_sandbox_and_expected_output()
