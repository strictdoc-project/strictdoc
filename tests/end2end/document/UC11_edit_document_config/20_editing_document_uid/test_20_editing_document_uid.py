import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC11_20_EditDocumentUID(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "document.sdoc"),
            os.path.join(path_to_sandbox, "document.sdoc"),
        )

        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("Document 1")
        self.assert_text("PROJECT INDEX")

        self.click_link("DOC")
        self.assert_text_visible("Requirement title")

        self.click_nth_visible_element(
            "//a[@title='Edit document configuration']", 1
        )

        self.type("(//div[@id='document[UID]'])[1]", "DOC_001", by=By.XPATH)

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text("UID")

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
