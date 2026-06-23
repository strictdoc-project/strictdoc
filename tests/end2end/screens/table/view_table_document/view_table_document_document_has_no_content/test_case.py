"""
@relation(SDOC-SRS-62, scope=file)
"""

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
            screen_project_index.assert_contains_document("Document title")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document title")

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            # Display mode: Title is visible, meta is simply absent (no
            # placeholder banner — that one belongs to the Document screen
            # only), the table shows its own empty-state placeholder.
            self.assert_text("Document title", '[data-testid="document-title"]')
            self.assert_element_not_visible(
                '[data-testid="document-config-uid-field"]'
            )
            self.assert_element_not_visible(
                '[data-testid="document-config-version-field"]'
            )
            screen_table.assert_empty_view("table-empty-placeholder")
            self.assert_element_not_visible('[data-testid="table-add-row"]')

            # The Table item in the viewtype menu is never marked "(empty)"
            # (same as Document).
            viewtype_selector.do_click_viewtype_handler()
            viewtype_selector.assert_viewtype_menu_opened()
            viewtype_selector.assert_menu_item_is_not_empty("table")
            viewtype_selector.do_click_viewtype_handler()
            viewtype_selector.assert_viewtype_menu_closed()

        assert test_setup.compare_sandbox_and_expected_output()
