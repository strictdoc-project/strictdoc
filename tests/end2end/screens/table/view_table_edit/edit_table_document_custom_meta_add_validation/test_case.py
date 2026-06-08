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

            add = '[data-testid="document-config-metadata-add"]'
            name = '[data-testid="form-field-metadata-name-new_custom_meta_1"]'
            value = (
                '[data-testid="form-field-metadata-value-new_custom_meta_1"]'
            )
            error = (
                "[data-testid="
                '"document-config-metadata-error-new_custom_meta_1"]'
            )

            self.click(add)
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)
            self.assert_element(add)
            self.assert_element_not_present(name)

            self.click(add)
            self.type(value, "Value without name")
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)
            self.assert_exact_text("Key must not be empty.", error)
            assert self.get_attribute(name, "errors") == "true"
            assert self.get_attribute(value, "errors", hard_fail=False) is None
            assert self.get_text(value) == "Value without name"

            self.click(name)
            screen_table.do_cancel_inline_cell_by_escape()
            self.assert_element_not_present(error)

            self.click(add)
            self.type(name, "EMPTY_VALUE")
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)
            self.assert_exact_text("Value must not be empty.", error)
            assert self.get_attribute(name, "errors", hard_fail=False) is None
            assert self.get_attribute(value, "errors") == "true"

            self.click(name)
            screen_table.do_cancel_inline_cell_by_escape()

            self.click(add)
            self.type(name, "invalid name")
            self.type(value, "Preserved value")
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)
            self.assert_text("Key must start", selector=error)
            assert self.get_attribute(name, "errors") == "true"
            assert self.get_attribute(value, "errors", hard_fail=False) is None
            assert (
                self.get_attribute(
                    'input[name="metadata[new_custom_meta_1][name]"]',
                    "value",
                )
                == "INVALID NAME"
            )
            assert (
                self.get_attribute(
                    'input[name="metadata[new_custom_meta_1][value]"]',
                    "value",
                )
                == "Preserved value"
            )
            assert len(self.find_elements(error)) == 1

            self.click(name)
            self.type(name, "VALID_NAME")
            screen_table.do_save_inline_cell_by_cmd_enter()
            self.sleep(0.5)

            row = '[data-testid="document-config-metadata-row-custom_meta_1"]'
            self.assert_text("VALID_NAME:", selector=row)
            self.assert_text("Preserved value", selector=row)
            self.assert_element(add)
            self.assert_element_not_present(error)

        assert test_setup.compare_sandbox_and_expected_output()
