from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer


class Test_UC03_T05_CreateThreeNestedSections(BaseCase):
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

            # Section 1
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

            self.type("#section_title", "Section_1")
            self.type(
                "#section_content", "This is a free text of the section 1."
            )

            self.click_xpath('//*[@data-testid="form-submit-action"]')
            self.assert_text("1. Section_1")

            # Section 1_1
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
                    '//*[@data-testid="node-add-section-child-action"]'
                ),
                by=By.XPATH,
            )

            self.type("#section_title", "Section_1_1")
            self.type(
                "#section_content", "This is a free text of the section 1_1."
            )

            self.click_xpath('//*[@data-testid="form-submit-action"]')
            self.assert_text("1.1. Section_1_1")

            # # Section 1_1_1
            self.hover_and_click(
                hover_selector="(//sdoc-node)[3]",
                click_selector=(
                    '(//sdoc-node)[3]//*[@data-testid="node-menu-handler"]'
                ),
                hover_by=By.XPATH,
                click_by=By.XPATH,
            )
            self.click(
                selector=(
                    "(//sdoc-node)[3]"
                    '//*[@data-testid="node-add-section-child-action"]'
                ),
                by=By.XPATH,
            )

            self.type("#section_title", "Section_1_1_1")
            self.type(
                "#section_content", "This is a free text of the section 1_1_1."
            )

            self.click_xpath('//*[@data-testid="form-submit-action"]')
            self.assert_text("1.1.1. Section_1_1_1")

            self.assert_element(
                "//turbo-frame[@id='frame-toc']//*[contains(., 'Section_1_1')]"
            )

        assert test_setup.compare_sandbox_and_expected_output()
