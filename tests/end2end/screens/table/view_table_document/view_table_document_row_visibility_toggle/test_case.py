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

            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.assert_not_empty_view()

            #
            # Initial state
            #
            screen_table.assert_rows_toolbar_btn_label("NODES")
            screen_table.assert_rows_toolbar_panel_closed()

            # Open rows panel — Show all disabled, both types present
            screen_table.do_open_rows_toolbar_panel()
            screen_table.assert_rows_show_all_disabled()
            self.assert_element('[data-testid="row-checkbox-SECTION"]')
            self.assert_element('[data-testid="row-checkbox-REQUIREMENT"]')

            #
            # Hide "SECTION" rows
            #
            screen_table.do_toggle_row_type("SECTION")
            screen_table.assert_rows_of_type_hidden("SECTION")
            screen_table.assert_rows_of_type_visible("REQUIREMENT")
            screen_table.assert_rows_toolbar_btn_label("NODES • 1 hidden")
            screen_table.assert_rows_show_all_enabled()

            #
            # Replace tbody and verify the rows filter targets the new body.
            #
            self.execute_script(
                "const tbody = document.querySelector("
                "  '.content-view-table > tbody'"
                ");"
                "tbody.replaceWith(tbody.cloneNode(true));"
            )
            self.sleep(0.1)
            screen_table.assert_rows_of_type_hidden("SECTION")
            screen_table.assert_rows_of_type_visible("REQUIREMENT")

            screen_table.do_toggle_row_type("SECTION")
            screen_table.assert_rows_of_type_visible("SECTION")
            screen_table.do_toggle_row_type("SECTION")
            screen_table.assert_rows_of_type_hidden("SECTION")

            #
            # Hide "REQUIREMENT" rows
            #
            screen_table.do_toggle_row_type("REQUIREMENT")
            screen_table.assert_rows_of_type_hidden("REQUIREMENT")
            screen_table.assert_rows_toolbar_btn_label("NODES • 2 hidden")

            #
            # Show all
            #
            screen_table.do_click_rows_show_all()
            screen_table.assert_rows_of_type_visible("SECTION")
            screen_table.assert_rows_of_type_visible("REQUIREMENT")
            screen_table.assert_rows_toolbar_btn_label("NODES")
            screen_table.assert_rows_show_all_disabled()

        assert test_setup.compare_sandbox_and_expected_output()
