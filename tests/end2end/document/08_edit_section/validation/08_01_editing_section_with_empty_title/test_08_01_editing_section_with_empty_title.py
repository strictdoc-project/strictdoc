import os
import shutil

from selenium.webdriver import Keys
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_08_EditSectionWithEmptyTitle(BaseCase):
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

        # HACK: The only way the field is actually cleared.
        self.type("#section_title", "X")
        section_title_field = self.find_element("//div[@id='section_title']")
        section_title_field.click()
        section_title_field.send_keys(Keys.BACKSPACE)

        self.type("#section_content", "Modified statement.")

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text("Section title must not be empty.")
