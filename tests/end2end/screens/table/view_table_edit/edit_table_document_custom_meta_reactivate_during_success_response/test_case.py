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

            # A successful save for an older value must not close a reopened
            # editor or replace newer input. Pause the save when the browser
            # calls fetch with New value. The user reopens the same cell and
            # enters Reactivated value before the request reaches the server.
            # After release, the success must keep that input visible. Escape
            # must then restore New value because the server accepted it.
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
            self.type(editor, "Reactivated value")

            blocked_fetch.release()
            blocked_fetch.restore()

            assert self.get_attribute(field, "data-mode") == "editing"
            assert self.get_text(editor) == "Reactivated value"

            screen_table.do_cancel_inline_cell_by_escape()
            self.assert_text("New value", selector=row)

            # A normal save must apply its response without waiting for Turbo's
            # animation-frame callback. Disable requestAnimationFrame, save the
            # newer value again, and require the editor to close. The test fails
            # if table editing still delegates the DOM update to Turbo's
            # deferred rendering path.
            self.execute_script(
                """
                window.__originalRAF = window.requestAnimationFrame;
                window.requestAnimationFrame = function () { return 1; };
                """
            )
            try:
                self.click(field)
                self.type(editor, "Reactivated value")
                screen_table.do_save_inline_cell_by_outside_click()
                self.assert_element_not_present(editor)
                self.assert_text("Reactivated value", selector=row)
            finally:
                self.execute_script(
                    "window.requestAnimationFrame = window.__originalRAF;"
                )

        assert test_setup.compare_sandbox_and_expected_output()
