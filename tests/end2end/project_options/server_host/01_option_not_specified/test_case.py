import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        # Running this test can eventually cause conflicts when running
        # tests in parallel. Hoping that testing the server_host option is the
        # only case where we have to customize ports.
        custom_server_stderr_expectations = [
            "INFO:     Application startup complete.",
            "INFO:     Uvicorn running on http://127.0.0.1:5112 (Press CTRL+C to quit)",  # noqa: E501
        ]

        with SDocTestServer(
            input_path=path_to_this_test_file_folder,
            expectations=custom_server_stderr_expectations,
            port=5112,
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_header_project_name("Untitled Project")
