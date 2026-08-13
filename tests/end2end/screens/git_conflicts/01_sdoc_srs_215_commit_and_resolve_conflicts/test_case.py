"""
@relation(SDOC-SRS-215, scope=file)
"""

import os
import subprocess
import tempfile

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.realpath(__file__))

HELLO_WORLD_MID = "05fa6a26798d43298b62bbefd18a7d6e"
HELLO_WORLD_SECTION_MID = "11111111111111111111111111111111"
HELLO_WORLD_SECTION_TEXT_MID = "22222222222222222222222222222222"


def run_git(cwd: str, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result


def write_hello_world(path_to_target_repo: str, statement: str) -> None:
    # A stable, explicit MID (document has ENABLE_MID: True) is what lets
    # the 3-way node classifier recognize base/target/incoming copies of
    # this TEXT node as "the same logical node" across branches.
    with open(
        os.path.join(path_to_target_repo, "hello_world.sdoc"),
        "w",
        encoding="utf8",
    ) as hello_world_file:
        hello_world_file.write(
            "[DOCUMENT]\nTITLE: Hello World\nOPTIONS:\n"
            "  ENABLE_MID: True\n\n"
            f"[TEXT]\nMID: {HELLO_WORLD_MID}\nSTATEMENT: >>>\n"
            f"{statement}\n<<<\n"
        )


def write_hello_world_with_section(
    path_to_target_repo: str, statement: str
) -> None:
    with open(
        os.path.join(path_to_target_repo, "hello_world.sdoc"),
        "w",
        encoding="utf8",
    ) as hello_world_file:
        hello_world_file.write(
            "[DOCUMENT]\nTITLE: Hello World\nOPTIONS:\n"
            "  ENABLE_MID: True\n\n"
            f"[[SECTION]]\nMID: {HELLO_WORLD_SECTION_MID}\nTITLE: Section\n\n"
            f"[TEXT]\nMID: {HELLO_WORLD_SECTION_TEXT_MID}\nSTATEMENT: >>>\n"
            f"{statement}\n<<<\n\n"
            "[[/SECTION]]\n"
        )


def write_hello_world_with_new_section(
    path_to_target_repo: str,
    *,
    section_mid: str,
    section_title: str,
    text_mid: str,
    statement: str,
) -> None:
    # The shared, unchanged TEXT node stays as-is; a brand-new section (own
    # MID, distinct per branch) is appended after it.
    with open(
        os.path.join(path_to_target_repo, "hello_world.sdoc"),
        "w",
        encoding="utf8",
    ) as hello_world_file:
        hello_world_file.write(
            "[DOCUMENT]\nTITLE: Hello World\nOPTIONS:\n"
            "  ENABLE_MID: True\n\n"
            f"[TEXT]\nMID: {HELLO_WORLD_MID}\nSTATEMENT: >>>\n"
            "Hello world.\n<<<\n\n"
            f"[[SECTION]]\nMID: {section_mid}\nTITLE: {section_title}\n\n"
            f"[TEXT]\nMID: {text_mid}\nSTATEMENT: >>>\n{statement}\n<<<\n\n"
            "[[/SECTION]]\n"
        )


def write_hello_world_without_section(path_to_target_repo: str) -> None:
    with open(
        os.path.join(path_to_target_repo, "hello_world.sdoc"),
        "w",
        encoding="utf8",
    ) as hello_world_file:
        hello_world_file.write(
            "[DOCUMENT]\nTITLE: Hello World\nOPTIONS:\n  ENABLE_MID: True\n"
        )


class Test(E2ECase):
    def test_sub_scenario_1_same_text_node_modified_by_both_branches(self):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc_config.py"
        )
        assert os.path.isfile(path_to_sdoc_config)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."],
                check=True,
                cwd=path_to_repo,
            )
            run_git(path_to_repo, "init", "-b", "main")
            run_git(path_to_repo, "config", "user.name", "Your Name")
            run_git(path_to_repo, "config", "user.email", "you@example.com")

            # Step 1: a project directory with documentation content
            # consisting of only one Hello World SDoc document with
            # ENABLE_MID: True.
            write_hello_world(path_to_repo, "Hello world.")
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Initial commit")

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

                # Step 2: switch to a new working branch via the UI branch
                # control (not a raw "git checkout -b").
                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                # Step 4 (sub-scenario 1) done first: "in the meantime"
                # another user modifies the same text node on main. This
                # single git repo has no real concurrency, so the other
                # user's commit is made -- and the branch switched back to
                # "feature" -- *before* our own working-tree edit below, to
                # avoid `git checkout` discarding an uncommitted change.
                run_git(path_to_repo, "checkout", "main")
                write_hello_world(path_to_repo, "Text updated by another user.")
                run_git(path_to_repo, "add", ".")
                run_git(path_to_repo, "commit", "-m", "Change by another user")
                run_git(path_to_repo, "checkout", "feature")

                # Step 3 (sub-scenario 1): the user modifies the existing
                # text node on their branch.
                write_hello_world(path_to_repo, "Text updated by our user.")

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present(
                    "hello_world.sdoc"
                )

                # Step 5: the user commits their own change under the exact
                # commit message "Change by our user".
                git_workspace_screen.do_check_status_row("hello_world.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Change by our user"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                log_result = subprocess.run(
                    ["git", "log", "--oneline"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert "Change by our user" in log_result.stdout

                # Step 5 (second)/6: select the target branch and
                # synchronize -- this lands on the Git conflict resolution
                # screen.
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")
                git_conflicts_screen.assert_conflict_present("hello_world.sdoc")
                git_conflicts_screen.assert_incoming_content(
                    "Text updated by our user."
                )
                git_conflicts_screen.assert_target_content(
                    "Text updated by another user."
                )

                # Step 7: resolve by clicking on the text node from their
                # own branch (left/incoming side). This document has a
                # single TEXT node, so the whole-document "use incoming"
                # action resolves exactly that one node.
                git_conflicts_screen.do_use_incoming("hello_world.sdoc")
                git_conflicts_screen.assert_on_screen("git_conflicts")

                # Step 8: finish the synchronization. Per SDOC-SRS-217 the
                # conflict-resolution screen's own Commit action is what
                # publishes the merge once every node is allocated -- there
                # is no second, separate "Synchronize" button click once
                # already on this screen.
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 9.
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                with open(
                    os.path.join(path_to_repo, "hello_world.sdoc"),
                    encoding="utf8",
                ) as hello_world_file:
                    assert (
                        "Text updated by our user." in hello_world_file.read()
                    )

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert status_result.stdout == ""

    def test_sub_scenario_2_independent_new_sections_placed_via_drag_and_drop(
        self,
    ):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc_config.py"
        )
        assert os.path.isfile(path_to_sdoc_config)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."],
                check=True,
                cwd=path_to_repo,
            )
            run_git(path_to_repo, "init", "-b", "main")
            run_git(path_to_repo, "config", "user.name", "Your Name")
            run_git(path_to_repo, "config", "user.email", "you@example.com")

            # Step 1: a project directory with documentation content
            # consisting of only one Hello World SDoc document with
            # ENABLE_MID: True.
            write_hello_world(path_to_repo, "Hello world.")
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Initial commit")

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

                # Step 2: switch to a new working branch via the UI.
                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                # Step 4 (sub-scenario 2) done first, same reasoning as the
                # other sub-scenarios: "in the meantime" another user
                # creates a new section with a text node on main -- done
                # and switched back before our own working-tree edit, to
                # avoid `git checkout` discarding an uncommitted change.
                run_git(path_to_repo, "checkout", "main")
                write_hello_world_with_new_section(
                    path_to_repo,
                    section_mid="33333333333333333333333333333333",
                    section_title="Main Section",
                    text_mid="44444444444444444444444444444444",
                    statement="Added by another user.",
                )
                run_git(path_to_repo, "add", ".")
                run_git(path_to_repo, "commit", "-m", "Change by another user")
                run_git(path_to_repo, "checkout", "feature")

                # Step 3 (sub-scenario 2): the user creates a new section
                # with a text node on their own branch.
                write_hello_world_with_new_section(
                    path_to_repo,
                    section_mid="55555555555555555555555555555555",
                    section_title="Feature Section",
                    text_mid="66666666666666666666666666666666",
                    statement="Added by our user.",
                )

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present(
                    "hello_world.sdoc"
                )

                # Step 5: commit our own change under the exact commit
                # message "Change by our user".
                git_workspace_screen.do_check_status_row("hello_world.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Change by our user"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 5 (second)/6: select the target branch and
                # synchronize. Both branches' new sections are independent,
                # non-conflicting additions -- they auto-merge in
                # immediately (0 conflicts), in a fixed default order
                # (target's own new section first, incoming's last).
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")
                git_conflicts_screen.assert_incoming_content(
                    "Added by our user."
                )
                git_conflicts_screen.assert_target_content(
                    "Added by another user."
                )

                # Step 7 (sub-scenario 2's drag variant): drag the left
                # (incoming) new section to be positioned right after the
                # shared, unchanged text node (#0) -- ahead of target's own
                # new section (#1/#2), i.e. a real reordering, not the
                # already-below default. Node keys follow document order:
                # #0 shared TEXT, #1/#2 target's new section+text, #3/#4
                # incoming's new section+text.
                git_conflicts_screen.do_drag_node_after(
                    "hello_world.sdoc#3", "hello_world.sdoc#0"
                )
                git_conflicts_screen.assert_on_screen("git_conflicts")

                # Step 8.
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 9.
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                with open(
                    os.path.join(path_to_repo, "hello_world.sdoc"),
                    encoding="utf8",
                ) as hello_world_file:
                    content = hello_world_file.read()
                    assert "Added by our user." in content
                    assert "Added by another user." in content
                    # The drag placed incoming's section ahead of target's.
                    assert content.index("Added by our user.") < content.index(
                        "Added by another user."
                    )

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert status_result.stdout == ""

    def test_sub_scenario_3_independent_neighboring_section_deletions(self):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc_config.py"
        )
        assert os.path.isfile(path_to_sdoc_config)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."],
                check=True,
                cwd=path_to_repo,
            )
            run_git(path_to_repo, "init", "-b", "main")
            run_git(path_to_repo, "config", "user.name", "Your Name")
            run_git(path_to_repo, "config", "user.email", "you@example.com")

            def write_two_sections(
                section_a_present: bool, section_b_present: bool
            ) -> None:
                content = (
                    "[DOCUMENT]\nTITLE: Hello World\nOPTIONS:\n"
                    "  ENABLE_MID: True\n\n"
                    f"[TEXT]\nMID: {HELLO_WORLD_MID}\nSTATEMENT: >>>\n"
                    "Hello world.\n<<<\n"
                )
                if section_a_present:
                    content += (
                        "\n[[SECTION]]\nMID: 77777777777777777777777777777777\n"
                        "TITLE: Section A\n\n"
                        "[TEXT]\nMID: 88888888888888888888888888888888\n"
                        "STATEMENT: >>>\nSection A text.\n<<<\n\n"
                        "[[/SECTION]]\n"
                    )
                if section_b_present:
                    content += (
                        "\n[[SECTION]]\nMID: 99999999999999999999999999999999\n"
                        "TITLE: Section B\n\n"
                        "[TEXT]\nMID: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
                        "STATEMENT: >>>\nSection B text.\n<<<\n\n"
                        "[[/SECTION]]\n"
                    )
                with open(
                    os.path.join(path_to_repo, "hello_world.sdoc"),
                    "w",
                    encoding="utf8",
                ) as hello_world_file:
                    hello_world_file.write(content)

            # Step 1: base content -- the Hello World text plus two
            # neighboring sections, one of which each branch will delete.
            write_two_sections(True, True)
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Initial commit")

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

                # Step 2: switch to a new working branch via the UI.
                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                # Step 4 (sub-scenario 3) done first: "in the meantime"
                # another user removes Section B on main.
                run_git(path_to_repo, "checkout", "main")
                write_two_sections(True, False)
                run_git(path_to_repo, "add", ".")
                run_git(path_to_repo, "commit", "-m", "Change by another user")
                run_git(path_to_repo, "checkout", "feature")

                # Step 3 (sub-scenario 3): the user removes Section A (the
                # neighbor) on their own branch.
                write_two_sections(False, True)

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present(
                    "hello_world.sdoc"
                )

                # Step 5: commit our own change under the exact commit
                # message "Change by our user".
                git_workspace_screen.do_check_status_row("hello_world.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Change by our user"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 5 (second)/6: select the target branch and
                # synchronize. Deleting two *different* neighboring
                # sections is not a conflict (only one side ever touched
                # each section) -- both deletions auto-merge in with 0
                # true conflicts, straight to a Commit-ready review screen.
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")

                # Step 8 (no step 7 needed -- nothing to resolve).
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 9.
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                with open(
                    os.path.join(path_to_repo, "hello_world.sdoc"),
                    encoding="utf8",
                ) as hello_world_file:
                    content = hello_world_file.read()
                    assert "Hello world." in content
                    assert "Section A text." not in content
                    assert "Section B text." not in content

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert status_result.stdout == ""

    def test_sub_scenario_4_independent_new_documents_both_survive(self):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc_config.py"
        )
        assert os.path.isfile(path_to_sdoc_config)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."],
                check=True,
                cwd=path_to_repo,
            )
            run_git(path_to_repo, "init", "-b", "main")
            run_git(path_to_repo, "config", "user.name", "Your Name")
            run_git(path_to_repo, "config", "user.email", "you@example.com")

            # Step 1: a project directory with documentation content
            # consisting of only one Hello World SDoc document with
            # ENABLE_MID: True.
            write_hello_world(path_to_repo, "Hello world.")
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Initial commit")

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

                # Step 2: switch to a new working branch via the UI.
                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                # Step 4 (sub-scenario 4) done first, same reasoning as the
                # other sub-scenarios: "in the meantime" another user
                # creates a whole new document on main -- done and
                # switched back before our own working-tree edit, to avoid
                # `git checkout` discarding an uncommitted change.
                run_git(path_to_repo, "checkout", "main")
                with open(
                    os.path.join(path_to_repo, "main_doc.sdoc"),
                    "w",
                    encoding="utf8",
                ) as main_file:
                    main_file.write(
                        "[DOCUMENT]\nTITLE: Main Doc\n\n"
                        "[TEXT]\nSTATEMENT: >>>\nAdded by another user.\n<<<\n"
                    )
                run_git(path_to_repo, "add", ".")
                run_git(path_to_repo, "commit", "-m", "Change by another user")
                run_git(path_to_repo, "checkout", "feature")

                # Step 3 (sub-scenario 4): the user creates a whole new
                # document on their own branch.
                with open(
                    os.path.join(path_to_repo, "feature_doc.sdoc"),
                    "w",
                    encoding="utf8",
                ) as feature_file:
                    feature_file.write(
                        "[DOCUMENT]\nTITLE: Feature Doc\n\n"
                        "[TEXT]\nSTATEMENT: >>>\nAdded by our user.\n<<<\n"
                    )

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present(
                    "feature_doc.sdoc"
                )

                # Step 5: commit our own change under the exact commit
                # message "Change by our user".
                git_workspace_screen.do_check_status_row("feature_doc.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Change by our user"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 5 (second)/6: select the target branch and
                # synchronize. Two whole new, unrelated documents are not
                # a conflict at all -- both auto-merge in with 0 true
                # conflicts, straight to a Commit-ready review screen.
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")

                # Step 8 (no step 7 needed -- nothing to resolve).
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 9.
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                assert os.path.isfile(
                    os.path.join(path_to_repo, "feature_doc.sdoc")
                )
                assert os.path.isfile(
                    os.path.join(path_to_repo, "main_doc.sdoc")
                )

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert status_result.stdout == ""

    def test_sub_scenario_5_independent_document_deletions_both_removed(
        self,
    ):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc_config.py"
        )
        assert os.path.isfile(path_to_sdoc_config)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."],
                check=True,
                cwd=path_to_repo,
            )
            run_git(path_to_repo, "init", "-b", "main")
            run_git(path_to_repo, "config", "user.name", "Your Name")
            run_git(path_to_repo, "config", "user.email", "you@example.com")

            # Step 1: base content -- the Hello World text plus two
            # separate documents, one of which each branch will delete.
            # These use a UID-tagged REQUIREMENT (not TEXT): a node kept
            # unchanged by one side still needs to be *matched* back to
            # its base copy for the classifier to recognize "only the
            # other side deleted it, this side never touched it" -- and
            # TEXT has no title/UID for that matching to fall back on.
            write_hello_world(path_to_repo, "Hello world.")
            for name, uid, statement in (
                ("doc_a.sdoc", "DOC_A_REQ", "Doc A text."),
                ("doc_b.sdoc", "DOC_B_REQ", "Doc B text."),
            ):
                with open(
                    os.path.join(path_to_repo, name), "w", encoding="utf8"
                ) as doc_file:
                    doc_file.write(
                        f"[DOCUMENT]\nTITLE: {name}\n\n"
                        f"[REQUIREMENT]\nUID: {uid}\nSTATEMENT: {statement}\n"
                    )
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Initial commit")

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

                # Step 2: switch to a new working branch via the UI.
                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                # Step 4 (sub-scenario 5) done first: "in the meantime"
                # another user removes doc_b.sdoc on main.
                run_git(path_to_repo, "checkout", "main")
                run_git(path_to_repo, "rm", "doc_b.sdoc")
                run_git(path_to_repo, "commit", "-m", "Change by another user")
                run_git(path_to_repo, "checkout", "feature")

                # Step 3 (sub-scenario 5): the user removes doc_a.sdoc on
                # their own branch. Plain filesystem removal, not `git rm`
                # -- this leaves the deletion *unstaged*, matching a real
                # user deleting the file and then using Stage in the UI
                # (git rm would pre-stage it, and re-staging an
                # already-staged deletion via `git add` fails outright:
                # "pathspec did not match any files", since there is
                # nothing left on disk for the pathspec to match).
                os.remove(os.path.join(path_to_repo, "doc_a.sdoc"))

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present("doc_a.sdoc")

                # Step 5: commit our own change under the exact commit
                # message "Change by our user".
                git_workspace_screen.do_check_status_row("doc_a.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Change by our user"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 5 (second)/6: select the target branch and
                # synchronize. Deleting two *different* documents is not a
                # conflict -- both deletions auto-merge in with 0 true
                # conflicts, straight to a Commit-ready review screen.
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")

                # Step 8 (no step 7 needed -- nothing to resolve).
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 9.
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                # Both documents must be entirely gone, not merely
                # emptied.
                assert not os.path.exists(
                    os.path.join(path_to_repo, "doc_a.sdoc")
                )
                assert not os.path.exists(
                    os.path.join(path_to_repo, "doc_b.sdoc")
                )
                assert os.path.isfile(
                    os.path.join(path_to_repo, "hello_world.sdoc")
                )

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert status_result.stdout == ""

    def test_sub_scenario_6_text_node_in_section_modified_while_section_deleted(
        self,
    ):
        path_to_sdoc_config = os.path.join(
            path_to_this_test_file_folder, "strictdoc_config.py"
        )
        assert os.path.isfile(path_to_sdoc_config)

        with tempfile.TemporaryDirectory() as path_to_temp_folder_:
            real_path_to_temp_folder = os.path.realpath(path_to_temp_folder_)
            path_to_repo = os.path.join(real_path_to_temp_folder, "repo")
            os.mkdir(path_to_repo)

            subprocess.run(
                ["cp", path_to_sdoc_config, "."],
                check=True,
                cwd=path_to_repo,
            )
            run_git(path_to_repo, "init", "-b", "main")
            run_git(path_to_repo, "config", "user.name", "Your Name")
            run_git(path_to_repo, "config", "user.email", "you@example.com")

            # Step 1: a project directory with documentation content
            # consisting of only one Hello World SDoc document with
            # ENABLE_MID: True -- here with a section around the text node,
            # as sub-scenario 6 needs something to delete on one side while
            # the text node inside it is modified on the other.
            write_hello_world_with_section(path_to_repo, "Hello world.")
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Initial commit")

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

                # Step 2: switch to a new working branch via the UI branch
                # control.
                git_workspace_screen.do_create_and_switch_branch("feature")
                git_workspace_screen.assert_on_screen("git_workspace")
                git_workspace_screen.assert_current_branch("feature")

                # Step 4 (sub-scenario 6) done first, same reasoning as
                # sub-scenario 1: "in the meantime" another user deletes the
                # entire section on main -- done and switched back before
                # our own working-tree edit, to avoid `git checkout`
                # discarding an uncommitted change.
                run_git(path_to_repo, "checkout", "main")
                write_hello_world_without_section(path_to_repo)
                run_git(path_to_repo, "add", ".")
                run_git(path_to_repo, "commit", "-m", "Change by another user")
                run_git(path_to_repo, "checkout", "feature")

                # Step 3 (sub-scenario 6): the user modifies the existing
                # text node inside the section on their branch.
                write_hello_world_with_section(
                    path_to_repo, "Text updated by our user."
                )

                self.open(test_server.get_host_and_port() + "/git_workspace")
                git_workspace_screen.assert_status_row_present(
                    "hello_world.sdoc"
                )

                # Step 5: commit our own change under the exact commit
                # message "Change by our user".
                git_workspace_screen.do_check_status_row("hello_world.sdoc")
                git_workspace_screen.do_stage_selected()
                git_workspace_screen.do_fill_in_commit_message(
                    "Change by our user"
                )
                git_workspace_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                log_result = subprocess.run(
                    ["git", "log", "--oneline"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert "Change by our user" in log_result.stdout

                # Step 5 (second)/6: select the target branch and
                # synchronize -- this is a delete/modify conflict (the
                # section was deleted on target while a node inside it was
                # modified on incoming), not a plain true conflict.
                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")
                git_conflicts_screen.assert_conflict_present("hello_world.sdoc")
                git_conflicts_screen.assert_incoming_content(
                    "Text updated by our user."
                )

                # Step 7: resolve by clicking on the text node from their
                # own branch (left/incoming side) -- restores the deleted
                # section together with the modified node inside it.
                git_conflicts_screen.do_use_incoming("hello_world.sdoc")
                git_conflicts_screen.assert_on_screen("git_conflicts")

                # Step 8.
                git_conflicts_screen.do_commit()
                git_workspace_screen.assert_on_screen("git_workspace")

                # Step 9.
                git_workspace_screen.assert_message(
                    "Synchronization finished: rebased onto"
                )

                with open(
                    os.path.join(path_to_repo, "hello_world.sdoc"),
                    encoding="utf8",
                ) as hello_world_file:
                    content = hello_world_file.read()
                    assert "[[SECTION]]" in content
                    assert "Text updated by our user." in content

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path_to_repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert status_result.stdout == ""
