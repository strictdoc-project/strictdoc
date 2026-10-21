"""
@relation(SDOC-SRS-53, scope=file)
"""

import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_configuration.screen_project_configuration import (
    Screen_ProjectConfiguration,
)
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

            Screen_ProjectIndex(self).assert_on_screen()
            self.click('[data-testid="project-configuration-link"]')

            project_configuration = Screen_ProjectConfiguration(self)
            project_configuration.assert_on_screen()

            # Input paths: the external path prefix is hidden by default
            # and gets revealed by clicking on the "…" toggle.
            project_configuration.assert_dashboard_input_path_present()
            project_configuration.assert_dashboard_input_path_external_toggle_present()
            project_configuration.assert_dashboard_input_path_external_full_hidden()
            project_configuration.do_click_dashboard_input_path_external_toggle()
            project_configuration.assert_dashboard_input_path_external_full_visible()

            # Source root path: same reveal behavior.
            project_configuration.assert_dashboard_source_root_path_present()
            project_configuration.assert_dashboard_source_root_path_external_toggle_present()
            project_configuration.assert_dashboard_source_root_path_external_full_hidden()
            project_configuration.do_click_on_dashboard_source_root_path_external_toggle()
            project_configuration.assert_dashboard_source_root_path_external_full_visible()
