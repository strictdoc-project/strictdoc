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
            # Case 1: Edit mode is off by default — clicking a cell does NOT open input.
            #
            screen_table.assert_edit_mode_off()
            screen_table.assert_no_edit_input(node_mid, "TITLE")
            screen_table.do_click_cell(node_mid, "TITLE")
            screen_table.assert_no_edit_input(node_mid, "TITLE")

            #
            # Case 2: Enable edit mode, then Cancel (Escape) — value and file unchanged.
            #
            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            screen_table.assert_cell_value(node_mid, "TITLE", "Old title")
            screen_table.do_edit_cell_and_cancel(
                node_mid, "TITLE", "Cancelled title"
            )
            # Value is restored to original.
            screen_table.assert_cell_value(node_mid, "TITLE", "Old title")

            #
            # Case 3: Open input, change nothing, submit — no server request, value unchanged.
            #
            screen_table.do_click_cell(node_mid, "TITLE")
            screen_table.assert_edit_input_visible(node_mid, "TITLE")
            # Submit without changing value (input already has "Old title").
            screen_table.do_submit_cell_unchanged(node_mid, "TITLE")
            screen_table.assert_cell_value(node_mid, "TITLE", "Old title")

            #
            # Case 4: Edit and submit with Enter — value updates on page immediately.
            #
            screen_table.do_edit_cell_and_submit(node_mid, "TITLE", "New title")
            self.sleep(0.5)
            # data-current-value attribute updated.
            screen_table.assert_cell_value(node_mid, "TITLE", "New title")
            # Visible text in the cell updated via Turbo.
            screen_table.assert_cell_dom_text(node_mid, "TITLE", "New title")

            # Disable edit mode.
            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
