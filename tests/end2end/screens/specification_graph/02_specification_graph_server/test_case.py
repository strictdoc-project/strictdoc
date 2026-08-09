import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.specification_graph.specification_graph import (
    Screen_SpecificationGraph,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_uid(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            specification_graph_screen: Screen_SpecificationGraph = (
                screen_project_index.do_click_on_specification_graph_screen_link()
            )
            specification_graph_screen.assert_on_screen()
            # The title is wrapped across two <tspan> lines inside the SVG
            # (see svg_renderer.py), so only assert on a substring that is
            # guaranteed to land on a single line.
            specification_graph_screen.assert_contains_text(
                "Specification Graph"
            )
