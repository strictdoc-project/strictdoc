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
            screen_table.do_toggle_edit_mode()

            title = '[data-testid="document-title-field"]'
            self.click(title)
            self.type('[data-testid="form-field-TITLE"]', "Cancelled title")
            screen_table.do_cancel_inline_cell_by_escape()
            self.assert_text("Old document title", selector=title)

            self.click(title)
            self.type(
                '[data-testid="form-field-TITLE"]',
                "New document title",
            )
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)
            self.assert_text("New document title", selector=title)

            uid = '[data-testid="document-config-uid-field"]'
            classification = (
                '[data-testid="document-config-classification-field"]'
            )
            self.click(uid)
            self.type('[data-testid="form-field-UID"]', "DOC-002")
            self.click(classification)
            self.wait_for_element('[data-testid="form-field-CLASSIFICATION"]')
            self.type(
                '[data-testid="form-field-CLASSIFICATION"]',
                "Restricted",
            )
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            version = '[data-testid="document-config-version-field"]'
            self.click(version)
            version_editor = '[data-testid="form-field-VERSION"]'
            self.type(version_editor, "1")
            self.find_element(version_editor).send_keys(Keys.BACKSPACE)
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)
            assert self.get_text(version) == ""

            prefix = '[data-testid="document-config-prefix-field"]'
            self.click(prefix)
            self.type('[data-testid="form-field-PREFIX"]', "NEW-")
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            date = '[data-testid="document-config-date-field"]'
            assert self.get_text(date) == "2026-06-08"
            self.click(date)
            self.assert_element_not_present('[data-testid="form-field-DATE"]')

        assert test_setup.compare_sandbox_and_expected_output()
