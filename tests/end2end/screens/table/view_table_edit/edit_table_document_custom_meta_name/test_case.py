from selenium.webdriver.common.keys import Keys

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
            screen_project_index.do_click_on_first_document()

            self.clear_local_storage()

            screen_table = ViewType_Selector(self).do_go_to_table()
            screen_table.assert_on_screen_table()

            row = '[data-testid="document-config-metadata-row-custom_meta_0"]'
            label = f'{row} [data-testid="document-config-metadata-label"]'
            editor = '[data-testid="form-field-metadata-name-custom_meta_0"]'
            error = (
                '[data-testid="document-config-metadata-error-custom_meta_0"]'
            )

            self.click(label)
            assert (
                self.find_element(label).get_attribute("data-mode") or ""
            ) != "editing"

            screen_table.do_toggle_edit_mode()

            self.click(label)
            self.wait_for_element(editor)
            self.type(editor, "CANCELLED")
            screen_table.do_cancel_inline_cell_by_escape()
            self.assert_exact_text("FIRST:", label)

            self.click(label)
            self.type(editor, "1")
            self.find_element(editor).send_keys(Keys.BACKSPACE)
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            self.assert_exact_text("Key must not be empty.", error)
            assert self.get_attribute(editor, "errors") == "true"
            self.assert_text("First value", selector=row)

            self.click(label)
            self.type(editor, "RENAMED_FIRST")
            screen_table.do_save_inline_cell_by_cmd_enter()
            self.sleep(0.5)

            self.assert_exact_text("RENAMED_FIRST:", label)
            self.assert_text("First value", selector=row)
            self.assert_element_not_present(error)
            assert (
                self.get_attribute(
                    f'{row} input[name="metadata[custom_meta_0][name]"]',
                    "value",
                )
                == "RENAMED_FIRST"
            )
            self.assert_exact_text(
                "SECOND:",
                '[data-testid="document-config-metadata-row-custom_meta_1"] '
                '[data-testid="document-config-metadata-label"]',
            )

        assert test_setup.compare_sandbox_and_expected_output()
