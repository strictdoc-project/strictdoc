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
            title_editor = '[data-testid="form-field-TITLE"]'

            self.click(title)
            self.type(title_editor, "Updated document")
            screen_table.do_save_inline_cell_by_outside_click()
            self.assert_text("Updated document", selector=title)

            # The custom-metadata rows share one <form> with the document's
            # TITLE/UID/VERSION/CLASSIFICATION/PREFIX fields (rendered as
            # hidden inputs alongside the rows). Saving one metadata field
            # submits that whole form, so the request the server receives
            # for this metadata save also carries those hidden fields.
            first_row = (
                '[data-testid="document-config-metadata-row-custom_meta_0"]'
            )
            first_field = (
                f'{first_row} [data-testid="document-config-metadata-field"]'
            )
            self.click(first_field)
            self.wait_for_element(
                '[data-testid="form-field-metadata-custom_meta_0"]'
            )
            self.type(
                '[data-testid="form-field-metadata-custom_meta_0"]',
                "Updated value",
            )
            screen_table.do_save_inline_cell_by_outside_click()
            self.assert_text("Updated value", selector=first_row)

            # The title must still read the value saved above: the hidden
            # TITLE input carried by the metadata form's own submission was
            # captured before that edit and must not overwrite it.
            self.assert_text("Updated document", selector=title)

            screen_table.do_toggle_edit_mode()

        assert test_setup.compare_sandbox_and_expected_output()
