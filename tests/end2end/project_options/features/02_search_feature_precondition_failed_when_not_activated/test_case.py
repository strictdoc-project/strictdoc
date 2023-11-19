import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            path_to_search = test_server.get_host_and_port() + "/search"
            self.open(path_to_search)

            self.assert_text(
                "The Search feature is not activated in the project config."
            )
