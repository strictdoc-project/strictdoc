import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test06CreateRequirementInSection(BaseCase):
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

        self.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-menu-handler"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        self.click(
            selector=(
                "(//sdoc-node)[2]"
                '//*[@data-testid="node-add-requirement-child-action"]'
            ),
            by=By.XPATH,
        )

        self.type("#requirement_TITLE", "Requirement title")
        self.type("#requirement_STATEMENT", "Requirement statement")

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text("1. Requirement title")
        self.assert_element(
            "//turbo-frame[@id='frame-toc']"
            "//*[contains(., 'Requirement title')]"
        )

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
