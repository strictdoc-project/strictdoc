import filecmp
import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test06CreateRequirement(BaseCase):
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

        # Requirement 1
        self.click_nth_visible_element("//a[contains(text(), '+R⬊')]", 1)

        self.type("#requirement_UID", "REQ-001")
        self.type("#requirement_TITLE", "Requirement title #1")
        self.type("#requirement_STATEMENT", "Requirement statement #1.")
        self.type("#requirement_RATIONALE", "Requirement rationale #1.")

        self.click_xpath("//button[@type='submit' and text()='Save']")

        # Requirement 2
        self.click_nth_visible_element("//a[contains(text(), '+R⬇')]", 1)

        self.type("#requirement_UID", "REQ-002")
        self.type("#requirement_TITLE", "Requirement title #2")
        self.type("#requirement_STATEMENT", "Requirement statement #2.")
        self.type("#requirement_RATIONALE", "Requirement rationale #2.")

        self.click_xpath("//button[@type='submit' and text()='Save']")

        # Requirement 3
        self.click_nth_visible_element("//a[contains(text(), '+R⬇')]", 2)

        self.type("#requirement_UID", "REQ-003")
        self.type("#requirement_TITLE", "Requirement title #3")
        self.type("#requirement_STATEMENT", "Requirement statement #3.")
        self.type("#requirement_RATIONALE", "Requirement rationale #3.")

        self.click_xpath("//button[@type='submit' and text()='Save']")

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
