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

TABLE = "+---+----+\n| a | bb |\n+---+----+\n| 1x | 2  |\n+---+----+"
ALIGNED_TABLE = (
    "+----+----+\n| a  | bb |\n+----+----+\n| 1x | 2  |\n+----+----+"
)


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

            table_editor.do_place_caret_after("| 1")
            table_editor.do_type_at_caret("x")
            typed = text.replace("| 1 ", "| 1x ", 1)
            assert TABLE in typed
            table_editor.assert_field_text(typed)

            # The table is aligned when the caret leaves it. The alignment
            # is an undo step of its own.
            table_editor.do_place_caret_after("Paragraph.")
            aligned = typed.replace(TABLE, ALIGNED_TABLE)
            table_editor.wait_for_field_text(aligned)

            table_editor.do_undo()
            table_editor.wait_for_field_text(typed)
            table_editor.do_undo()
            table_editor.wait_for_field_text(text)
            table_editor.do_redo()
            table_editor.wait_for_field_text(typed)
            table_editor.do_redo()
            table_editor.wait_for_field_text(aligned)

            # RST rejects a misaligned table. After the undo of the
            # alignment, the table is aligned again when the form is sent,
            # also if the caret was outside the table on Ctrl+Z.
            table_editor.do_place_caret_after("Paragraph.")
            table_editor.do_undo()
            table_editor.wait_for_field_text(typed)
            form.do_form_submit()
            screen_document.assert_text("Paragraph.")

        assert test_setup.compare_sandbox_and_expected_output()
