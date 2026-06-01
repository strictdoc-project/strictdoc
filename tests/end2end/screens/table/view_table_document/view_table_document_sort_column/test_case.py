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
            # Initial state: no sorting, reset button hidden.
            # Server order: Banana, Apple, Cherry.
            #
            screen_table.assert_col_sort_state("Title", None)
            screen_table.assert_sort_reset_hidden()
            assert (
                screen_table.get_nth_row_field_text(1, "TITLE")
                == "Banana requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(2, "TITLE")
                == "Apple requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(3, "TITLE")
                == "Cherry requirement"
            )

            #
            # First click: ascending. Apple, Banana, Cherry.
            #
            screen_table.do_click_col_sort_btn("Title")
            screen_table.assert_col_sort_state("Title", "asc")
            screen_table.assert_sort_reset_visible()
            assert (
                screen_table.get_nth_row_field_text(1, "TITLE")
                == "Apple requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(2, "TITLE")
                == "Banana requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(3, "TITLE")
                == "Cherry requirement"
            )

            #
            # Second click: descending. Cherry, Banana, Apple.
            #
            screen_table.do_click_col_sort_btn("Title")
            screen_table.assert_col_sort_state("Title", "desc")
            screen_table.assert_sort_reset_visible()
            assert (
                screen_table.get_nth_row_field_text(1, "TITLE")
                == "Cherry requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(2, "TITLE")
                == "Banana requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(3, "TITLE")
                == "Apple requirement"
            )

            #
            # Third click: back to server order via icon cycle.
            #
            screen_table.do_click_col_sort_btn("Title")
            screen_table.assert_col_sort_state("Title", None)
            screen_table.assert_sort_reset_hidden()
            assert (
                screen_table.get_nth_row_field_text(1, "TITLE")
                == "Banana requirement"
            )

            #
            # Sort ascending again, then use toolbar "Order reset" button.
            #
            screen_table.do_click_col_sort_btn("Title")
            screen_table.assert_sort_reset_visible()
            assert (
                screen_table.get_nth_row_field_text(1, "TITLE")
                == "Apple requirement"
            )

            screen_table.do_click_sort_reset()
            screen_table.assert_col_sort_state("Title", None)
            screen_table.assert_sort_reset_hidden()
            assert (
                screen_table.get_nth_row_field_text(1, "TITLE")
                == "Banana requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(2, "TITLE")
                == "Apple requirement"
            )
            assert (
                screen_table.get_nth_row_field_text(3, "TITLE")
                == "Cherry requirement"
            )

        assert test_setup.compare_sandbox_and_expected_output()
