import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_UC55_T02_CancelReqIFImportForm(BaseCase):
    def test_01(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("PROJECT INDEX")

            self.click('[data-testid="tree-import-reqif-action"]')

            self.click('[data-testid="form-cancel-action"]')

            self.assert_element_not_present(
                '[data-testid="form-cancel-action"]'
            )
