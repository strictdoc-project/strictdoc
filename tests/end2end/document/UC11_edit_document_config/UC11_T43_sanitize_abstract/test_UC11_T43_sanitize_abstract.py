# pylint: disable=invalid-name

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer


class Test_UC11_T43_SanitizeAbstract(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("Document 1")
            self.assert_text("PROJECT INDEX")

            self.click_xpath('//*[@data-testid="tree-file-link"]')
            self.assert_text_visible("Document 1")

            self.hover_and_click(
                hover_selector="(//sdoc-node)[1]",
                click_selector=(
                    '(//sdoc-node)[1]//*[@data-testid="document-edit-config-action"]'  # noqa: E501
                ),
                hover_by=By.XPATH,
                click_by=By.XPATH,
            )

            # Contains trailing symbols.
            text_with_trailing_symbols = """
Hello world!    
              
Hello world!    
            
Hello world!    
            """  # noqa: W291, W293

            self.type(
                "(//*[@id='document[FREETEXT]'])[1]",
                text_with_trailing_symbols,
                by=By.XPATH,
            )

            self.click_xpath('//*[@data-testid="form-submit-action"]')

            self.assert_element_not_present(
                '[data-testid="form-submit-action"]'
            )

            self.assert_text("Hello world!\nHello world!\nHello world!")

        assert test_setup.compare_sandbox_and_expected_output()
