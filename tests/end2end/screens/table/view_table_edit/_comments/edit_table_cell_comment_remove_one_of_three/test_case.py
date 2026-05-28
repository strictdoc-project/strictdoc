from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

_HIDDEN_COLUMNS = (
    "Type|Level|UID|PREFIX|STATUS|TAGS|REFS|Title|Statement|Rationale"
)


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

            # Hide all columns except COMMENT so the inline form buttons are on screen.
            screen_table.do_reload_with_hidden_columns(_HIDDEN_COLUMNS)

            node_mid = screen_table.get_node_mid_from_row(row_order=1)
            assert node_mid is not None

            form = Form_EditRequirement(self)

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            screen_table.do_open_inline_cell(node_mid, "COMMENT")

            form.do_delete_comment(field_order=2)

            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            screen_table.assert_text("Comment #1")
            screen_table.assert_no_text("Comment #2")
            screen_table.assert_text("Comment #3")

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
