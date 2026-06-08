from strictdoc.helpers.mid import MID
from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.form.form import Form
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
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
            form_requirement = Form_EditRequirement(self)

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            # Delay handling of the response so the second keyboard shortcut
            # runs while the first request is still in flight.
            self.execute_script(
                """
                window.tableUpdatePostCount = 0;
                const originalFetch = window.fetch.bind(window);
                window.fetch = function (...args) {
                    const [url, options = {}] = args;
                    const responsePromise = originalFetch(...args);
                    if (
                        url.includes("/actions/table/update_node") &&
                        options.method === "POST"
                    ) {
                        window.tableUpdatePostCount += 1;
                        return responsePromise.then(
                            response => new Promise(
                                resolve => setTimeout(
                                    () => resolve(response),
                                    250
                                )
                            )
                        );
                    }
                    return responsePromise;
                };
                """
            )

            #
            # Case 1: Open STATEMENT inline, type new value, save by Cmd/Ctrl+Enter — cell updates.
            #
            screen_table.do_open_inline_cell(node_mid, "STATEMENT")
            form.do_fill_in("STATEMENT", "New statement.")
            screen_table.do_save_inline_cell_by_cmd_enter()
            # Trigger save again while the first request is still in flight.
            screen_table.do_save_inline_cell_by_cmd_enter()
            self.sleep(0.5)

            screen_table.assert_cell_dom_text(
                node_mid, "STATEMENT", "New statement."
            )
            assert (
                self.execute_script("return window.tableUpdatePostCount") == 1
            )

            #
            # Case 2: Open COMMENT inline, type new value, save by Cmd/Ctrl+Enter — cell updates.
            #
            screen_table.do_open_inline_cell(node_mid, "COMMENT")
            comment_mid = MID(screen_table.get_comment_row_mid(order=1))
            form_requirement.do_fill_in_field_comment(
                comment_mid, "New comment."
            )
            screen_table.do_save_inline_cell_by_cmd_enter()
            self.sleep(0.5)

            self.assert_text("New comment.")
            assert (
                self.execute_script("return window.tableUpdatePostCount") == 2
            )

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
