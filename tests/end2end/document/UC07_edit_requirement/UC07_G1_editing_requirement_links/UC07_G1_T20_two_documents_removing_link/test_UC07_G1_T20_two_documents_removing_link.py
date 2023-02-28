from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer


class Test_UC07_G1_T20_TwoDocumentsRemovingLink(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("Document 1")
            self.assert_text("PROJECT INDEX")
            # First, check that the first document's requirement REQ-001 does
            # contain a child link to REQ-002.
            self.click_xpath("(//*[@data-testid='tree-file-link'])[1]")
            self.assert_element("//*[contains(., 'REQ-002')]", by=By.XPATH)

            # Now, go to the document 2 and remove the parent link to REQ-001.
            self.open(test_server.get_host_and_port())
            self.click_xpath("(//*[@data-testid='tree-file-link'])[2]")

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

            # Now check that the documents do not have the link anymore.
            self.open(test_server.get_host_and_port())
            self.click_xpath("(//*[@data-testid='tree-file-link'])[1]")
            self.assert_element_not_present(
                "//*[contains(., 'REQ-002')]", by=By.XPATH
            )

            self.open(test_server.get_host_and_port())
            self.click_xpath("(//*[@data-testid='tree-file-link'])[2]")
            self.assert_element_not_present(
                "//*[contains(., 'REQ-001')]", by=By.XPATH
            )

        assert test_setup.compare_sandbox_and_expected_output()
