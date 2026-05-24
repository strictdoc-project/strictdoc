import os

from selenium.webdriver.common.by import By

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

    def test_04_home_page_link_navigates_to_project_index(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            # Use a nested URL to ensure the relative-path bug is exercised:
            # without the fix, "index.html" would resolve to
            # "/nested/path/index.html" instead of "/index.html".
            self.open(
                test_server.get_host_and_port()
                + "/nested/path/nonexistent-page.html"
            )
            screen_error = Screen_ErrorPage(self)
            screen_error.assert_on_screen()
            screen_error.assert_error_code(404)
            screen_error.do_click_home_page_link()

            # Skip assert_no_js_errors(): the browser log still contains the
            # expected 404 network error from the page we just navigated away from.
            self.assert_element(
                '//body[@data-viewtype="document-tree"]', by=By.XPATH
            )
            self.wait_for_ready_state_complete()

    def test_05_nav_project_index_link_navigates_to_project_index(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            # Use a nested URL to ensure the relative-path bug is exercised:
            # without the fix, "index.html" would resolve to
            # "/nested/path/index.html" instead of "/index.html".
            self.open(
                test_server.get_host_and_port()
                + "/nested/path/nonexistent-page.html"
            )
            screen_error = Screen_ErrorPage(self)
            screen_error.assert_on_screen()
            screen_error.assert_error_code(404)
            screen_error.do_click_nav_project_index_link()

            # Skip assert_no_js_errors(): the browser log still contains the
            # expected 404 network error from the page we just navigated away from.
            self.assert_element(
                '//body[@data-viewtype="document-tree"]', by=By.XPATH
            )
            self.wait_for_ready_state_complete()
