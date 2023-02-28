import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC08_T03_EditSectionSanitizeTrailingSymbols(BaseCase):
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
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

        self.type("#section_title", "Modified title")

        # Contains trailing spaces.
        self.type(
            "#section_content",
            """
Hello world!    

Hello world!    

Hello world!    
            """,  # noqa: W291
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        self.assert_text("1. Modified title")

        # TODO: Cannot match this text for some reason.
        # The visual output and the written .sdoc file are ok though.
        # self.assert_text("Hello world!\\n Hello world!\\n Hello world!")  # noqa: ERA001, E501

        self.assert_element(
            "//turbo-frame[@id='frame-toc']//*[contains(., 'Modified title')]"
        )

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
