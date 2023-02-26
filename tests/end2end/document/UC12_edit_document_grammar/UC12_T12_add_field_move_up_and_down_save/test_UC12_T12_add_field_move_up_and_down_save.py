import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC12_T12_AddFieldMoveUpAndDownSave(BaseCase):
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
        self.assert_text_visible("Requirement title")

        self.click_xpath('(//*[@data-testid="document-edit-grammar-action"])')

        self.click_link("Add grammar field")

        self.type(
            "(//*[@id='document_grammar[]'])[last()]",
            "CUSTOM_FIELD",
            by=By.XPATH,
        )

        # Move 3 times up and two times down.
        self.click_xpath(
            '(//*[@data-testid="form-move-up-Custom field-field-action"])[last()]'  # noqa: E501
        )
        self.click_xpath(
            '(//*[@data-testid="form-move-up-Custom field-field-action"])[last()]'  # noqa: E501
        )
        self.click_xpath(
            '(//*[@data-testid="form-move-up-Custom field-field-action"])[last()]'  # noqa: E501
        )

        self.click_xpath(
            '(//*[@data-testid="form-move-down-Custom field-field-action"])[last()]'  # noqa: E501
        )
        self.click_xpath(
            '(//*[@data-testid="form-move-down-Custom field-field-action"])[last()]'  # noqa: E501
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
