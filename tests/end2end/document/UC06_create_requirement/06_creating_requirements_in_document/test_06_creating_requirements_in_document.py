import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test06CreateRequirementsInDocument(BaseCase):
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

        # Requirement 1
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

        self.type("//*[@id='requirement[UID]']", "REQ-001", by=By.XPATH)
        self.type(
            "//*[@id='requirement[TITLE]']", "Requirement title #1", by=By.XPATH
        )
        self.type(
            "//*[@id='requirement[STATEMENT]']",
            "Requirement statement #1.",
            by=By.XPATH,
        )
        self.type(
            "//*[@id='requirement[RATIONALE]']",
            "Requirement rationale #1.",
            by=By.XPATH,
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        # Requirement 2
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
                '//*[@data-testid="node-add-requirement-below-action"]'
            ),
            by=By.XPATH,
        )

        self.type("//*[@id='requirement[UID]']", "REQ-002", by=By.XPATH)
        self.type(
            "//*[@id='requirement[TITLE]']", "Requirement title #2", by=By.XPATH
        )
        self.type(
            "//*[@id='requirement[STATEMENT]']",
            "Requirement statement #2.",
            by=By.XPATH,
        )
        self.type(
            "//*[@id='requirement[RATIONALE]']",
            "Requirement rationale #2.",
            by=By.XPATH,
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        # Requirement 3
        self.hover_and_click(
            hover_selector="(//sdoc-node)[3]",
            click_selector=(
                '(//sdoc-node)[3]//*[@data-testid="node-menu-handler"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        self.click(
            selector=(
                "(//sdoc-node)[3]"
                '//*[@data-testid="node-add-requirement-below-action"]'
            ),
            by=By.XPATH,
        )

        self.type("//*[@id='requirement[UID]']", "REQ-003", by=By.XPATH)
        self.type(
            "//*[@id='requirement[TITLE]']", "Requirement title #3", by=By.XPATH
        )
        self.type(
            "//*[@id='requirement[STATEMENT]']",
            "Requirement statement #3.",
            by=By.XPATH,
        )
        self.type(
            "//*[@id='requirement[RATIONALE]']",
            "Requirement rationale #3.",
            by=By.XPATH,
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        self.assert_element_not_present(
            "//button[@type='submit' and text()='Save']", by=By.XPATH
        )

        # Check the resulting TOC.

        self.assert_text("1. Requirement title #1")
        self.assert_text("2. Requirement title #2")
        self.assert_text("3. Requirement title #3")

        self.assert_element(
            "//turbo-frame[@id='frame-toc']"
            "//*[contains(., 'Requirement title #1')]"
        )
        self.assert_element(
            "//turbo-frame[@id='frame-toc']"
            "//*[contains(., 'Requirement title #2')]"
        )
        self.assert_element(
            "//turbo-frame[@id='frame-toc']"
            "//*[contains(., 'Requirement title #3')]"
        )

        # Check the resulting SDoc.

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
