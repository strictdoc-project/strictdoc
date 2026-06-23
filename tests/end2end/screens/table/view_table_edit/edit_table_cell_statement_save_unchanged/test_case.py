from selenium.webdriver.common.by import By

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
            assert node_mid is not None

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            #
            # Open a multiline cell (STATEMENT), make no changes, save by clicking outside.
            # The file must be unchanged — no CR characters (\r) must be introduced.
            #
            # Root cause: table_view_edit.js used `new FormData(form)` as the fetch
            # body, which triggers multipart/form-data encoding. Per spec, multipart
            # encodes textarea newlines as CRLF (\r\n). The server-side sanitizer
            # for multiline fields did not strip \r, so \r was written to the .sdoc
            # file and appeared as ^M in git diffs.
            #
            # Fix: table_view_edit.js now uses `new URLSearchParams(new FormData(form))`
            # (application/x-www-form-urlencoded), which sends \n as %0A — no CRLF.
            # The sanitizer also now normalises \r\n → \n as a server-side safeguard.
            #
            # Without the fix, compare_sandbox_and_expected_output() fails because
            # the saved file contains \r\n while expected_output has \n only.
            #
            screen_table.do_open_inline_cell(node_mid, "STATEMENT")
            # Wait for the async Turbo Stream to inject the inline form.
            self.wait_for_element(
                f"//*[@data-node-mid='{node_mid}']"
                f"[@data-field-name='STATEMENT']//form",
                by=By.XPATH,
                timeout=3,
            )
            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_not_editing(node_mid, "STATEMENT")

            screen_table.assert_cell_has_no_validation_error(
                node_mid, "STATEMENT"
            )

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
