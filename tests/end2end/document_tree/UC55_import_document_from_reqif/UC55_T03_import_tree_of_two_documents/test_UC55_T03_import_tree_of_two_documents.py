import os

from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document_tree.form_import_reqif import (
    Form_ImportReqIF,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_UC55_T03_ImportTreeOfTwoDocuments(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)
            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_empty_tree()

            form_import: Form_ImportReqIF = (
                screen_document_tree.do_open_modal_import_reqif()
            )
            form_import.do_choose_file(path_to_reqif_sample)

            form_import.do_form_submit()

            screen_document_tree.assert_contains_document("Document 1")
            screen_document_tree.assert_contains_document("Document 2")

        assert test_setup.compare_sandbox_and_expected_output()
