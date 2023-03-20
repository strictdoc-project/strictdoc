import os

from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document_tree.form_add_document import (
    Form_AddDocument,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_TC51_G1_T03_NoSDocExtension(BaseCase):
    def test_01(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)
            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_empty_tree()

            form_add_document: Form_AddDocument = (
                screen_document_tree.do_open_modal_form_add_document()
            )
            form_add_document.do_fill_in_title("Document 1")  # Empty document
            form_add_document.do_fill_in_path("docs/document")
            form_add_document.do_form_submit_and_catch_error(
                "Document path must end with a file name. "
                "The file name must have the .sdoc extension."
            )
