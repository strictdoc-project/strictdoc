from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.form.form import Form
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
            assert node_mid is not None

            form = Form(self)

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            #
            # Case 1: None → text.
            # Adding a TITLE assigns the node a level and adds it to the TOC.
            #
            screen_table.assert_cell_dom_text(node_mid, "LEVEL", "")
            screen_table.assert_toc_contains_not("First title")

            screen_table.do_open_inline_cell(node_mid, "TITLE")
            form.do_fill_in("TITLE", "First title")
            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_dom_text(node_mid, "LEVEL", "1")

            screen_table.assert_cell_dom_text(node_mid, "LEVEL", "1")
            screen_table.assert_toc_contains("First title")

            #
            # Case 2: text → other text.
            # Renaming a TITLE keeps the level intact and updates the TOC entry.
            #
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            form.do_fill_in("TITLE", "Second title")
            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_dom_text(node_mid, "LEVEL", "1")

            screen_table.assert_cell_dom_text(node_mid, "LEVEL", "1")
            screen_table.assert_toc_contains_not("First title")
            screen_table.assert_toc_contains("Second title")

            #
            # Case 3: text → None.
            # Removing a TITLE clears the level and drops the TOC entry.
            #
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            form.do_clear_field("TITLE")
            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_dom_text(node_mid, "LEVEL", "")

            screen_table.assert_cell_dom_text(node_mid, "LEVEL", "")
            screen_table.assert_toc_contains_not("Second title")

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
