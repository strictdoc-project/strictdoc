from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
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
            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document")

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            node_mid = screen_table.get_node_mid_from_row(row_order=1)
            assert node_mid is not None, "Could not find node MID in table row"

            #
            # Case 1: Edit mode is off — clicking a multiline cell does NOT open popup.
            #
            screen_table.assert_edit_mode_off()
            screen_table.assert_no_multiline_popup()
            screen_table.do_click_multiline_cell(node_mid, "STATEMENT")
            screen_table.assert_no_multiline_popup()

            #
            # Case 2: Enable edit mode, click multiline cell — popup opens.
            #
            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            screen_table.do_click_multiline_cell(node_mid, "STATEMENT")
            screen_table.assert_multiline_popup_open()

            #
            # Case 3: Close popup with the Close button.
            #
            screen_table.do_close_multiline_popup_by_btn()
            screen_table.assert_no_multiline_popup()

            #
            # Case 4: Open popup again, close with Escape.
            #
            screen_table.do_click_multiline_cell(node_mid, "STATEMENT")
            screen_table.assert_multiline_popup_open()
            screen_table.do_close_multiline_popup_by_escape()
            screen_table.assert_no_multiline_popup()
