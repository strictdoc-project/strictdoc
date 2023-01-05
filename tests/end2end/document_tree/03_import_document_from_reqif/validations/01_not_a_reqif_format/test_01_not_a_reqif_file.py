import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_Validation_01_NotAReqIFormat(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        test_server.run()

        self.open("http://localhost:8001")

        self.assert_text("Project index")

        self.assert_text("The document tree has no documents yet.")

        self.click_link("Import document tree from ReqIF")

        reqif_input_field = self.find_element("#reqif_file")
        reqif_input_field.send_keys(path_to_reqif_sample)
        self.click_xpath("//button[@type='submit' and text()='Import ReqIF']")

        self.assert_text(
            "Cannot parse ReqIF file: "
            "Start tag expected, '<' not found, line 1, column 1 (, line 1)"
        )
