import os
import shutil

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC11_02_EditDocumentTitle_EmptyValidation(BaseCase):
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
        self.assert_text_visible("Requirement title")

        self.click_nth_visible_element(
            "//a[contains(text(), 'Edit document config')]", 1
        )

        # HACK: The only way the field is actually cleared.
        self.type("(//div[@id='document[TITLE]'])[1]", "1", by=By.XPATH)
        document_title_field = self.find_visible_elements(
            "//div[@id='document[TITLE]']"
        )[0]
        document_title_field.send_keys(Keys.BACKSPACE)

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text("Document title must not be empty.")
