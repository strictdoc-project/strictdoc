import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer
from tests.end2end.test_helpers import available_systems

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


# FIXME: It is not clear what prevents a specific version of macOS fail on GitHub Actions.
@available_systems(["linux", "windows"])
class Test(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            with open(
                test_server.path_to_out_log, encoding="utf8"
            ) as out_log_file:
                logs = out_log_file.read()
            assert '"GET / HTTP/1.1" 200 OK' not in logs
            assert '"GET / HTTP/1.1" 304 Not Modified' not in logs
            assert '"GET /_static/turbo.js HTTP/1.1" 200 OK' not in logs
            assert (
                '"GET /_static/turbo.js HTTP/1.1" 304 Not Modified' not in logs
            )

            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            with open(
                test_server.path_to_out_log, encoding="utf8"
            ) as out_log_file:
                logs = out_log_file.read()

            assert '"GET / HTTP/1.1" 200 OK' in logs
            assert '"GET / HTTP/1.1" 304 Not Modified' not in logs
            assert '"GET /_static/turbo.min.js HTTP/1.1" 200 OK' in logs
            assert (
                '"GET /_static/turbo.min.js HTTP/1.1" 304 Not Modified'
                not in logs
            )

            # Opening for the second time should result in 304 records in the log.
            self.open(test_server.get_host_and_port())

            with open(
                test_server.path_to_out_log, encoding="utf8"
            ) as out_log_file:
                logs = out_log_file.read()

            # The HTML pages as well as the assets get cached.
            assert '"GET / HTTP/1.1" 200 OK' in logs
            assert '"GET / HTTP/1.1" 304 Not Modified' in logs
            assert '"GET /_static/turbo.min.js HTTP/1.1" 200 OK' in logs
            assert (
                '"GET /_static/turbo.min.js HTTP/1.1" 304 Not Modified' in logs
            )
