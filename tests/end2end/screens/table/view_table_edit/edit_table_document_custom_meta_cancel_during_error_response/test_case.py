from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.screens.table.view_table_edit.race_helpers import (
    BlockedTableFetch,
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
            screen_project_index.do_click_on_first_document()

            self.clear_local_storage()

            screen_table = ViewType_Selector(self).do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.do_toggle_edit_mode()

            row = '[data-testid="document-config-metadata-row-custom_meta_0"]'
            field = f'{row} [data-testid="document-config-metadata-field"]'
            editor = '[data-testid="form-field-metadata-custom_meta_0"]'
            error = (
                '[data-testid="document-config-metadata-error-custom_meta_0"]'
            )

            # Pause the invalid save when the browser calls fetch. The user
            # cancels the cell before the request reaches the server. After
            # release, the validation error belongs to the closed input. The
            # error must not reopen the cell or replace its displayed value.
            blocked_validation = BlockedTableFetch(
                self,
                "/actions/table/update_document_custom_meta",
                "active_field_name=value",
            )
            self.click(field)
            self.type(editor, "1")
            self.find_element(editor).send_keys(Keys.BACKSPACE)
            screen_table.do_save_inline_cell_by_outside_click()
            blocked_validation.wait_until_requested()

            self.click(field)
            screen_table.do_cancel_inline_cell_by_escape()
            blocked_validation.release()
            blocked_validation.restore()

            self.assert_element_not_present(editor)
            self.assert_element_not_present(error)
            self.assert_text("First value", selector=row)

            # Pause another save after the browser calls fetch. The user cancels
            # the cell before the test rejects the held fetch. The network
            # failure belongs to the closed input. The failure must not add an
            # error or reopen the cell after cancellation.
            blocked_network = BlockedTableFetch(
                self,
                "/actions/table/update_document_custom_meta",
                "active_field_name=value",
            )
            self.click(field)
            self.type(editor, "Unsaved value")
            screen_table.do_save_inline_cell_by_outside_click()
            blocked_network.wait_until_requested()

            self.click(field)
            screen_table.do_cancel_inline_cell_by_escape()
            blocked_network.reject()
            blocked_network.restore()

            self.assert_element_not_present(editor)
            self.assert_element_not_present(error)
            self.assert_text("First value", selector=row)

        assert test_setup.compare_sandbox_and_expected_output()
