"""
@relation(SDOC-SRS-221, scope=file)
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


def run_git(cwd: str, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result


def write_document(
    path_to_target_repo: str,
    *,
    auto_statement: str,
    conflict_statement: str,
    nested_statement: str,
) -> None:
    # UIDs are required for the 3-way node classifier to recognize
    # base/target/incoming copies of these nodes as "the same logical
    # node" (matched by MID, then UID, then title/content similarity --
    # never by STATEMENT alone).
    with open(
        os.path.join(path_to_target_repo, "requirement.sdoc"),
        "w",
        encoding="utf8",
    ) as requirement_file:
        requirement_file.write(
            "[DOCUMENT]\nTITLE: Test\n\n"
            "[REQUIREMENT]\nUID: REQ_UNCHANGED\n"
            "STATEMENT: Same everywhere.\n\n"
            f"[REQUIREMENT]\nUID: REQ_AUTO\nSTATEMENT: {auto_statement}\n\n"
            "[REQUIREMENT]\nUID: REQ_CONFLICT\n"
            f"STATEMENT: {conflict_statement}\n\n"
            "[[SECTION]]\nUID: SEC_UNCHANGED_WRAPPER\n"
            "TITLE: Section wrapping a change\n\n"
            "[REQUIREMENT]\nUID: REQ_IN_SECTION\n"
            f"STATEMENT: {nested_statement}\n\n"
            "[[/SECTION]]\n"
        )


class Test(E2ECase):
    def test_modified_nodes_expanded_unchanged_nodes_collapsed(self):
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

            # Base: everything at its starting value.
            write_document(
                path_to_repo,
                auto_statement="Base.",
                conflict_statement="Base conflict.",
                nested_statement="Base nested.",
            )
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Initial commit")

            run_git(path_to_repo, "checkout", "-b", "feature")
            run_git(path_to_repo, "checkout", "main")

            # Target ("main") independently changes only REQ_CONFLICT --
            # this, together with feature's own change to the same node
            # below, is what makes REQ_CONFLICT a true conflict. REQ_AUTO
            # and REQ_IN_SECTION are left untouched on this side, so their
            # eventual changes on "feature" auto-merge cleanly.
            write_document(
                path_to_repo,
                auto_statement="Base.",
                conflict_statement="Main version.",
                nested_statement="Base nested.",
            )
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Main change")
            run_git(path_to_repo, "checkout", "feature")

            # Feature changes REQ_UNCHANGED nowhere (stays identical to
            # base and target), changes REQ_AUTO and REQ_IN_SECTION (the
            # only side to touch them, so they auto-merge), and changes
            # REQ_CONFLICT differently than target did (a true conflict).
            write_document(
                path_to_repo,
                auto_statement="Incoming auto.",
                conflict_statement="Feature version.",
                nested_statement="Incoming nested.",
            )
            run_git(path_to_repo, "add", ".")
            run_git(path_to_repo, "commit", "-m", "Feature change")

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

                git_conflicts_screen = git_workspace_screen.do_sync()
                git_conflicts_screen.assert_on_screen("git_conflicts")
                git_conflicts_screen.assert_conflict_present("requirement.sdoc")

                # Node keys follow the document's node order, assigned
                # sequentially by the classifier: REQ_UNCHANGED (#0),
                # REQ_AUTO (#1), REQ_CONFLICT (#2), the wrapping SECTION
                # (#3), REQ_IN_SECTION (#4).
                git_conflicts_screen.assert_node_collapsed("requirement.sdoc#0")
                git_conflicts_screen.assert_node_expanded("requirement.sdoc#1")
                git_conflicts_screen.assert_node_expanded("requirement.sdoc#2")
                # The section's own fields (TITLE) never changed, but a
                # node nested inside it did -- per SDOC-SRS-221 it must
                # still be expanded, or the change inside would be hidden.
                git_conflicts_screen.assert_node_expanded("requirement.sdoc#3")
                git_conflicts_screen.assert_node_expanded("requirement.sdoc#4")
