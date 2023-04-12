import os
import shutil
from sys import platform

from seleniumbase import BaseCase

from tests.end2end.conftest import DOWNLOADED_FILES_PATH, test_environment
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
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

            screen_document_tree = Screen_DocumentTree(self)
            screen_document_tree.assert_on_screen()

            screen_document_tree.do_export_reqif()

            # FIXME: does not work on Linux CI
            if platform == "linux" or platform == "linux2":
                return

            self.sleep(test_environment.download_file_timeout_seconds)

            assert os.path.exists(path_to_expected_downloaded_file)

        assert test_setup.compare_sandbox_and_expected_output()
