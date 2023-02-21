import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC51_G1_T01_CreatingDocumentWithEmptyTitle(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("PROJECT INDEX")

        self.assert_text("The document tree has no documents yet.")

        self.click('[data-testid="tree-add-document-action"]')

        self.type("#document_title", "")  # Empty document
        self.type("#document_path", "docs/document1.sdoc")

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        self.assert_text("Document title must not be empty.")
