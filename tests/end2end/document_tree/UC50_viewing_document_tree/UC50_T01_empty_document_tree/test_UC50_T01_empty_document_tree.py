import os

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC50_T01_EmptyDocumentTree(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("PROJECT INDEX")

        self.assert_text("The document tree has no documents yet.")

        self.assert_element(
            (
                "//*[@data-testid='document-tree-empty-text' "
                "and contains(., 'The document tree has no documents yet.')]"
            ),
            by=By.XPATH,
        )
