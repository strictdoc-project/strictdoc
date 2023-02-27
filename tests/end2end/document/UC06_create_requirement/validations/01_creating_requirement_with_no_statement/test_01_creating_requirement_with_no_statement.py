import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_06_01_ValidationRequirementWithNoStatement(BaseCase):
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

        self.click_xpath('//*[@data-testid="tree-file-link"]')

        self.assert_text("Hello world!")

        self.hover_and_click(
            hover_selector="(//sdoc-node)[1]",
            click_selector=(
                '(//sdoc-node)[1]//*[@data-testid="node-menu-handler"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        self.click(
            selector=(
                "(//sdoc-node)[1]"
                '//*[@data-testid="node-add-requirement-first-action"]'
            ),
            by=By.XPATH,
        )

        self.type(
            "//*[@id='requirement[TITLE]']", "Requirement title", by=By.XPATH
        )
        # Nothing is entered into the STATEMENT field.

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        self.assert_text("Requirement statement must not be empty.")
