import filecmp
import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test04CreatingTwoSiblingSections(BaseCase):
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

        # Section 1
        self.click_link("+S⬊")

        self.type("#section_title", "Section_1")
        self.type("#section_content", "This is a free text of the section 1.")

        self.click_xpath("//button[@type='submit' and text()='Save']")
        self.assert_text("1. Section_1")

        # Section 1_1
        self.click_nth_visible_element("//a[contains(text(), '+S⬊')]", 1)

        self.type("#section_title", "Section_1_1")
        self.type("#section_content", "This is a free text of the section 1_1.")

        self.click_xpath("//button[@type='submit' and text()='Save']")
        self.assert_text("1.1. Section_1_1")

        # Section 1_1_1
        self.click_nth_visible_element("//a[contains(text(), '+S⬊')]", 2)

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
