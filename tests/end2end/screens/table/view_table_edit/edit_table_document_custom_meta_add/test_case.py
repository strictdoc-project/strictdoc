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

            self.assert_element('[data-testid="document-config-metadata-add"]')
            self.assert_element_not_present(
                '[data-testid^="document-config-metadata-row-"]'
            )

            self.click('[data-testid="document-config-metadata-add"]')
            self.type(
                '[data-testid="form-field-metadata-name-new_custom_meta_0"]',
                "AUTHOR",
            )
            self.type(
                '[data-testid="form-field-metadata-value-new_custom_meta_0"]',
                "Ada",
            )
            screen_table.do_save_inline_cell_by_outside_click()

            row = '[data-testid="document-config-metadata-row-custom_meta_0"]'
            self.assert_text("AUTHOR:", selector=row)
            self.assert_text("Ada", selector=row)
            self.assert_element('[data-testid="document-config-metadata-add"]')

        assert test_setup.compare_sandbox_and_expected_output()
