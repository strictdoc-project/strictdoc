import filecmp
import os
import shutil

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC07_G1_T20_TwoDocumentsRemovingLink(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "document1.sdoc"),
            os.path.join(path_to_sandbox, "document1.sdoc"),
        )
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "document2.sdoc"),
            os.path.join(path_to_sandbox, "document2.sdoc"),
        )

        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("Document 1")
        self.assert_text("PROJECT INDEX")
        # First, check that the first document's requirement REQ-001 does
        # contain a child link to REQ-002.
        self.click_xpath("(//a[text()='DOC'])[1]")
        self.assert_element("//*[contains(., 'REQ-002')]", by=By.XPATH)

        # Now, go to the document 2 and remove the parent link to REQ-001.
        self.open(test_server.get_host_and_port())
        self.click_xpath("(//a[text()='DOC'])[2]")

        self.assert_text("Hello world 2!")
        self.assert_element("//*[contains(., 'REQ-001')]", by=By.XPATH)

        self.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

        self.click_xpath(
            '//*[@data-testid="form-delete-'
            'requirement[REFS_PARENT][]-field-action"]'
        )

        self.click_xpath('//*[@data-testid="form-submit-action"]')
        self.assert_element_not_present(
            '//*[@data-testid="form-submit-action"]', by=By.XPATH
        )

        assert os.path.exists(os.path.join(path_to_sandbox, "document1.sdoc"))
        assert os.path.exists(os.path.join(path_to_sandbox, "document2.sdoc"))
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document1.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document1.expected.sdoc"
            ),
        )
        assert filecmp.cmp(
            os.path.join(path_to_sandbox, "document2.sdoc"),
            os.path.join(
                path_to_this_test_file_folder, "document2.expected.sdoc"
            ),
        )

        # Now check that the documents do not have the link anymore.
        self.open(test_server.get_host_and_port())
        self.click_xpath("(//a[text()='DOC'])[1]")
        self.assert_element_not_present(
            "//*[contains(., 'REQ-002')]", by=By.XPATH
        )

        self.open(test_server.get_host_and_port())
        self.click_xpath("(//a[text()='DOC'])[2]")
        self.assert_element_not_present(
            "//*[contains(., 'REQ-001')]", by=By.XPATH
        )
