import os
import subprocess
import tempfile

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.realpath(__file__))


class Test(E2ECase):
    def test(self):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc_config.py"
        )
        assert os.path.isfile(path_to_sdoc_config)
        path_to_sdoc_input = os.path.join(
            path_to_this_test_file_folder, "input.sdoc"
        )
        assert os.path.isfile(path_to_sdoc_input)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."], check=True, cwd=path_to_repo
            )
            subprocess.run(
                ["cp", path_to_sdoc_input, "."], check=True, cwd=path_to_repo
            )
            subprocess.run(
                ["git", "init", "-b", "main"], check=True, cwd=path_to_repo
            )
            subprocess.run(
                'git config user.name "Your Name"'.split(" "),
                check=True,
                cwd=path_to_repo,
            )
            subprocess.run(
                'git config user.email "you@example.com'.split(" "),
                check=True,
                cwd=path_to_repo,
            )
            subprocess.run(["git", "add", "."], check=True, cwd=path_to_repo)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                check=True,
                cwd=path_to_repo,
            )

            with SDocTestServer(
                input_path=path_to_repo,
                cwd=path_to_repo,
            ) as test_server:
                self.open(test_server.get_host_and_port())

                screen_project_index = Screen_ProjectIndex(self)
                screen_project_index.assert_on_screen()

                git_workspace_screen = (
                    screen_project_index.do_click_on_git_workspace_screen_link()
                )
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("main")

                # "release" branches off "main" and gets a commit of its
                # own, so it is a real ancestor of "feature" below and not
                # just an alias for "main".
                git_workspace_screen.do_create_and_switch_branch("release")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("release")

                with open(
                    os.path.join(path_to_repo, "input.sdoc"),
                    "a",
                    encoding="utf8",
                ) as input_file:
                    input_file.write(
                        "\n[REQUIREMENT]\nUID: REQ-2\n"
                        "TITLE: Second requirement\n"
                        "STATEMENT: Added on release.\n"
                    )

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present("input.sdoc")
                git_workspace_screen.do_check_status_row("input.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Add REQ-2 on release"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_message(
                    "Committed the staged changes."
                )

                # "feature" branches off "release", not "main": neither
                # side of the synchronization below is "main".
                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                with open(
                    os.path.join(path_to_repo, "input.sdoc"),
                    "a",
                    encoding="utf8",
                ) as input_file:
                    input_file.write(
                        "\n[REQUIREMENT]\nUID: REQ-3\n"
                        "TITLE: Third requirement\n"
                        "STATEMENT: Added on feature.\n"
                    )

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present("input.sdoc")
                git_workspace_screen.do_check_status_row("input.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Add REQ-3 on feature"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_message(
                    "Committed the staged changes."
                )

                # The default target branch is "main" (SDOC-SRS-... default
                # fallback); explicitly point it at "release" instead, so
                # the synchronize below compares "feature" against
                # "release" -- two branches, neither of which is "main".
                git_workspace_screen.do_select_target_branch("release")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                # "feature" now carries both REQ-2 (from "release") and
                # REQ-3 (its own change), proving the merge actually
                # compared "feature" against "release".
                with open(
                    os.path.join(path_to_repo, "input.sdoc"),
                    encoding="utf8",
                ) as input_file:
                    feature_content = input_file.read()
                assert "REQ-2" in feature_content
                assert "REQ-3" in feature_content

                log_result = subprocess.run(
                    ["git", "log", "--oneline"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert "Synchronize 'feature' onto 'release'" in (
                    log_result.stdout
                )
                assert "Add REQ-2 on release" in log_result.stdout

                # "main" was never touched: it still has neither REQ-2 nor
                # REQ-3, confirming the synchronization did not silently
                # fall back to comparing against "main".
                main_content_result = subprocess.run(
                    ["git", "show", "main:input.sdoc"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                assert "REQ-2" not in main_content_result.stdout
                assert "REQ-3" not in main_content_result.stdout
