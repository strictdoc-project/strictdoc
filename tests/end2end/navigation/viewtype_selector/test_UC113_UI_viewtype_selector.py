from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import (
    ViewType_Selector,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test_UC113_UI_viewtype_selector(BaseCase):
    def test_01(self):
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
            screen_document.assert_text("Hello world!")

            viewtype_selector = ViewType_Selector(self)

            # menu is on the page and closed
            viewtype_selector.assert_viewtype_handler()
            viewtype_selector.assert_viewtype_menu_closed()
            # open menu
            viewtype_selector.do_click_viewtype_handler()
            # menu is opened
            viewtype_selector.assert_viewtype_menu_opened()

            # close menu
            viewtype_selector.do_click_viewtype_handler()
            # menu is closed
            viewtype_selector.assert_viewtype_menu_closed()

            # go to deep traceability
            screen_deep_traceability = (
                viewtype_selector.do_go_to_deep_traceability()
            )
            screen_deep_traceability.assert_on_screen_deep_traceability()

            # go to traceability
            screen_traceability = viewtype_selector.do_go_to_traceability()
            screen_traceability.assert_on_screen_traceability()

            # go to table
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            # go back to document
            screen_document_2step = viewtype_selector.do_go_to_document()
            screen_document_2step.assert_on_screen_document()

        assert test_setup.compare_sandbox_and_expected_output()
