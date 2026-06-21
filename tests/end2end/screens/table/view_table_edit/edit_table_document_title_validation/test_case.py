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
            editor = '[data-testid="form-field-TITLE"]'
            error = '[data-testid="table-inline-field-error"]'

            self.click(title)
            self.type(editor, "1")
            self.find_element(editor).send_keys(Keys.BACKSPACE)
            screen_table.do_save_inline_cell_by_outside_click()

            self.assert_exact_text(
                "Document title must not be empty.",
                error,
            )
            # The SeleniumBase methods `assert_text`, `assert_element`,
            # `assert_element_not_present`, and `assert_exact_text`
            # have built-in polling (default timeout ~20 seconds).
            # That's why we know that by the time the attribute is checked,
            # the element will definitely already be in the DOM,
            # if it is called after `self.assert_exact_text(...)`.
            assert self.get_attribute(title, "data-validation-error") == "true"

            self.click(title)
            screen_table.do_cancel_inline_cell_by_escape()
            self.assert_text("Original document", selector=title)
            self.assert_element_not_present(error)

            self.click(title)
            self.type(editor, "1")
            self.find_element(editor).send_keys(Keys.BACKSPACE)
            screen_table.do_save_inline_cell_by_outside_click()

            self.click(title)
            self.type(editor, "Corrected document")
            screen_table.do_save_inline_cell_by_outside_click()

            self.assert_text("Corrected document", selector=title)
            self.assert_element_not_present(error)
            assert (
                self.get_attribute(
                    title,
                    "data-validation-error",
                    hard_fail=False,
                )
                or ""
            ) != "true"

        assert test_setup.compare_sandbox_and_expected_output()
