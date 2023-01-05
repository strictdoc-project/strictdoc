import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.conftest import DOWNLOADED_FILES_PATH
from tests.end2end.server import SDocTestServer, DOWNLOAD_FILE_TIMEOUT

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_expected_file = os.path.join(
    path_to_this_test_file_folder, "export.expected.reqif"
)
path_to_expected_downloaded_file = os.path.join(
    DOWNLOADED_FILES_PATH, "export.reqif"
)


class Test_20_ExportTreeToReqIF(BaseCase):
    def test_01(self):
        shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)

        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "Document_1.sdoc"),
            os.path.join(path_to_sandbox, "Document_1.sdoc"),
        )
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "Document_2.sdoc"),
            os.path.join(path_to_sandbox, "Document_2.sdoc"),
        )

        test_server.run()

        self.open("http://localhost:8001")
        self.save_screenshot_to_logs()

        self.assert_text("Document 1")
        self.assert_text("Project index")

        self.click_link("Export document tree to ReqIF")

        self.sleep(DOWNLOAD_FILE_TIMEOUT)

        assert os.path.exists(path_to_expected_downloaded_file)
