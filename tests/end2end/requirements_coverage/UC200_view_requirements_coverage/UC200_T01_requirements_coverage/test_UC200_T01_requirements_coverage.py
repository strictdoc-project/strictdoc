import os

from seleniumbase import BaseCase

from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.requirements_coverage.screen_requirements_coverage import (  # noqa: E501
    Screen_RequirementsCoverage,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC200_T01_ViewRequirementsCoverage(BaseCase):
    def test_01(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_link_to_requirements_coverage_present()

            screen_requirements_coverage: Screen_RequirementsCoverage = (
                screen_project_index.do_click_on_requirements_coverage_link()
            )
            screen_requirements_coverage.assert_on_screen()
