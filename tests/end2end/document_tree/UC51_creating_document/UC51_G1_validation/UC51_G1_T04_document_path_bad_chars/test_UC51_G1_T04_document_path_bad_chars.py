import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_TC51_G1_T04_BadCharacters(BaseCase):
    def test_01(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("PROJECT INDEX")

            self.assert_text("The document tree has no documents yet.")

            self.click('[data-testid="tree-add-document-action"]')

            self.type("#document_title", "Document 1")  # Empty document
            self.type("#document_path", "docs/doc!#ument.sdoc")

            self.click_xpath('//*[@data-testid="form-submit-action"]')
            self.assert_text(
                "Document path must be relative and only contain slashes, "
                "alphanumeric characters, and underscore symbols."
            )
