"""
@relation(SDOC-SRS-211, scope=file)
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
            text = table_editor.get_field_text()

            # A widget write is one undo step after the typing before it:
            # Ctrl+Z undoes the Format table write, then the typing, and
            # Ctrl+Shift+Z redoes them in the same steps.
            table_editor.do_place_caret_after("| 1")
            table_editor.do_type_at_caret("x")
            typed = text.replace("| 1 ", "| 1x ", 1)
            table_editor.assert_field_text(typed)
            # Typing hides the buttons until the caret moves.
            table_editor.do_place_caret_after("| a")
            table_editor.assert_extra_button("Format table")
            table_editor.do_click_extra_button()
            formatted = table_editor.get_field_text()
            assert formatted != typed

            table_editor.do_undo()
            table_editor.wait_for_field_text(typed)
            table_editor.do_undo()
            table_editor.wait_for_field_text(text)
            table_editor.do_redo()
            table_editor.wait_for_field_text(typed)
            table_editor.do_redo()
            table_editor.wait_for_field_text(formatted)

            # The form sends the text after undo and redo.
            form.do_form_submit()
            screen_document.assert_text("Paragraph.")

        assert test_setup.compare_sandbox_and_expected_output()
