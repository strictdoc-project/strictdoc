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

            first_row = (
                '[data-testid="document-config-metadata-row-custom_meta_0"]'
            )
            first_field = (
                f'{first_row} [data-testid="document-config-metadata-field"]'
            )

            self.click(first_field)
            assert (
                self.find_element(first_field).get_attribute("data-mode") or ""
            ) != "editing"

            screen_table.do_toggle_edit_mode()

            self.click(first_field)
            self.wait_for_element(
                '[data-testid="form-field-metadata-custom_meta_0"]'
            )
            self.type(
                '[data-testid="form-field-metadata-custom_meta_0"]',
                "Cancelled value",
            )
            screen_table.do_cancel_inline_cell_by_escape()
            self.assert_text("First value", selector=first_row)

            self.click(first_field)
            self.type(
                '[data-testid="form-field-metadata-custom_meta_0"]',
                "Saved by command",
            )
            screen_table.do_save_inline_cell_by_cmd_enter()
            self.sleep(0.5)
            self.assert_text("Saved by command", selector=first_row)

            second_row = (
                '[data-testid="document-config-metadata-row-custom_meta_1"]'
            )
            self.click(
                f'{second_row} [data-testid="document-config-metadata-field"]'
            )
            self.type(
                '[data-testid="form-field-metadata-custom_meta_1"]',
                "Saved by blur",
            )
            screen_table.do_save_inline_cell_by_outside_click()
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
            assert row_labels == ["FIRST:", "SECOND:", "REVISION:"]

            raw_revision = self.get_attribute(
                '[data-testid="document-config-metadata-row-custom_meta_2"] '
                'input[name="metadata[custom_meta_2][value]"]',
                "value",
            )
            rendered_revision = self.get_text(
                '[data-testid="document-config-metadata-row-custom_meta_2"] '
                "sdoc-autogen"
            )
            assert raw_revision == "@GIT_VERSION"
            assert rendered_revision != raw_revision
            assert len(rendered_revision) > 0

        assert test_setup.compare_sandbox_and_expected_output()
