from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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

            field_xpath = "(//*[@data-testid='form-field-TITLE'])[1]"

            #
            # Case 1: Enter key is blocked in TITLE (singleline field).
            # Pressing Enter must not insert a newline — value is saved on one line.
            #
            # Root cause: editable_field_controller.js checked `data-editable`
            # instead of `data-field-type`, so `isSingle` was always false and
            # the Enter keydown handler never registered. In this scenario,
            # pressing Enter inserts \n into the contenteditable, which reaches
            # the server and either causes a 422 (RST validation) or corrupts
            # the .sdoc file (parser fails on next load).
            #
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            form.do_fill_in("TITLE", "New title")
            self.find_element(field_xpath, by=By.XPATH).send_keys(
                Keys.RETURN + " extra"
            )
            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_save_applied(node_mid, "TITLE")

            screen_table.assert_cell_has_no_validation_error(node_mid, "TITLE")
            screen_table.assert_cell_dom_text(
                node_mid, "TITLE", "New title extra"
            )

            #
            # Case 2: Paste text containing newlines into TITLE.
            # Newlines must be replaced with spaces — value is saved on one line without error.
            #
            # The paste handler in editable_field_controller.js calls filterSingleLine
            # only when isSingle is true. Without the fix (isSingle always false),
            # pasted \n characters bypassed filtering, reached the server,
            # and caused the same 422 / file corruption as Case 1.
            #
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            field_element = self.find_element(field_xpath, by=By.XPATH)
            # filterSingleLine replaces each \n with a space and collapses
            # consecutive whitespace, so "Pasted\nwith\nnewlines" → "Pasted with newlines".
            self.do_paste_text_via_js(field_element, "Pasted\nwith\nnewlines")
            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_save_applied(node_mid, "TITLE")

            screen_table.assert_cell_has_no_validation_error(node_mid, "TITLE")
            screen_table.assert_cell_dom_text(
                node_mid, "TITLE", "Pasted with newlines"
            )

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
