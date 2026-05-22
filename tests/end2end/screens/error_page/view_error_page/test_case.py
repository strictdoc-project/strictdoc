import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.error_page.screen_error_page import (
    Screen_ErrorPage,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_01_nonexistent_document_shows_404(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(
                test_server.get_host_and_port() + "/nonexistent-page.html"
            )
            screen = Screen_ErrorPage(self)
            screen.assert_on_screen()
            screen.assert_error_code(404)

    def test_02_nonexistent_asset_shows_404(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port() + "/nonexistent-file.png")
            screen = Screen_ErrorPage(self)
            screen.assert_on_screen()
            screen.assert_error_code(404)

    def test_03_no_extension_url_shows_404(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port() + "/nonexistent-path")
            screen = Screen_ErrorPage(self)
            screen.assert_on_screen()
            screen.assert_error_code(404)
