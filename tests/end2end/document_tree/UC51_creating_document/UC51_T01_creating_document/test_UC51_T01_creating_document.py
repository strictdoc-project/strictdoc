import filecmp
import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC51_T01_CreatingDocument(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        test_server.run()

        self.open(test_server.get_host_and_port())

        self.click_link("Add document")
        self.click('[data-testid="tree-add-document-action"]')

        self.type("#document_title", "Document 1")
        self.type("#document_path", "docs/document1.sdoc")

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        self.assert_text("Document 1")

        create_document_path = os.path.join(
            path_to_sandbox, "docs", "document1.sdoc"
        )
        assert os.path.exists(create_document_path)
        assert filecmp.cmp(
            create_document_path,
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
