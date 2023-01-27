import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_06_02_CreatingRequirementMalformedRSTStatement(BaseCase):
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

        # self.click_nth_visible_element("//a[contains(text(), '+R⬊')]", 1)
        self.hover_and_click(
            hover_selector="(//sdoc-node)[1]",
            click_selector='(//sdoc-node)[1]//*[@data-testid="node-menu-handler"]',
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        self.click(
            selector='(//sdoc-node)[1]//*[@data-testid="node-add-requirement-child-action"]',
            by=By.XPATH,
        )

        self.type("#requirement_TITLE", "Requirement title")
        self.type(
            "#requirement_STATEMENT",
            """
- Broken RST markup

  - AAA
  ---
""".strip(),
        )

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text(
            "RST markup syntax error on line 4: "
            "Bullet list ends without a blank line; unexpected unindent."
        )
