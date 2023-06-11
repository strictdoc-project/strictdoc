import os

from seleniumbase import BaseCase

from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC40_T03_DisplayInlineCSVTable(BaseCase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_ProjectIndex(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document: Screen_Document = (
                screen_document_tree.do_click_on_first_document()
            )

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_not_empty_document()

            screen_document.assert_no_js_and_404_errors()

            viewtype_selector = ViewType_Selector(self)
            screen_deep_traceability = (
                viewtype_selector.do_go_to_deep_traceability()
            )
            screen_deep_traceability.assert_on_screen_deep_traceability()
            screen_deep_traceability.assert_not_empty_view()
