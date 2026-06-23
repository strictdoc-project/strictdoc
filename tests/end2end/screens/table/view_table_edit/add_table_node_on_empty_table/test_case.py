from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.confirm import Confirm
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
            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            self.clear_local_storage()

            screen_table = ViewType_Selector(self).do_go_to_table()
            screen_table.assert_on_screen_table()

            # Switch to edit mode: the table-empty placeholder is replaced by
            # the "Add Node" handler; the (still empty) meta fields become
            # visible/editable for integrity.
            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()
            screen_table.assert_not_empty_view("table-empty-placeholder")
            self.assert_element_visible('[data-testid="table-add-node-handle"]')
            self.assert_element_visible(
                '[data-testid="document-config-uid-field"]'
            )

            # Add the first node from the empty table.
            screen_table.do_open_add_node_menu(row_order=1)
            screen_table.do_click_add_node_action(
                element_type="REQUIREMENT",
                whereto="child",
                row_order=1,
            )
            screen_table.wait_for_table_row_count(1)
            assert screen_table.get_table_row_count() == 1
            new_node_mid = screen_table.get_node_mid_from_row(row_order=1)

            # There are now menu rows both before and after the new node.
            add_rows = self.find_elements('[data-testid="table-add-row"]')
            assert len(add_rows) == 2

            # Fill in some meta fields and save.
            uid = '[data-testid="document-config-uid-field"]'
            self.click(uid)
            self.type('[data-testid="form-field-UID"]', "DOC-001")
            screen_table.do_save_inline_cell_by_outside_click()

            version = '[data-testid="document-config-version-field"]'
            self.click(version)
            self.type('[data-testid="form-field-VERSION"]', "1.0")
            screen_table.do_save_inline_cell_by_outside_click()

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

            # No placeholders left: meta content and the added node are present.
            self.assert_text("DOC-001", uid)
            self.assert_text("1.0", version)
            screen_table.assert_not_empty_view("table-empty-placeholder")
            assert screen_table.get_table_row_count() == 1
            assert (
                screen_table.get_node_mid_from_row(row_order=1) == new_node_mid
            )

            # Switch back to edit mode: clear the meta fields and delete the node.
            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            self.click(uid)
            self.type('[data-testid="form-field-UID"]', "X")
            self.find_element('[data-testid="form-field-UID"]').send_keys(
                Keys.BACKSPACE
            )
            screen_table.do_save_inline_cell_by_outside_click()

            self.click(version)
            self.type('[data-testid="form-field-VERSION"]', "X")
            self.find_element('[data-testid="form-field-VERSION"]').send_keys(
                Keys.BACKSPACE
            )
            screen_table.do_save_inline_cell_by_outside_click()

            screen_table.do_click_delete_action(new_node_mid)
            Confirm(self).do_confirm_action()
            screen_table.assert_node_row_not_present(new_node_mid)

            # Back to a single add-row with the "add first node" menu item.
            add_rows = self.find_elements('[data-testid="table-add-row"]')
            assert len(add_rows) == 1
            screen_table.do_open_add_node_menu(row_order=1)
            screen_table.assert_add_node_actions_visible(row_order=1)
            self.assert_element(
                '[data-testid="table-add-node-action-requirement-child"]'
            )
            screen_table.do_close_add_node_menu_by_escape()

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

            # Placeholders are back: no meta in the root (only Title), table
            # shows its empty-state placeholder again.
            self.assert_element_not_visible(uid)
            self.assert_element_not_visible(version)
            screen_table.assert_empty_view("table-empty-placeholder")

        assert test_setup.compare_sandbox_and_expected_output()
