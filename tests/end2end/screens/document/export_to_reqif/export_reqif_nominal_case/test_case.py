import filecmp
import os
import shutil
import sys

from tests.end2end.conftest import DOWNLOADED_FILES_PATH, test_environment
from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_exported_downloaded_file = os.path.join(
    DOWNLOADED_FILES_PATH, "export.reqif"
)
path_to_expected_downloaded_file = os.path.join(
    path_to_this_test_file_folder, "export.expected.reqif"
)


class Test(E2ECase):
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

            shutil.rmtree(DOWNLOADED_FILES_PATH, ignore_errors=True)
            assert not os.path.exists(path_to_exported_downloaded_file)

            screen_document.do_export_reqif()

            # FIXME: does not work on Linux CI
            if sys.platform.startswith("linux"):
                return
            self.sleep(test_environment.download_file_timeout_seconds)
            assert os.path.exists(path_to_exported_downloaded_file)

            # FIXME: Activate this check when the exported ReqIF identifiers
            #        are stable.
            if False and not filecmp.cmp(
                path_to_exported_downloaded_file,
                path_to_expected_downloaded_file,
            ):
                diff = End2EndTestSetup.get_diff(
                    path_to_exported_downloaded_file,
                    path_to_expected_downloaded_file,
                )
                raise AssertionError(
                    f"Test-produced and expected files are not identical:\n"
                    f"{path_to_exported_downloaded_file}\n"
                    f"{path_to_expected_downloaded_file}\n"
                    "Diff:\n"
                    f"{diff}"
                )
