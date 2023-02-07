import filecmp
import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test03CreatingChildSection(BaseCase):
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

        self.hover_and_click("sdoc-node", '[data-testid="node-menu-handler"]')
        self.click('[data-testid="node-add-section-child-action"]')

        self.type("#section_title", "First title")
        self.type("#section_content", "This is a free text of this section.")

        self.click_xpath("//button[@type='submit' and text()='Save']")
        self.assert_text("1. First title")

        self.assert_element("//turbo-frame[@id='frame-toc']")
        self.assert_element("//*[contains(text(), 'First title')]")
        self.assert_element(
            "//turbo-frame[@id='frame-toc']//*[contains(., 'First title')]"
        )

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
