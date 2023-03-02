from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer


class Test_UC07_G1_T03_RemoveLink(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("Document 1")
            self.assert_text("PROJECT INDEX")

            self.click_xpath('//*[@data-testid="tree-file-link"]')

            self.assert_text("Hello world!")

            # Make sure that the normal (not table-based) requirement is
            # rendered.
            self.assert_element(
                '//sdoc-node[@data-testid="node-requirement-simple"]',
                by=By.XPATH,
            )

            self.hover_and_click(
                hover_selector="(//sdoc-node)[3]",
                click_selector=(
                    '(//sdoc-node)[3]//*[@data-testid="node-edit-action"]'
                ),
                hover_by=By.XPATH,
                click_by=By.XPATH,
            )

            self.click_xpath(
                '//*[@data-testid="form-delete-'
                'requirement[REFS_PARENT][]-field-action"]'
            )

            self.scroll_to(
                "//button[@type='submit' and text()='Save']", by=By.XPATH
            )
            self.click_xpath('//*[@data-testid="form-submit-action"]')

            # TODO: Make sure that the link with the REQ-001 text no longer
            # exists.

            self.assert_element_not_present(
                "//button[@type='submit' and text()='Save']", by=By.XPATH
            )

        assert test_setup.compare_sandbox_and_expected_output()
