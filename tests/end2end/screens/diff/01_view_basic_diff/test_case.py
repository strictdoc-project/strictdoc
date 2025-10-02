import os
import subprocess
import tempfile

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.diff.diff import Screen_Diff
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.realpath(__file__))


class Test(E2ECase):
    def test(self):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc.toml"
        )
        assert os.path.isfile(path_to_sdoc_config)
        path_to_sdoc_input = os.path.join(
            path_to_this_test_file_folder, "input.sdoc"
        )
        assert os.path.isfile(path_to_sdoc_input)
        path_to_sdoc_input_delta = os.path.join(
            path_to_this_test_file_folder, "input_delta.sdoc"
        )
        assert os.path.isfile(path_to_sdoc_input_delta)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            # It is important that realpath is used because macOS symlinks
            # /var → /private/var, so $TMPDIR is actually:
            # '/private/var/folders/sy/_sd67yzn5td5flr2_6vf73w40000gp/T/'.
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."],
                check=True,
                cwd=real_path_to_temp_folder,
            )
            subprocess.run(
                ["cp", path_to_sdoc_input, "."],
                check=True,
                cwd=real_path_to_temp_folder,
            )
            subprocess.run(
                ["git", "init"], check=True, cwd=real_path_to_temp_folder
            )
            subprocess.run(
                'git config user.name "Your Name"'.split(" "),
                check=True,
                cwd=real_path_to_temp_folder,
            )
            subprocess.run(
                'git config user.email "you@example.com'.split(" "),
                check=True,
                cwd=real_path_to_temp_folder,
            )
            subprocess.run(
                ["git", "add", "."], check=True, cwd=real_path_to_temp_folder
            )
            subprocess.run(
                ["git", "commit", "-m", "Test commit #1"],
                check=True,
                cwd=real_path_to_temp_folder,
            )

            subprocess.run(
                ["cp", path_to_sdoc_input_delta, "input.sdoc"],
                check=True,
                cwd=real_path_to_temp_folder,
            )
            subprocess.run(
                ["git", "add", "."], check=True, cwd=real_path_to_temp_folder
            )
            subprocess.run(
                ["git", "commit", "-m", "Test commit #2"],
                check=True,
                cwd=real_path_to_temp_folder,
            )

            with SDocTestServer(
                input_path=real_path_to_temp_folder,
                cwd=real_path_to_temp_folder,
            ) as test_server:
                self.open(test_server.get_host_and_port())

                screen_project_index = Screen_ProjectIndex(self)
                screen_project_index.assert_on_screen()
                screen_project_index.assert_link_to_diff_screen_present()

                diff_screen: Screen_Diff = (
                    screen_project_index.do_click_on_diff_screen_link()
                )
                diff_screen.assert_on_screen("diff")

                diff_screen.do_enter_field_lhs("HEAD^")
                diff_screen.do_enter_field_rhs("HEAD")
                diff_screen.do_submit()

                self.assert_text("Test document")
                self.assert_text("Modified test document")

                diff_screen.do_switch_tab_to_changelog()
                diff_screen.assert_documents_modified("1")
                diff_screen.assert_nodes_modified("SECTION", "1 (1 modified)")
                diff_screen.assert_nodes_modified(
                    "TEXT", "No nodes were modified."
                )
                diff_screen.assert_nodes_modified(
                    "REQUIREMENT", "2 (1 modified, 1 added)"
                )
