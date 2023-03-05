import os
import shutil
from sys import platform

from seleniumbase import BaseCase

from tests.end2end.conftest import DOWNLOAD_FILE_TIMEOUT, DOWNLOADED_FILES_PATH
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.server import SDocTestServer

path_to_expected_downloaded_file = os.path.join(
    DOWNLOADED_FILES_PATH, "export.reqif"
)


class Test_UC56_T01_ExportTreeToReqIF(BaseCase):
    def test_01(self):
        shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)

        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("Document 1")
            self.assert_text("PROJECT INDEX")

            self.click('[data-testid="tree-export-reqif-action"]')
            # FIXME: does not work on Linux CI
            if platform == "linux" or platform == "linux2":
                return

            self.sleep(DOWNLOAD_FILE_TIMEOUT)

            assert os.path.exists(path_to_expected_downloaded_file)

        assert test_setup.compare_sandbox_and_expected_output()
