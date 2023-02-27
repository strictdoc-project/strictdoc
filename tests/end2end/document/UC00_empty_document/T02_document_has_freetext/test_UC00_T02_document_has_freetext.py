import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC00_T02_DocumentHasFreeText(BaseCase):
    def test_01(self):
        test_server = SDocTestServer(input_path=path_to_this_test_file_folder)
        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("Document 1")

        self.assert_text("PROJECT INDEX")

        self.click_xpath('//*[@data-testid="tree-file-link"]')

        self.assert_element_not_visible(
            '//*[@data-testid="document-placeholder"]'
        )
