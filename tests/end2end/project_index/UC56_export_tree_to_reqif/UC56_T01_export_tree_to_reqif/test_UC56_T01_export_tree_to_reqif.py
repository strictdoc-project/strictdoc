import os
import shutil
from sys import platform

from seleniumbase import BaseCase

from tests.end2end.conftest import DOWNLOADED_FILES_PATH, test_environment
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_expected_downloaded_file = os.path.join(
    DOWNLOADED_FILES_PATH, "export.reqif"
)


class Test_UC56_T01_ExportTreeToReqIF(BaseCase):
    def test(self):
        shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)

        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_project_index.do_export_reqif()

            # FIXME: does not work on Linux CI
            if platform == "linux" or platform == "linux2":
                return

            self.sleep(test_environment.download_file_timeout_seconds)

            assert os.path.exists(path_to_expected_downloaded_file)

        assert test_setup.compare_sandbox_and_expected_output()
