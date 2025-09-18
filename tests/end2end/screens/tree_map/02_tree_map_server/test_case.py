"""
@relation(SDOC-SRS-155, scope=file)
"""

import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.tree_map.tree_map import Screen_TreeMap
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

            tree_map_screen: Screen_TreeMap = (
                screen_project_index.do_click_on_tree_map_screen_link()
            )
            tree_map_screen.assert_on_screen()
            tree_map_screen.assert_contains_text("Document tree map")
