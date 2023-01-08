import filecmp
import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test07EditRequirement(BaseCase):
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
        self.assert_text("Project index")

        self.click_link("DOC")

        self.assert_text("Hello world!")

        self.click_nth_visible_element("//a[contains(text(), 'Edit')]", 2)

        self.type("#requirement_UID", "Modified_UID")
        self.type("#requirement_TITLE", "Modified title")
        self.type("#requirement_STATEMENT", "Modified statement.")
        self.type("#requirement_RATIONALE", "Modified rationale.")

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text("1. Modified title")
        self.assert_text("Modified_UID")
        self.assert_text("Modified statement.")
        self.assert_text("Modified rationale.")

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
