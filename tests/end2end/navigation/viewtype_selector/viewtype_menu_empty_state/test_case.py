from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import (
    ViewType_Selector,
)
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
            screen_project_index.assert_contains_document("Empty document")

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Empty document")
            screen_document.assert_empty_document()

            viewtype_selector = ViewType_Selector(self)

            # Open menu — all views should be marked as empty.
            viewtype_selector.do_click_viewtype_handler()
            viewtype_selector.assert_viewtype_menu_opened()
            viewtype_selector.assert_menu_item_is_empty("table")
            viewtype_selector.assert_menu_item_is_empty("traceability")
            viewtype_selector.assert_menu_item_is_empty("deep_traceability")

            # Close menu.
            viewtype_selector.do_click_viewtype_handler()
            viewtype_selector.assert_viewtype_menu_closed()

            # Add a section to the document.
            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_section = root_node_menu.do_node_add_element_first(
                "SECTION"
            )
            form_edit_section.do_fill_in("TITLE", "New section")
            form_edit_section.do_form_submit()

            # Open menu — all views are no longer empty.
            viewtype_selector.do_click_viewtype_handler()
            viewtype_selector.assert_viewtype_menu_opened()
            viewtype_selector.assert_menu_item_is_not_empty("table")
            viewtype_selector.assert_menu_item_is_not_empty("traceability")
            viewtype_selector.assert_menu_item_is_not_empty("deep_traceability")

        assert test_setup.compare_sandbox_and_expected_output()
