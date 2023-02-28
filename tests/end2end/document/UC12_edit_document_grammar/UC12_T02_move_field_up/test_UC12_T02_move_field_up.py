import os

from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC12_T02_MoveFieldUp(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("Document 1")
            self.assert_text("PROJECT INDEX")

            self.click_xpath('//*[@data-testid="tree-file-link"]')
            self.assert_text_visible("Requirement title")

            self.click_xpath(
                '(//*[@data-testid="document-edit-grammar-action"])'
            )

            self.click_xpath(
                "(//*[@data-testid="
                '"form-move-up-document_grammar[CUSTOM_FIELD]-field-action"])'
            )

            self.click_xpath('//*[@data-testid="form-submit-action"]')
            self.assert_element_not_present(
                '[data-testid="form-submit-action"]'
            )

        assert test_setup.compare_sandbox_and_expected_output()
