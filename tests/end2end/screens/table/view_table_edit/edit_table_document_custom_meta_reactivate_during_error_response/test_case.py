from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.screens.table.view_table_edit.race_helpers import (
    BlockedTableFetch,
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

            row = '[data-testid="document-config-metadata-row-custom_meta_0"]'
            field = f'{row} [data-testid="document-config-metadata-field"]'
            editor = '[data-testid="form-field-metadata-custom_meta_0"]'

            # A validation error for an older value must not replace a newer
            # correction. Pause the invalid save when the browser calls fetch.
            # The user reopens the same cell and enters Corrected value before
            # the request reaches the server. After release, the validation
            # error must leave that text and the active editor unchanged. A
            # following save must persist the correction.
            blocked_fetch = BlockedTableFetch(
                self,
                "/actions/table/update_document_custom_meta",
                "active_field_name=value",
            )

            self.click(field)
            self.type(editor, "1")
            self.find_element(editor).send_keys(Keys.BACKSPACE)
            screen_table.do_save_inline_cell_by_outside_click()
            blocked_fetch.wait_until_requested()

            self.click(field)
            self.type(editor, "Corrected value")

            blocked_fetch.release()
            blocked_fetch.restore()

            assert self.get_text(editor) == "Corrected value"
            assert self.get_attribute(field, "data-mode") == "editing"

            screen_table.do_save_inline_cell_by_outside_click()
            WebDriverWait(self.driver, 10).until(
                lambda _: (
                    (
                        self.get_attribute(field, "data-mode", hard_fail=False)
                        or ""
                    )
                    != "editing"
                )
            )

            self.assert_text("Corrected value", selector=row)

        assert test_setup.compare_sandbox_and_expected_output()
