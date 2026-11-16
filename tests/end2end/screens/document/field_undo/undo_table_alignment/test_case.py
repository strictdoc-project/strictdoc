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

            # Two edits are two undo steps: the caret moves between them.
            table_editor.do_place_caret_after("| 1")
            table_editor.do_type_at_caret("x")
            first_typed = text.replace("| 1 ", "| 1x ", 1)
            table_editor.assert_field_text(first_typed)
            table_editor.do_place_caret_after("| 2")
            table_editor.do_type_at_caret("y")
            typed = first_typed.replace("| 2 ", "| 2y ", 1)
            table_editor.assert_field_text(typed)

            # The table is aligned when the caret leaves it.
            table_editor.do_place_caret_after("Paragraph.")
            aligned = typed.replace(
                "+---+----+\n| a | bb |\n+---+----+\n| 1x | 2y  |\n+---+----+",
                "+----+----+\n| a  | bb |\n+----+----+\n| 1x | 2y |\n+----+----+",
            )
            assert aligned != typed
            table_editor.wait_for_field_text(aligned)

            # One Ctrl+Z undoes the alignment and the edit before it, one
            # Ctrl+Shift+Z redoes both.
            table_editor.do_undo()
            table_editor.wait_for_field_text(first_typed)
            table_editor.do_redo()
            table_editor.wait_for_field_text(aligned)

            # After the undo, the table is aligned again when the caret
            # leaves it.
            table_editor.do_undo()
            table_editor.wait_for_field_text(first_typed)
            table_editor.do_place_caret_after("Paragraph.")
            table_editor.wait_for_field_text(
                first_typed.replace(
                    "+---+----+\n| a | bb |\n+---+----+\n| 1x | 2  |\n+---+----+",
                    "+----+----+\n| a  | bb |\n+----+----+\n| 1x | 2  |\n+----+----+",
                )
            )

            form.do_form_submit()
            screen_document.assert_text("Paragraph.")

        assert test_setup.compare_sandbox_and_expected_output()
