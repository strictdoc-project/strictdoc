from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer


class Test_UC03_T06_CreateSectionAfterRequirement(BaseCase):
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

            # Section

            self.hover_and_click(
                hover_selector="(//sdoc-node)[1]",
                click_selector=(
                    '(//sdoc-node)[1]//*[@data-testid="node-menu-handler"]'
                ),
                hover_by=By.XPATH,
                click_by=By.XPATH,
            )
            self.click(
                selector=(
                    "(//sdoc-node)[1]"
                    '//*[@data-testid="node-add-section-first-action"]'
                ),
                by=By.XPATH,
            )

            self.type("#section_title", "Section title")
            self.type("#section_content", "Section statement.")

            self.click_xpath('//*[@data-testid="form-submit-action"]')

            self.assert_text("1. Section title")

            # Requirement

            self.hover_and_click(
                hover_selector="(//sdoc-node)[2]",
                click_selector=(
                    '(//sdoc-node)[2]//*[@data-testid="node-menu-handler"]'
                ),
                hover_by=By.XPATH,
                click_by=By.XPATH,
            )
            self.click(
                selector=(
                    "(//sdoc-node)[2]"
                    '//*[@data-testid="node-add-requirement-below-action"]'
                ),
                by=By.XPATH,
            )

            self.type(
                "//*[@id='requirement[TITLE]']",
                "Requirement title",
                by=By.XPATH,
            )

            self.type(
                "//*[@id='requirement[STATEMENT]']",
                "Requirement statement.",
                by=By.XPATH,
            )

            self.click_xpath('//*[@data-testid="form-submit-action"]')

            self.assert_text("2. Requirement title")

        assert test_setup.compare_sandbox_and_expected_output()
