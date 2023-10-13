import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC80_T01_ViewDocument(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_not_empty_document()

            viewtype_selector = ViewType_Selector(self)
            screen_standalone_document = (
                viewtype_selector.do_go_to_standalone_document()
            )
            screen_standalone_document.assert_on_standalone_screen_document()
            screen_standalone_document.assert_not_empty_document()
            screen_standalone_document.assert_no_js_and_404_errors()
