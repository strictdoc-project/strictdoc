import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC07_G1_T02_AddThreeLinks(BaseCase):
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

        self.assert_text("Hello world!")
        # Make sure that the normal (not table-based) requirement is rendered.
        self.assert_element(
            '//sdoc-node[@data-testid="node-requirement-normal"]', by=By.XPATH
        )

        self.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

        self.click_xpath("//*[@data-testid='form-add-parent-link-action']")
        self.click_xpath("//*[@data-testid='form-add-parent-link-action']")
        self.click_xpath("//*[@data-testid='form-add-parent-link-action']")

        self.type(
            "(//*[@data-testid='form-requirement[REFS_PARENT][]-field'])[1]",
            "REQ-002",
        )
        self.type(
            "(//*[@data-testid='form-requirement[REFS_PARENT][]-field'])[2]",
            "REQ-003",
        )
        self.type(
            "(//*[@data-testid='form-requirement[REFS_PARENT][]-field'])[3]",
            "REQ-004",
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')
        self.assert_element_not_present(
            "//button[@type='submit' and text()='Save']", by=By.XPATH
        )

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
