import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test05_CreatingThreeNestedSections(BaseCase):
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

        # Section 1
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
                '//*[@data-testid="node-add-section-child-action"]'
            ),
            by=By.XPATH,
        )

        self.type("#section_title", "Section_1")
        self.type("#section_content", "This is a free text of the section 1.")

        self.click_xpath("//button[@type='submit' and text()='Save']")
        self.assert_text("1. Section_1")

        # Section 1_1
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
                '//*[@data-testid="node-add-section-child-action"]'
            ),
            by=By.XPATH,
        )

        self.type("#section_title", "Section_1_1")
        self.type("#section_content", "This is a free text of the section 1_1.")

        self.click_xpath("//button[@type='submit' and text()='Save']")
        self.assert_text("1.1. Section_1_1")

        # # Section 1_1_1
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
                '//*[@data-testid="node-add-section-child-action"]'
            ),
            by=By.XPATH,
        )

        self.type("#section_title", "Section_1_1_1")
        self.type(
            "#section_content", "This is a free text of the section 1_1_1."
        )

        self.click_xpath("//button[@type='submit' and text()='Save']")
        self.assert_text("1.1.1. Section_1_1_1")

        self.assert_element(
            "//turbo-frame[@id='frame-toc']//*[contains(., 'Section_1_1')]"
        )

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
