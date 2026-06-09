from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    @staticmethod
    def assert_same_vertical_position(before: dict, after: dict) -> None:
        assert abs(after["top"] - before["top"]) <= 5, (
            "Expected viewport position to be preserved: "
            f"before={before}, after={after}."
        )

    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            self.driver.set_window_size(1280, 700)

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.assert_not_empty_view()

            screen_table.do_click_col_sort_btn("Title")
            screen_table.assert_col_sort_state("Title", "asc")

            screen_table.do_open_rows_toolbar_panel()
            screen_table.do_toggle_row_type("SECTION")

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            screen_table.do_open_add_node_menu(row_order=3)
            screen_table.scroll_open_add_node_menu_to_center()
            screen_table.assert_add_node_actions_hidden(row_order=3)
            screen_table.assert_add_node_message(
                "Reset column sorting before adding nodes in Table view.",
                row_order=3,
            )
            screen_table.assert_add_node_message(
                "Show all node types before adding nodes in Table view.",
                row_order=3,
            )

            menu_position_before_sort_reset = (
                screen_table.get_open_add_node_menu_viewport_position()
            )
            screen_table.do_click_add_node_unblock(
                blocker="sorting",
                row_order=3,
            )
            screen_table.assert_col_sort_state("Title", None)
            menu_position_after_sort_reset = (
                screen_table.get_open_add_node_menu_viewport_position()
            )
            self.assert_same_vertical_position(
                menu_position_before_sort_reset,
                menu_position_after_sort_reset,
            )
            screen_table.assert_add_node_actions_hidden(row_order=None)
            screen_table.assert_add_node_message(
                "Show all node types before adding nodes in Table view.",
                row_order=None,
            )

            menu_position_before_rows_reset = (
                screen_table.get_open_add_node_menu_viewport_position()
            )
            screen_table.do_click_add_node_unblock(
                blocker="rows",
                row_order=None,
            )
            screen_table.assert_rows_of_type_visible("SECTION")
            menu_position_after_rows_reset = (
                screen_table.get_open_add_node_menu_viewport_position()
            )
            self.assert_same_vertical_position(
                menu_position_before_rows_reset,
                menu_position_after_rows_reset,
            )
            screen_table.assert_add_node_actions_visible(row_order=None)

            screen_table.do_close_add_node_menu_by_escape()

            active_node_mid = screen_table.get_node_mid_from_row(row_order=2)
            screen_table.do_open_inline_cell(active_node_mid, "TITLE")
            screen_table.scroll_node_row_to_center(active_node_mid)
            active_row_position_before_sort = (
                screen_table.get_node_row_viewport_position(active_node_mid)
            )

            screen_table.do_click_col_sort_btn_without_scrolling("Title")
            self.sleep(0.1)
            screen_table.assert_col_sort_state("Title", "asc")
            screen_table.assert_cell_is_inline_editing(
                active_node_mid,
                "TITLE",
            )
            active_row_position_after_sort = (
                screen_table.get_node_row_viewport_position(active_node_mid)
            )
            self.assert_same_vertical_position(
                active_row_position_before_sort,
                active_row_position_after_sort,
            )

            screen_table.do_open_rows_toolbar_panel()
            row_position_before_filter = (
                screen_table.get_node_row_viewport_position(active_node_mid)
            )
            screen_table.do_toggle_row_type("SECTION")
            self.sleep(0.5)
            screen_table.assert_cell_is_not_inline_editing(
                active_node_mid,
                "TITLE",
            )
            row_position_after_filter = (
                screen_table.get_node_row_viewport_position(active_node_mid)
            )
            assert (
                abs(
                    row_position_after_filter["top"]
                    - row_position_before_filter["top"]
                )
                > 5
            )
            screen_table.do_click_rows_show_all()

            screen_table.do_click_sort_reset()
            screen_table.assert_col_sort_state("Title", None)

            screen_table.do_open_add_node_menu(row_order=3)
            screen_table.scroll_open_add_node_menu_to_center()
            menu_position_before_creation = (
                screen_table.get_open_add_node_menu_viewport_position()
            )
            screen_table.do_click_add_node_action(
                element_type="REQUIREMENT",
                whereto="before",
                row_order=3,
            )
            self.sleep(0.5)

            new_node_mid = screen_table.get_node_mid_from_row(row_order=3)
            new_row_position = screen_table.get_node_row_viewport_position(
                new_node_mid
            )
            assert (
                abs(
                    new_row_position["top"]
                    - menu_position_before_creation["top"]
                )
                <= 3
            )
            assert (
                abs(
                    new_row_position["left"]
                    - menu_position_before_creation["left"]
                )
                <= 3
            )
            screen_table.assert_cell_is_not_inline_editing(
                new_node_mid,
                "TITLE",
            )

        assert test_setup.compare_sandbox_and_expected_output()
