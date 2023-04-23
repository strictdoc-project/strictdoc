import os

from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_ProjectOptions_ServerHostAndPort_01_OptionNotSpecified(BaseCase):
    def test_01(self):
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

            screen_document_tree = Screen_DocumentTree(self)
            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_header_project_name("Untitled Project")
