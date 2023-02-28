import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_UC55_G1_T01_NotAReqIFormat(BaseCase):
    def test_01(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("PROJECT INDEX")

            self.assert_text("The document tree has no documents yet.")

            self.click('[data-testid="tree-import-reqif-action"]')

            reqif_input_field = self.find_element(
                "//*[@data-testid='form-reqif_file-field']"
            )
            reqif_input_field.send_keys(path_to_reqif_sample)
            self.click_xpath('//*[@data-testid="form-submit-action"]')

            self.assert_text(
                "Cannot parse ReqIF file: "
                "Start tag expected, '<' not found, line 1, column 1 (, line 1)"
            )
