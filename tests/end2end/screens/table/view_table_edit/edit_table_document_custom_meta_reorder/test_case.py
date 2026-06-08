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

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.do_toggle_edit_mode()

            self.drag_and_drop(
                '[data-testid="document-config-metadata-row-custom_meta_2"] '
                '[data-testid="form-move-field-action-form-field-metadata"]',
                '[data-testid="document-config-metadata-row-custom_meta_0"] '
                '[data-testid="document-config-metadata-label"]',
            )
            self.sleep(0.5)

            row_labels = self.execute_script(
                """
                return Array.from(document.querySelectorAll(
                    '[data-testid^="document-config-metadata-row-"]'
                )).map(row => row.querySelector(
                    '[data-testid="document-config-metadata-label"]'
                ).textContent.trim());
                """
            )
            assert row_labels == [
                "THIRD:",
                "FIRST:",
                "SECOND:",
            ]
            row_testids = self.execute_script(
                """
                return Array.from(document.querySelectorAll(
                    '[data-testid^="document-config-metadata-row-"]'
                )).map(row => row.dataset.testid);
                """
            )
            assert row_testids == [
                "document-config-metadata-row-custom_meta_0",
                "document-config-metadata-row-custom_meta_1",
                "document-config-metadata-row-custom_meta_2",
            ]

        assert test_setup.compare_sandbox_and_expected_output()
