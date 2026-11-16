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


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()
            form = screen_document.get_node().do_open_form_edit_requirement()
            form.assert_on_form()

            table_editor = TableEditor(self, "STATEMENT")
            table_editor.assert_highlighted_tables(0)

            # A pasted table is recognized at once, without another edit of
            # the field.
            table_editor.do_place_caret_on_next_line("Paragraph.")
            table_editor.do_paste_at_caret(
                "\n+-----+-----+\n| a   | b   |\n+-----+-----+\n"
            )
            table_editor.wait_for_highlighted_tables(1)
            table_editor.do_place_caret_after("| a")
            table_editor.assert_button("edit")

            # The hidden field gets the pasted text, so the form saves it.
            form.do_form_submit()
            screen_document.assert_text("Last paragraph.")

        assert test_setup.compare_sandbox_and_expected_output()
