import os
import shutil
from sys import platform

from seleniumbase import BaseCase

from tests.end2end.conftest import DOWNLOADED_FILES_PATH, test_environment
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_expected_downloaded_file = os.path.join(
    DOWNLOADED_FILES_PATH, "export.reqif"
)


class Test_UC20_T1_GreenCase(BaseCase):
    def test(self):
        shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)

        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_text("Hello world!")

            # TODO
            shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)
            assert not os.path.exists(path_to_expected_downloaded_file)

            screen_document.do_export_reqif()

            # FIXME: does not work on Linux CI
            if platform == "linux" or platform == "linux2":
                return
            self.sleep(test_environment.download_file_timeout_seconds)
            assert os.path.exists(path_to_expected_downloaded_file)
