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
            screen_project_index.assert_contains_document("Document")

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            # Clear localStorage before navigating to table view.
            # Tests run with --reuse-session (shared browser), so localStorage
            # persists across test cases. Clearing here ensures the table view
            # JS starts with no saved column state and reflects a clean initial state.
            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.assert_not_empty_view()

            #
            # Initial state
            #
            screen_table.assert_toolbar_btn_label("Columns")
            screen_table.assert_toolbar_panel_closed()

            # Open panel — Show all disabled, checkboxes present
            screen_table.do_open_toolbar_panel()
            screen_table.assert_show_all_disabled()
            self.assert_element('[data-testid="col-checkbox-Type"]')
            self.assert_element('[data-testid="col-checkbox-Statement"]')

            #
            # Hide "Type" column
            #
            screen_table.do_toggle_column("Type")
            screen_table.assert_column_header_hidden("Type")
            self.assert_url_contains("hidden=Type")
            screen_table.assert_toolbar_btn_label("Columns (1 hidden)")
            screen_table.assert_show_all_enabled()

            #
            # Hide "Statement" column
            #
            screen_table.do_toggle_column("Statement")
            screen_table.assert_column_header_hidden("Statement")
            self.assert_url_contains("Statement")
            screen_table.assert_toolbar_btn_label("Columns (2 hidden)")

            #
            # Close panel by clicking outside
            #
            screen_table.do_close_panel_by_outside_click()

            #
            # Show all
            #
            screen_table.do_open_toolbar_panel()
            screen_table.do_click_show_all()
            screen_table.assert_column_header_visible("Type")
            screen_table.assert_column_header_visible("Statement")
            self.assert_url_not_contains("hidden=")
            screen_table.assert_toolbar_btn_label("Columns")
            screen_table.assert_show_all_disabled()

        assert test_setup.compare_sandbox_and_expected_output()
