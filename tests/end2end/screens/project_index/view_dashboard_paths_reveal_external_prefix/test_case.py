"""
@relation(SDOC-SRS-53, scope=file)
"""

import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            # Input paths: the external path prefix is hidden by default
            # and gets revealed by clicking on the "…" toggle.
            screen_project_index.assert_dashboard_input_path_present()
            screen_project_index.assert_dashboard_input_path_external_toggle_present()
            screen_project_index.assert_dashboard_input_path_external_full_hidden()
            screen_project_index.do_click_on_dashboard_input_path_external_toggle()
            screen_project_index.assert_dashboard_input_path_external_full_visible()

            # Source root path: same reveal behavior.
            screen_project_index.assert_dashboard_source_root_path_present()
            screen_project_index.assert_dashboard_source_root_path_external_toggle_present()
            screen_project_index.assert_dashboard_source_root_path_external_full_hidden()
            screen_project_index.do_click_on_dashboard_source_root_path_external_toggle()
            screen_project_index.assert_dashboard_source_root_path_external_full_visible()
