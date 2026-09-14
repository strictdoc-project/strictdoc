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
            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            self.clear_local_storage()

            screen_table = ViewType_Selector(self).do_go_to_table()
            screen_table.assert_on_screen_table()
            node_mid = screen_table.get_node_mid_from_row(row_order=1)
            assert node_mid is not None

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            # Reject the first save after the user selects Active. The failed
            # request must leave the autocomplete input open with Active still
            # available for a retry.
            self.execute_script(
                """
                const originalFetch = window.fetch;
                window.fetch = function(input, init) {
                    if (
                        String(input).includes(
                            '/actions/table/update_node_field'
                        )
                        && init?.method === 'POST'
                    ) {
                        window.fetch = originalFetch;
                        return Promise.reject(new TypeError('Network error'));
                    }
                    return originalFetch(input, init);
                };
                """
            )
            screen_table.do_cell_autocomplete(node_mid, "STATUS", "act")
            screen_table.do_submit_cell_autocomplete()
            error = '[data-testid="table-inline-field-error"]'
            self.assert_exact_text("Unable to save this field.", error)

            # Pause the retry when the browser calls fetch. Reopen the same cell
            # and press Escape before the request reaches the server. Escape
            # first restores the old empty display. After release, the server
            # accepts Active. The successful response must replace the empty
            # display without reopening the editor.
            blocked_retry = BlockedTableFetch(
                self,
                "/actions/table/update_node_field",
                "field_value=Active",
            )
            self.click(f"#cell-{node_mid}-STATUS")
            screen_table.do_submit_cell_autocomplete()
            blocked_retry.wait_until_requested()

            self.click(f"#cell-{node_mid}-STATUS")
            screen_table.do_cancel_inline_cell_by_escape()
            screen_table.assert_cell_dom_text(node_mid, "STATUS", "")

            blocked_retry.release()
            blocked_retry.restore()
            screen_table.wait_for_cell_save_applied(node_mid, "STATUS")
            screen_table.assert_cell_dom_text(node_mid, "STATUS", "Active")

        assert test_setup.compare_sandbox_and_expected_output()
