from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document_tree.form_add_document import (
    Form_AddDocument,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC51_T01_CreatingDocument(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)
            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_empty_tree()

            form_add_document: Form_AddDocument = (
                screen_document_tree.do_open_modal_form_add_document()
            )
            form_add_document.do_fill_in_title("Document 1")  # Empty document
            form_add_document.do_fill_in_path("docs/document1.sdoc")
            form_add_document.do_form_submit()

            screen_document_tree.assert_contains_document("Document 1")

        assert test_setup.compare_sandbox_and_expected_output()
