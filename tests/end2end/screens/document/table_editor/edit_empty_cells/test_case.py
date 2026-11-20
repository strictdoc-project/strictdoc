"""
@relation(SDOC-SRS-61, scope=file)
"""

from selenium.webdriver.common.keys import Keys

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
            screen_document = screen_project_index.do_click_on_the_document(1)
            form = screen_document.get_node().do_open_form_edit_requirement()
            table_editor = TableEditor(self, "STATEMENT")

            table_editor.assert_highlighted_tables(2)

            table_editor.do_place_caret_after("123")
            table_editor.do_open_edit()
            table_editor.do_place_caret_at_cell_end(2, 2)
            table_editor.do_type_at_caret(Keys.BACKSPACE * 3)
            table_editor.do_apply()
            table_editor.assert_highlighted_tables(2)

            table_editor.do_place_caret_after("one")
            table_editor.do_open_edit()
            table_editor.do_click_extend("row")
            table_editor.assert_cell(1, 0, "")
            table_editor.assert_cell(1, 1, "")
            table_editor.do_apply()

            form.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
