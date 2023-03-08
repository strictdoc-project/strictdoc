import os
import shutil
from sys import platform

from seleniumbase import BaseCase

from tests.end2end.conftest import DOWNLOAD_FILE_TIMEOUT, DOWNLOADED_FILES_PATH
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_expected_downloaded_file = os.path.join(
    DOWNLOADED_FILES_PATH, "export.reqif"
)


class Test_UC20_T1_GreenCase(BaseCase):
    def test_01(self):
        shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)

        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen()
            screen_document.assert_is_document_title("Document 1")
            screen_document.assert_text("Hello world!")

            # TODO
            shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)
            assert not os.path.exists(path_to_expected_downloaded_file)

            screen_document.do_export_reqif()

            # FIXME: does not work on Linux CI
            if platform == "linux" or platform == "linux2":
                return
            self.sleep(DOWNLOAD_FILE_TIMEOUT)
            assert os.path.exists(path_to_expected_downloaded_file)
