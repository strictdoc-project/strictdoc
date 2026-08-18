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
            path_to_remote = os.path.join(
                real_path_to_temp_folder, "remote.git"
            )
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["git", "init", "--bare", "-b", "main", path_to_remote],
                check=True,
                cwd=real_path_to_temp_folder,
            )

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
            subprocess.run(
                ["git", "remote", "add", "origin", path_to_remote],
                check=True,
                cwd=path_to_repo,
            )
            subprocess.run(
                ["git", "push", "-u", "origin", "main"],
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
                screen_project_index.assert_link_to_git_workspace_screen_present()

                git_workspace_screen = (
                    screen_project_index.do_click_on_git_workspace_screen_link()
                )
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("main")

                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                # Simulate the user editing documentation content: a file
                # changes on disk while the server is running, exactly as a
                # real document save would leave it.
                with open(
                    os.path.join(path_to_repo, "input.sdoc"),
                    "a",
                    encoding="utf8",
                ) as input_file:
                    input_file.write(
                        "\n[REQUIREMENT]\nUID: REQ-2\n"
                        "TITLE: Second requirement\n"
                        "STATEMENT: Second statement.\n"
                    )

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present("input.sdoc")

                git_workspace_screen.do_check_status_row("input.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.assert_on_screen("git_workspace")

                git_workspace_screen.do_fill_in_commit_message(
                    "Add second requirement"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_message(
                    "Committed the staged changes."
                )

                log_result = subprocess.run(
                    ["git", "log", "--oneline"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert "Add second requirement" in log_result.stdout

                # Synchronize (onto "main", the default target branch) is a
                # pure merge -- it must not push anywhere on its own. Per
                # SDOC-SRS-217, it always lands on the review screen by
                # default, even though there's nothing to actually resolve
                # here; the user must explicitly commit to finish.
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                # SDOC-SRS-222: a completed synchronization is never a
                # terminal state -- Synchronize must still be usable
                # immediately, before ever pushing (e.g. "main" moves
                # again while the user is still working). Drive a second
                # full Synchronize -> Commit cycle here, with no Push in
                # between, and confirm it isn't blocked.
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                remote_branches_before_push = subprocess.run(
                    ["git", "branch", "-r"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert (
                    "origin/feature" not in remote_branches_before_push.stdout
                )

                # Pushing is a separate, explicit step.
                git_workspace_screen.do_push()
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_message(
                    "Pushed the branch to its remote."
                )

                remote_branches_result = subprocess.run(
                    ["git", "branch", "-r"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert "origin/feature" in remote_branches_result.stdout
