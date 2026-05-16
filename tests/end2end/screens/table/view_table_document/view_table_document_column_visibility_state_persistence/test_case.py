from urllib.parse import urlparse, urlunparse

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            # Clear localStorage before navigating to table view.
            # Tests run with --reuse-session (shared browser), so localStorage
            # persists across test cases. Clearing here ensures the table JS
            # starts with no saved state — this test explicitly controls what
            # goes into storage as part of verifying the persistence mechanism.
            self.execute_script("localStorage.clear()")

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            # Hide "Type" via the toolbar — URL gets ?hidden=Type
            screen_table.do_open_toolbar_panel()
            screen_table.do_toggle_column("Type")
            self.assert_url_contains("hidden=Type")
            screen_table.assert_column_header_hidden("Type")

            # Get base URL without query params or fragment
            current_url = self.get_current_url()
            parsed = urlparse(current_url)
            clean_url = urlunparse(parsed._replace(query="", fragment=""))

            # Navigate to the clean URL — state must be restored from localStorage
            self.open(clean_url)
            screen_table.assert_on_screen_table()
            screen_table.assert_column_header_hidden("Type")
            # URL should reflect the storage state
            self.assert_url_contains("hidden=Type")

        assert test_setup.compare_sandbox_and_expected_output()
