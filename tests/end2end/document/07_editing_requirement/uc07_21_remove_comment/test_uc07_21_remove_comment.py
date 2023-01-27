import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC07_EditRequirement_21_RemoveComment(BaseCase):
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

        self.open("http://localhost:8001")

        self.assert_text("Document 1")
        self.assert_text("PROJECT INDEX")

        self.click_link("DOC")

        self.assert_text("Hello world!")

        # self.click_nth_visible_element("//a[text()='Edit']", 2)
        self.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector='(//sdoc-node)[2]//*[@data-testid="node-edit-action"]',
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

        self.click_xpath("(//a[text()='Delete comment'])[2]")

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text("Comment #1")
        self.assert_text("Comment #3")

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
