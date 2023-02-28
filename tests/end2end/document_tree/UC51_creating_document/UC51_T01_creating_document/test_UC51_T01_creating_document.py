from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer


class Test_UC51_T01_CreatingDocument(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.click_link("Add document")
            self.click('[data-testid="tree-add-document-action"]')

            self.type("#document_title", "Document 1")
            self.type("#document_path", "docs/document1.sdoc")

            self.click_xpath('//*[@data-testid="form-submit-action"]')

            self.assert_text("Document 1")

        assert test_setup.compare_sandbox_and_expected_output()
