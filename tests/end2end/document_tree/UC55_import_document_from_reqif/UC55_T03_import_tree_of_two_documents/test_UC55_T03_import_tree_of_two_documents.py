import os

from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_UC55_T03_ImportTreeOfTwoDocuments(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("PROJECT INDEX")

            self.click('[data-testid="tree-import-reqif-action"]')

            reqif_input_field = self.find_element(
                "//*[@data-testid='form-reqif_file-field']"
            )
            reqif_input_field.send_keys(path_to_reqif_sample)
            self.click_xpath('//*[@data-testid="form-submit-action"]')

            self.assert_text("Document 1")
            self.assert_text("Document 2")

        assert test_setup.compare_sandbox_and_expected_output()
