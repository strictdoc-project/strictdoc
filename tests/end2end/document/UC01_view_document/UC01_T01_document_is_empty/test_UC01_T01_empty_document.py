import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC01_T01_DocumentIsEmpty(BaseCase):
    def test_01(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("Empty Document")

            self.assert_text("PROJECT INDEX")

            self.click_xpath('//*[@data-testid="tree-file-link"]')

            self.assert_element('//*[@data-testid="document-placeholder"]')
