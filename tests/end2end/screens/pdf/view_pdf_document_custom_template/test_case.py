import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.pdf.screen_pdf import Screen_PDFDocument
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Empty Document")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Empty Document")
            screen_document.assert_empty_document()

            viewtype_selector = ViewType_Selector(self)
            screen_pdf: Screen_PDFDocument = (
                viewtype_selector.do_go_to_pdf_document()
            )
            screen_pdf.assert_on_pdf_document()
            screen_pdf.assert_not_empty_view()

            screen_pdf.assert_text("CUSTOM TEMPLATE HERE")
