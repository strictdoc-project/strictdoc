import filecmp
import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC07_EditRequirement_20_AddComment(BaseCase):
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

        self.click_nth_visible_element("//a[text()='Edit']", 2)

        self.type("(//*[@id='requirement_COMMENT'])", "Comment #1")

        self.click_link("Add comment")
        self.type("(//*[@id='requirement_COMMENT'])[2]", "Comment #2")

        self.click_link("Add comment")
        self.type("(//*[@id='requirement_COMMENT'])[3]", "Comment #3")

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text("Comment #1")
        self.assert_text("Comment #2")
        self.assert_text("Comment #3")

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
