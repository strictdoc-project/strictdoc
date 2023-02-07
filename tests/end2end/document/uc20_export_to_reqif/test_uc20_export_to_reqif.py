import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.conftest import DOWNLOADED_FILES_PATH
from tests.end2end.server import SDocTestServer, DOWNLOAD_FILE_TIMEOUT

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_expected_downloaded_file = os.path.join(
    DOWNLOADED_FILES_PATH, "export.reqif"
)


class Test_UC20_ExportToReqIF(BaseCase):
    def test_01(self):
        shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)

        test_server = SDocTestServer(input_path=path_to_this_test_file_folder)
        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("Document 1")
        self.assert_text("PROJECT INDEX")

        self.click_link("DOC")

        self.assert_text("Hello world!")

        shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)
        assert not os.path.exists(path_to_expected_downloaded_file)

        self.click_link("Export to ReqIF")
        self.sleep(DOWNLOAD_FILE_TIMEOUT)
        assert os.path.exists(path_to_expected_downloaded_file)
