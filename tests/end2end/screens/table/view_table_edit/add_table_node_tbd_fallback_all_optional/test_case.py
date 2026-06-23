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

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.assert_not_empty_view()

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()
            assert screen_table.get_table_row_count() == 1

            screen_table.do_open_add_node_menu(row_order=1)
            screen_table.do_click_add_node_action(
                element_type="NOTE",
                whereto="before",
                row_order=1,
            )
            screen_table.wait_for_table_row_count(2)

            assert screen_table.get_table_row_count() == 2

        assert test_setup.compare_sandbox_and_expected_output()
