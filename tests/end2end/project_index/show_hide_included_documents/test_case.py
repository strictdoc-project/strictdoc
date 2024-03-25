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

            screen_project_index.assert_project_tree_controls_present()
            screen_project_index.assert_contains_document("Including document")
            screen_project_index.assert_document_is_hidden("Fragment")
            # show
            screen_project_index.do_click_on_fragment_switcher()
            screen_project_index.assert_contains_document("Fragment")
            # hide
            screen_project_index.do_click_on_fragment_switcher()
            screen_project_index.assert_document_is_hidden("Fragment")
