import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_UC55_T02_CancelReqIFImportForm(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("PROJECT INDEX")

        self.assert_text("The document tree has no documents yet.")

        self.click_link("Import document tree from ReqIF")

        self.click_nth_visible_element("//a[contains(text(), 'Cancel')]", 1)

        self.assert_text_not_visible("Cancel")
