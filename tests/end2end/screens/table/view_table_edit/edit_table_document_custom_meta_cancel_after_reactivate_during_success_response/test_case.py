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

            row = '[data-testid="document-config-metadata-row-custom_meta_1"]'
            field = f'{row} [data-testid="document-config-metadata-field"]'
            editor = '[data-testid="form-field-metadata-custom_meta_1"]'

            # A value accepted by the server must appear after the user reopens
            # and then cancels the same cell. Pause the save when the browser
            # calls fetch with New value. The user reopens the cell and presses
            # Escape before the request reaches the server. Escape first
            # restores Second value. After release, the successful save must
            # display New value without reopening the editor.
            blocked_fetch = BlockedTableFetch(
                self,
                "/actions/table/update_document_custom_meta",
                "active_field_name=value",
            )

            self.click(field)
            self.type(editor, "New value")
            screen_table.do_save_inline_cell_by_outside_click()
            blocked_fetch.wait_until_requested()

            self.click(field)
            screen_table.do_cancel_inline_cell_by_escape()

            self.assert_text("Second value", selector=row)
            assert self.get_attribute(field, "data-mode", hard_fail=False) != (
                "editing"
            )

            blocked_fetch.release()
            blocked_fetch.restore()

            self.assert_text("New value", selector=row)
            assert self.get_attribute(field, "data-mode", hard_fail=False) != (
                "editing"
            )

        assert test_setup.compare_sandbox_and_expected_output()
