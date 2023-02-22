import filecmp
import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_03_02_CreatingBeforeSection(BaseCase):
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
        self.click('[data-testid="node-add-section-above-action"]')

        self.type("#section_title", "Section A")
        self.type("#section_content", "Section A text.")

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        self.assert_text("1. Section A")
        self.assert_text("2. Section B")

        self.assert_element(
            "//turbo-frame[@id='frame-toc']//*[contains(., 'Section A')]"
        )
        self.assert_element(
            "//turbo-frame[@id='frame-toc']//*[contains(., 'Section B')]"
        )

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
