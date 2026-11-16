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
            table_editor.do_place_caret_after("| 1")
            table_editor.do_open_edit()

            # The paste into a cell is one undo step, and the typing before
            # it can still be undone.
            table_editor.do_place_caret_at_cell_end(1, 0)
            table_editor.do_type_at_caret("x")
            table_editor.do_paste_in_cell(1, 0, "yz")
            table_editor.assert_cell(1, 0, "1xyz")

            table_editor.do_undo()
            table_editor.assert_cell(1, 0, "1x")
            table_editor.do_undo()
            table_editor.assert_cell(1, 0, "1")
            table_editor.do_redo()
            table_editor.assert_cell(1, 0, "1x")
            table_editor.do_redo()
            table_editor.assert_cell(1, 0, "1xyz")

            # The table model gets the text after undo and redo too.
            table_editor.do_apply()
            form.do_form_submit()
            screen_document.assert_text("1xyz")

        assert test_setup.compare_sandbox_and_expected_output()
