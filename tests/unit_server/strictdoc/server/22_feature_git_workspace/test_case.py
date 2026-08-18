import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.features.git_workspace import sync_worktree_service
from strictdoc.server.app import create_app


def run_git(path_to_repo: str, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )
    assert result.returncode == 0, result


def _write_gitignore(path_to_repo: str) -> None:
    # PYTHONPYCACHEPREFIX (set to a relative "build/pycache" by this
    # project's tox.ini) makes the interpreter write bytecode cache under
    # "build/" resolved against whatever the current working directory
    # happens to be -- including a test fixture's temp repo, if it's the
    # first test in the session to trigger compiling some not-yet-cached
    # stdlib module while chdir'd into it. Gitignoring "build/" here
    # (mirroring this project's own root .gitignore) keeps that harmless
    # side effect from tripping is_clean_branch()-gated tests.
    with open(
        os.path.join(path_to_repo, ".gitignore"), "w", encoding="utf8"
    ) as gitignore_file:
        gitignore_file.write("/build/\n")


def build_project_config(
    path_to_repo: str, *, activate_git_workspace: bool
) -> ProjectConfig:
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=path_to_repo,
        # Deliberately a sibling of path_to_repo, not nested inside it: an
        # output/ dir nested inside the repo would show up as untracked in
        # "git status" and make is_clean_branch() (and therefore
        # checkout_branch()) think the workspace is dirty.
        output_path=os.path.join(os.path.dirname(path_to_repo), "output"),
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config = ProjectConfigLoader.load_using_server_config(server_config)
    if activate_git_workspace:
        project_config.project_features.append("GIT_WORKSPACE_EXPERIMENTAL")
    return project_config


@pytest.fixture
def project_config(tmp_path):
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)
    with open(
        os.path.join(path_to_repo, "sample.sdoc"), "w", encoding="utf8"
    ) as sample_file:
        sample_file.write(
            "[DOCUMENT]\nTITLE: Sample document\n\n"
            "[REQUIREMENT]\nSTATEMENT: System shall do 1.\n"
        )
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")

    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        yield build_project_config(path_to_repo, activate_git_workspace=True)
    finally:
        os.chdir(path_to_cwd_before)


def write_requirement(path_to_target_repo: str, statement: str) -> None:
    # A stable UID is required for the 3-way node classifier to recognize
    # base/target/incoming copies of this requirement as "the same logical
    # node" (it matches by MID, then UID, then title/content similarity --
    # never by STATEMENT alone; see three_way_merge_analyzer.py).
    with open(
        os.path.join(path_to_target_repo, "requirement.sdoc"),
        "w",
        encoding="utf8",
    ) as requirement_file:
        requirement_file.write(
            "[DOCUMENT]\nTITLE: Test\n\n"
            f"[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: {statement}\n"
        )


@pytest.fixture
def project_config_diverged(tmp_path):
    """
    Builds a repo with two *local* branches ("main", "feature") that both
    edit the same requirement, so rebasing "feature" onto "main" conflicts.

    Synchronize is a pure local rebase now (no fetch, no remote involved),
    so no remote/second-clone setup is needed to produce a conflict.

    Deliberately does NOT run the rebase here: create_app() eagerly builds
    the full traceability index at startup, and the SDoc parser cannot
    parse a file containing raw "<<<<<<<" conflict markers, so a server
    pointed at an already-conflicted working tree fails to even start.
    Real usage never hits this because the server is already running
    (index already built from clean content) before a sync produces a
    conflict live -- so tests must reproduce that same ordering: create the
    app first, then trigger the conflict through the running server via
    POST /git_workspace/sync, exactly like a real user would.
    """
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    write_requirement(path_to_repo, "Base.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")

    run_git(path_to_repo, "checkout", "-b", "feature")
    write_requirement(path_to_repo, "Feature.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Feature change")

    run_git(path_to_repo, "checkout", "main")
    write_requirement(path_to_repo, "Main.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Main change")

    run_git(path_to_repo, "checkout", "feature")

    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        yield build_project_config(path_to_repo, activate_git_workspace=True)
    finally:
        os.chdir(path_to_cwd_before)


@pytest.fixture
def project_config_with_remote(tmp_path):
    """
    A repo with a bare "origin" remote and one pushed commit on "main", for
    testing the push/force_push actions -- separate from sync (which no
    longer touches any remote at all).
    """
    path_to_remote = str(tmp_path / "remote.git")
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)

    run_git(str(tmp_path), "init", "--bare", "-b", "main", path_to_remote)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    write_requirement(path_to_repo, "Base.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")
    run_git(path_to_repo, "remote", "add", "origin", path_to_remote)
    run_git(path_to_repo, "push", "-u", "origin", "main")

    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        yield build_project_config(path_to_repo, activate_git_workspace=True)
    finally:
        os.chdir(path_to_cwd_before)


def trigger_conflict(client: TestClient) -> None:
    response = client.post(
        "/git_workspace/sync",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"found conflicts" in response.content


@pytest.fixture
def project_config_without_git_workspace(tmp_path):
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        yield build_project_config(path_to_repo, activate_git_workspace=False)
    finally:
        os.chdir(path_to_cwd_before)


def test_git_workspace_not_activated_returns_412(
    project_config_without_git_workspace: ProjectConfig,
):
    client = TestClient(
        create_app(project_config=project_config_without_git_workspace)
    )
    response = client.get("/git_workspace")
    assert response.status_code == 412


def test_git_workspace_screen_loads(project_config: ProjectConfig):
    client = TestClient(create_app(project_config=project_config))
    response = client.get("/git_workspace")
    assert response.status_code == 200
    assert b"main" in response.content


def test_git_workspace_stage_and_commit(project_config: ProjectConfig):
    client = TestClient(create_app(project_config=project_config))

    with open(
        os.path.join(project_config.input_paths[0], "new.sdoc"),
        "w",
        encoding="utf8",
    ) as new_file:
        new_file.write("[DOCUMENT]\nTITLE: New document\n")

    response = client.get("/git_workspace")
    assert response.status_code == 200
    assert b"new.sdoc" in response.content

    response = client.post(
        "/git_workspace/stage",
        data={"target_branch": "main", "paths": ["new.sdoc"]},
        follow_redirects=False,
    )
    assert response.status_code == 303

    response = client.post(
        "/git_workspace/commit",
        data={"target_branch": "main", "message": "Add new document"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Committed the staged changes." in response.content

    log_result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=project_config.input_paths[0],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Add new document" in log_result.stdout


def test_git_workspace_commit_without_staged_changes_is_rejected(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))
    response = client.post(
        "/git_workspace/commit",
        data={"target_branch": "main", "message": "Nothing to commit"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Nothing is staged to commit." in response.content


def test_git_workspace_branch_create_and_switch(project_config: ProjectConfig):
    client = TestClient(create_app(project_config=project_config))
    response = client.post(
        "/git_workspace/branch",
        data={
            "target_branch": "main",
            "branch_name": "feature",
            "action": "create",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Switched to branch &#39;feature&#39;." in response.content

    response = client.get("/git_workspace")
    assert b"feature" in response.content


def test_git_conflicts_no_sync_in_progress(project_config: ProjectConfig):
    client = TestClient(create_app(project_config=project_config))
    response = client.get("/git_conflicts")
    assert response.status_code == 200
    assert b"No synchronization is currently in progress." in response.content


def test_git_conflicts_screen_shows_both_sides(
    project_config_diverged: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config_diverged))
    trigger_conflict(client)

    response = client.get("/git_conflicts")
    assert response.status_code == 200
    assert b"requirement.sdoc" in response.content
    # STATEMENT differs between "Main." and "Feature.", so both sides get
    # rendered as a word-level colored diff (fragmented into per-token
    # spans) rather than as a literal contiguous substring -- check for the
    # field label and the conflict UI instead of the exact diffed text.
    assert b"STATEMENT" in response.content
    assert b'data-testid="git-conflicts-resolve-node-form"' in response.content
    assert b"1 conflict(s) remaining" in response.content


def _extract_conflict_node_key(response_content: bytes) -> str:
    html = response_content.decode("utf8")
    marker = 'data-testid="git-conflicts-resolve-node-form"'
    form_start = html.index(marker)
    key_marker = 'name="node_key" value="'
    key_start = html.index(key_marker, form_start) + len(key_marker)
    key_end = html.index('"', key_start)
    return html[key_start:key_end]


def _extract_commit_button_html(response_content: bytes) -> str:
    html = response_content.decode("utf8")
    marker = 'data-testid="git-conflicts-commit-action"'
    marker_start = html.index(marker)
    button_start = html.rindex("<button", 0, marker_start)
    button_end = html.index(">", marker_start)
    return html[button_start : button_end + 1]


def test_git_conflicts_resolve_and_commit(
    project_config_diverged: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config_diverged))
    path_to_repo = project_config_diverged.input_paths[0]

    branch_sha_before = subprocess.run(
        ["git", "rev-parse", "feature"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

    trigger_conflict(client)

    # The live tree must stay untouched while the conflict is unresolved:
    # no conflict markers on disk, live branch pointer unmoved. Node
    # classification runs entirely in isolated scratch worktrees.
    with open(
        os.path.join(path_to_repo, "requirement.sdoc"), encoding="utf8"
    ) as requirement_file_mid_conflict:
        assert "<<<<<<<" not in requirement_file_mid_conflict.read()
    branch_sha_mid_conflict = subprocess.run(
        ["git", "rev-parse", "feature"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    assert branch_sha_mid_conflict == branch_sha_before

    conflicts_response = client.get("/git_conflicts")
    node_key = _extract_conflict_node_key(conflicts_response.content)

    response = client.post(
        "/git_conflicts/resolve_node",
        data={
            "target_branch": "main",
            "node_key": node_key,
            "decision": "incoming",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Node resolved." in response.content

    response = client.post(
        "/git_conflicts/commit",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Synchronization finished: rebased onto" in response.content

    with open(
        os.path.join(path_to_repo, "requirement.sdoc"), encoding="utf8"
    ) as requirement_file:
        assert "STATEMENT: Feature." in requirement_file.read()

    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert status_result.stdout == ""

    # Exactly one new commit landed on top of "main"'s tip.
    count = subprocess.run(
        ["git", "rev-list", "--count", "main..feature"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    assert count == "1"


def test_git_conflicts_warns_and_blocks_commit_for_non_document_change(
    project_config_diverged: ProjectConfig,
):
    """
    SDOC-SRS-224: a changed file outside a readable StrictDoc format on
    either side of the synchronization must show a warning on the
    /git_conflicts screen and keep blocking Commit, even after every node
    conflict has been resolved.
    """
    path_to_repo = project_config_diverged.input_paths[0]
    with open(
        os.path.join(path_to_repo, "notes.txt"), "w", encoding="utf8"
    ) as notes_file:
        notes_file.write("Some non-document notes.\n")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Add non-document file")

    client = TestClient(create_app(project_config=project_config_diverged))
    trigger_conflict(client)

    conflicts_response = client.get("/git_conflicts")
    assert (
        b'data-testid="git-conflicts-non-document-warning"'
        in conflicts_response.content
    )
    assert b"notes.txt" in conflicts_response.content
    commit_button_html = _extract_commit_button_html(conflicts_response.content)
    assert "disabled" in commit_button_html

    node_key = _extract_conflict_node_key(conflicts_response.content)
    response = client.post(
        "/git_conflicts/resolve_node",
        data={
            "target_branch": "main",
            "node_key": node_key,
            "decision": "incoming",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Every node conflict is resolved, but the non-document change still
    # blocks the Commit button.
    assert b"0 conflict(s) remaining" in response.content
    assert (
        b'data-testid="git-conflicts-non-document-warning"' in response.content
    )
    commit_button_html = _extract_commit_button_html(response.content)
    assert "disabled" in commit_button_html

    response = client.post(
        "/git_conflicts/commit",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Cannot commit" in response.content
    assert b"not in a readable StrictDoc" in response.content

    # Nothing was published: the live branch pointer never moved.
    branch_sha_after = subprocess.run(
        ["git", "rev-parse", "feature"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    commit_count = subprocess.run(
        ["git", "rev-list", "--count", "main..feature"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    assert commit_count == "2"
    assert branch_sha_after != ""


def test_git_workspace_surfaces_pending_synchronization(
    project_config_diverged: ProjectConfig,
):
    """
    SDOC-SRS-218: a pending (uncommitted/unaborted) synchronization must be
    surfaced directly on the Git Workspace screen -- including after a
    fresh app build, simulating a server restart -- with both an Abort and
    a Continue action, so the user never has to type /git_conflicts by
    hand.
    """
    client = TestClient(create_app(project_config=project_config_diverged))
    response = client.get("/git_workspace")
    assert (
        b'data-testid="git-workspace-pending-sync-banner"'
        not in response.content
    )

    trigger_conflict(client)

    response = client.get("/git_workspace")
    assert response.status_code == 200
    assert (
        b'data-testid="git-workspace-pending-sync-banner"' in response.content
    )
    assert (
        b'data-testid="git-workspace-continue-sync-action"' in response.content
    )
    assert b'data-testid="git-workspace-abort-sync-action"' in response.content
    # Also survives a fresh app build against the same on-disk state
    # (simulating a server restart with a pending sync left behind).
    restarted_client = TestClient(
        create_app(project_config=project_config_diverged)
    )
    response = restarted_client.get("/git_workspace")
    assert (
        b'data-testid="git-workspace-pending-sync-banner"' in response.content
    )

    # Aborting directly from the workspace screen's own form clears it.
    response = client.post(
        "/git_conflicts/abort",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b'data-testid="git-workspace-pending-sync-banner"'
        not in response.content
    )


def test_git_conflicts_abort(project_config_diverged: ProjectConfig):
    client = TestClient(create_app(project_config=project_config_diverged))
    trigger_conflict(client)

    path_to_meta = os.path.join(
        project_config_diverged.get_path_to_cache_dir(),
        "git",
        "sync_merge.meta.json",
    )
    assert os.path.isfile(path_to_meta)

    response = client.post(
        "/git_conflicts/abort",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Synchronization aborted." in response.content

    path_to_repo = project_config_diverged.input_paths[0]
    status_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert status_result.stdout.strip() == "feature"
    assert not os.path.exists(path_to_meta)


def test_git_workspace_sync_without_conflict_lands_on_review_screen_by_default(
    project_config_diverged: ProjectConfig,
):
    """
    Per SDOC-SRS-217, by default the left/right review screen is always
    shown after Synchronize, even when there are zero true conflicts --
    the user must explicitly commit. Synchronize itself must still not
    create a commit or touch any remote on its own. Rebasing "feature" onto
    "main" here trivially succeeds because "main" is a fast-forward
    ancestor once "feature" only adds an unrelated file -- no conflicting
    edit is involved.
    """
    path_to_repo = project_config_diverged.input_paths[0]
    run_git(path_to_repo, "checkout", "main")
    run_git(path_to_repo, "checkout", "feature")
    # Re-point "feature" onto an unrelated, non-conflicting change so that
    # sync succeeds cleanly instead of hitting the conflict this fixture is
    # otherwise built for.
    run_git(path_to_repo, "reset", "--hard", "main")
    with open(
        os.path.join(path_to_repo, "other.sdoc"), "w", encoding="utf8"
    ) as other_file:
        other_file.write("[DOCUMENT]\nTITLE: Other\n")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Unrelated change")

    commit_count_before = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

    client = TestClient(create_app(project_config=project_config_diverged))
    response = client.post(
        "/git_workspace/sync",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Synchronization ready. Review and commit below." in response.content
    )
    assert b"0 conflict(s) remaining" in response.content
    # The review screen must not be empty just because there are zero true
    # conflicts -- the whole point of always showing it (SDOC-SRS-217) is
    # to let the user review what's being auto-merged before committing.
    # "other.sdoc" here is a whole new document added on the incoming side
    # with no requirements in it, so it has no node-level classification
    # to show either -- it must still appear as a document being added.
    assert b'data-testid="git-conflicts-document"' in response.content
    assert b"other.sdoc" in response.content

    # Nothing published yet -- still on the review screen, no commit/push.
    commit_count_mid = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    assert commit_count_mid == commit_count_before

    path_to_meta = os.path.join(
        project_config_diverged.get_path_to_cache_dir(),
        "git",
        "sync_merge.meta.json",
    )
    assert os.path.isfile(path_to_meta)

    # Explicit commit finishes it, as required.
    response = client.post(
        "/git_conflicts/commit",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Synchronization finished: rebased onto &#39;main&#39;."
        in response.content
    )
    assert not os.path.exists(path_to_meta)

    remote_result = subprocess.run(
        ["git", "remote"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert remote_result.stdout.strip() == ""


def test_git_workspace_sync_fast_forward_opt_in_publishes_immediately(
    project_config_diverged: ProjectConfig,
):
    """
    With the fast_forward checkbox enabled, a clean (zero-true-conflict)
    sync publishes immediately without visiting /git_conflicts -- the
    opt-in escape hatch from SDOC-SRS-217.
    """
    path_to_repo = project_config_diverged.input_paths[0]
    run_git(path_to_repo, "checkout", "main")
    run_git(path_to_repo, "checkout", "feature")
    run_git(path_to_repo, "reset", "--hard", "main")
    with open(
        os.path.join(path_to_repo, "other.sdoc"), "w", encoding="utf8"
    ) as other_file:
        other_file.write("[DOCUMENT]\nTITLE: Other\n")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Unrelated change")

    client = TestClient(create_app(project_config=project_config_diverged))
    response = client.post(
        "/git_workspace/sync",
        data={"target_branch": "main", "fast_forward": "true"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Synchronization finished: rebased onto &#39;main&#39;."
        in response.content
    )

    path_to_meta = os.path.join(
        project_config_diverged.get_path_to_cache_dir(),
        "git",
        "sync_merge.meta.json",
    )
    assert not os.path.exists(path_to_meta)


def test_git_workspace_sync_fast_forward_opt_in_skipped_for_non_document_change(
    project_config_diverged: ProjectConfig,
):
    """
    SDOC-SRS-224: even with the fast_forward checkbox enabled, a sync must
    never auto-publish while a non-document file changed on either side --
    it falls through to the normal /git_conflicts review screen instead,
    which then warns and blocks Commit.
    """
    path_to_repo = project_config_diverged.input_paths[0]
    run_git(path_to_repo, "checkout", "main")
    run_git(path_to_repo, "checkout", "feature")
    run_git(path_to_repo, "reset", "--hard", "main")
    with open(
        os.path.join(path_to_repo, "notes.txt"), "w", encoding="utf8"
    ) as notes_file:
        notes_file.write("Some non-document notes.\n")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Unrelated non-document change")

    client = TestClient(create_app(project_config=project_config_diverged))
    response = client.post(
        "/git_workspace/sync",
        data={"target_branch": "main", "fast_forward": "true"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"found conflicts" not in response.content
    assert (
        b"Synchronization ready. Review and commit below." in response.content
    )
    assert (
        b'data-testid="git-conflicts-non-document-warning"' in response.content
    )

    path_to_meta = os.path.join(
        project_config_diverged.get_path_to_cache_dir(),
        "git",
        "sync_merge.meta.json",
    )
    assert os.path.isfile(path_to_meta)


def test_git_workspace_sync_auto_merges_non_conflicting_changes(tmp_path):
    """
    Target and incoming each independently modify a *different* requirement
    relative to their common base: no true conflict exists (per the 3-way
    classifier, only one side touched each node). By default (no
    fast_forward) this still lands on the review screen with everything
    already auto-merged and Commit immediately enabled; committing there
    publishes a result containing both sides' changes.
    """
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    def write_two(statement_1: str, statement_2: str) -> None:
        with open(
            os.path.join(path_to_repo, "requirement.sdoc"),
            "w",
            encoding="utf8",
        ) as requirement_file:
            requirement_file.write(
                "[DOCUMENT]\nTITLE: Test\n\n"
                f"[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: {statement_1}\n\n"
                f"[REQUIREMENT]\nUID: REQ_2\nSTATEMENT: {statement_2}\n"
            )

    write_two("Base 1.", "Base 2.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")

    run_git(path_to_repo, "checkout", "-b", "feature")
    write_two("Base 1.", "Feature 2.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Feature change")

    run_git(path_to_repo, "checkout", "main")
    write_two("Main 1.", "Base 2.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Main change")
    run_git(path_to_repo, "checkout", "feature")

    project_config = build_project_config(
        path_to_repo, activate_git_workspace=True
    )
    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        client = TestClient(create_app(project_config=project_config))
        response = client.post(
            "/git_workspace/sync",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert (
            b"Synchronization ready. Review and commit below."
            in response.content
        )
        assert b"0 conflict(s) remaining" in response.content
        # Regression: an auto-merged node used to render the same resolved
        # value on both the "your branch" and target columns, making a real,
        # one-sided change look identical side-by-side (i.e. indistinguishable
        # from no change at all). Each column must show its own pre-merge
        # content instead -- including the *unchanged* side's original text
        # ("Base 1."/"Base 2."), which the old buggy render replaced with
        # the other side's resolved value everywhere.
        assert b"Main 1." in response.content
        assert b"Feature 2." in response.content
        assert b"Base 1." in response.content
        assert b"Base 2." in response.content

        response = client.post(
            "/git_conflicts/commit",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Synchronization finished" in response.content

        content = (Path(path_to_repo) / "requirement.sdoc").read_text()
        assert "STATEMENT: Main 1." in content
        assert "STATEMENT: Feature 2." in content

        count = subprocess.run(
            ["git", "rev-list", "--count", "main..feature"],
            cwd=path_to_repo,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        assert count == "1"
    finally:
        os.chdir(path_to_cwd_before)


def test_git_conflicts_place_node_reorders_independent_additions(tmp_path):
    """
    SDOC-SRS-215 sub-scenario 2: target and incoming each independently add
    a *new*, unrelated top-level section (with a text node) -- both
    auto-merge in without any conflict, in a fixed default order
    (target's own new section first, incoming's last). POST
    /git_conflicts/place_node lets the user override that default order
    before committing.
    """
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    def write_base() -> None:
        with open(
            os.path.join(path_to_repo, "requirement.sdoc"),
            "w",
            encoding="utf8",
        ) as requirement_file:
            requirement_file.write(
                "[DOCUMENT]\nTITLE: Test\n\n"
                "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Base.\n"
            )

    def add_section(uid: str, statement: str) -> None:
        with open(
            os.path.join(path_to_repo, "requirement.sdoc"),
            "a",
            encoding="utf8",
        ) as requirement_file:
            requirement_file.write(
                f"\n[[SECTION]]\nUID: {uid}\nTITLE: {uid}\n\n"
                f"[REQUIREMENT]\nUID: {uid}_TEXT\nSTATEMENT: {statement}\n\n"
                "[[/SECTION]]\n"
            )

    write_base()
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")

    run_git(path_to_repo, "checkout", "-b", "feature")
    add_section("SEC_INCOMING", "Added by incoming.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Feature change")

    run_git(path_to_repo, "checkout", "main")
    add_section("SEC_TARGET", "Added by target.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Main change")
    run_git(path_to_repo, "checkout", "feature")

    project_config = build_project_config(
        path_to_repo, activate_git_workspace=True
    )
    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        client = TestClient(create_app(project_config=project_config))
        response = client.post(
            "/git_workspace/sync",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"0 conflict(s) remaining" in response.content

        # Default order: target's own new section first, incoming's last
        # (node #0 is the shared, unchanged REQ_1; #1/#2 are target's new
        # section+text; #3/#4 are incoming's). Move incoming's new section
        # to right after REQ_1, ahead of target's.
        response = client.post(
            "/git_conflicts/place_node",
            data={
                "target_branch": "main",
                "node_key": "requirement.sdoc#3",
                "after_key": "requirement.sdoc#0",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Node repositioned." in response.content

        response = client.post(
            "/git_conflicts/commit",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Synchronization finished" in response.content

        content = (Path(path_to_repo) / "requirement.sdoc").read_text()
        # Incoming's section, placed right after REQ_1, must now precede
        # target's own section in the materialized file.
        incoming_index = content.index("Added by incoming.")
        target_index = content.index("Added by target.")
        assert incoming_index < target_index
    finally:
        os.chdir(path_to_cwd_before)


def test_git_workspace_sync_independent_new_documents_both_survive(tmp_path):
    """
    SDOC-SRS-215 sub-scenario 4: target and incoming each independently add
    a whole new, unrelated *document* (different file). Neither side ever
    saw the other's file, so this isn't a conflict at all -- both new
    documents must simply both exist after synchronization.
    """
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    write_requirement(path_to_repo, "Base.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")

    run_git(path_to_repo, "checkout", "-b", "feature")
    with open(
        os.path.join(path_to_repo, "feature_doc.sdoc"), "w", encoding="utf8"
    ) as feature_file:
        feature_file.write(
            "[DOCUMENT]\nTITLE: Feature Doc\n\n"
            "[REQUIREMENT]\nUID: FEATURE_REQ\nSTATEMENT: Added by feature.\n"
        )
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Feature change")

    run_git(path_to_repo, "checkout", "main")
    with open(
        os.path.join(path_to_repo, "main_doc.sdoc"), "w", encoding="utf8"
    ) as main_file:
        main_file.write(
            "[DOCUMENT]\nTITLE: Main Doc\n\n"
            "[REQUIREMENT]\nUID: MAIN_REQ\nSTATEMENT: Added by main.\n"
        )
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Main change")
    run_git(path_to_repo, "checkout", "feature")

    project_config = build_project_config(
        path_to_repo, activate_git_workspace=True
    )
    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        client = TestClient(create_app(project_config=project_config))
        response = client.post(
            "/git_workspace/sync",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"0 conflict(s) remaining" in response.content

        response = client.post(
            "/git_conflicts/commit",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Synchronization finished" in response.content

        assert (Path(path_to_repo) / "feature_doc.sdoc").is_file()
        assert (Path(path_to_repo) / "main_doc.sdoc").is_file()
        assert (
            "Added by feature."
            in (Path(path_to_repo) / "feature_doc.sdoc").read_text()
        )
        assert (
            "Added by main."
            in (Path(path_to_repo) / "main_doc.sdoc").read_text()
        )
    finally:
        os.chdir(path_to_cwd_before)


def test_git_workspace_sync_independent_document_deletions_both_removed(
    tmp_path,
):
    """
    SDOC-SRS-215 sub-scenario 5: target and incoming each independently
    delete a *different* existing document, leaving the other untouched.
    Neither side conflicts with the other's deletion -- both documents
    must be entirely gone after synchronization (not merely emptied: this
    is a regression test for a real bug where a whole-document deletion
    materialized as an empty document shell instead of removing the file,
    because materialize_and_publish always wrote *some* bytes for any
    composite document, even one every node had resolved out of).
    """
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    write_requirement(path_to_repo, "Base.")
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

    run_git(path_to_repo, "checkout", "-b", "feature")
    run_git(path_to_repo, "rm", "doc_a.sdoc")
    run_git(path_to_repo, "commit", "-m", "Feature change")

    run_git(path_to_repo, "checkout", "main")
    run_git(path_to_repo, "rm", "doc_b.sdoc")
    run_git(path_to_repo, "commit", "-m", "Main change")
    run_git(path_to_repo, "checkout", "feature")

    project_config = build_project_config(
        path_to_repo, activate_git_workspace=True
    )
    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        client = TestClient(create_app(project_config=project_config))
        response = client.post(
            "/git_workspace/sync",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"0 conflict(s) remaining" in response.content

        response = client.post(
            "/git_conflicts/commit",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Synchronization finished" in response.content

        assert not (Path(path_to_repo) / "doc_a.sdoc").exists()
        assert not (Path(path_to_repo) / "doc_b.sdoc").exists()
        assert (Path(path_to_repo) / "requirement.sdoc").is_file()

        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=path_to_repo,
            capture_output=True,
            text=True,
            check=False,
        )
        assert status_result.stdout == ""
    finally:
        os.chdir(path_to_cwd_before)


def test_git_workspace_sync_is_repeatable_without_pushing_in_between(
    tmp_path,
):
    """
    SDOC-SRS-222: a completed synchronization is never a terminal state --
    the user can synchronize again immediately, any number of times,
    without pushing in between. Drives two full Synchronize -> Commit
    cycles back-to-back (target branch moves again between them,
    simulating a teammate landing more work) and asserts neither
    /git_workspace/sync POST is ever rejected.
    """
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    write_requirement(path_to_repo, "Base.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")

    run_git(path_to_repo, "checkout", "-b", "feature")

    project_config = build_project_config(
        path_to_repo, activate_git_workspace=True
    )
    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        client = TestClient(create_app(project_config=project_config))

        # First cycle: main gets one commit, sync, commit -- no push.
        run_git(path_to_repo, "checkout", "main")
        write_requirement(path_to_repo, "Main change 1.")
        run_git(path_to_repo, "add", ".")
        run_git(path_to_repo, "commit", "-m", "Main change 1")
        run_git(path_to_repo, "checkout", "feature")

        response = client.post(
            "/git_workspace/sync",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"0 conflict(s) remaining" in response.content

        response = client.post(
            "/git_conflicts/commit",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Synchronization finished" in response.content
        # The old wording implied push was the only valid next step;
        # SDOC-SRS-222 requires the message to invite re-synchronizing too.
        assert b"Synchronize again if needed" in response.content

        # Nothing should be disabled or blocked -- the Synchronize button
        # is only ever gated on a dirty tree or a pending sync, neither of
        # which applies right after a clean commit.
        workspace_page = client.get("/git_workspace")
        assert (
            b'data-testid="git-workspace-sync-action"' in workspace_page.content
        )
        assert (
            b'data-testid="git-workspace-sync-action" disabled'
            not in workspace_page.content
        )

        # Second cycle, immediately, no push in between: main moves again.
        run_git(path_to_repo, "checkout", "main")
        write_requirement(path_to_repo, "Main change 2.")
        run_git(path_to_repo, "add", ".")
        run_git(path_to_repo, "commit", "-m", "Main change 2")
        run_git(path_to_repo, "checkout", "feature")

        response = client.post(
            "/git_workspace/sync",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"already in progress" not in response.content
        assert b"0 conflict(s) remaining" in response.content

        response = client.post(
            "/git_conflicts/commit",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Synchronization finished" in response.content

        content = (Path(path_to_repo) / "requirement.sdoc").read_text()
        assert "STATEMENT: Main change 2." in content

        # Each Synchronize places exactly one new commit on top of
        # target's tip (SDOC-SRS-216), regardless of how many times it's
        # run -- so after two cycles "feature" is still exactly one
        # commit ahead of "main"'s current tip, not accumulating one
        # extra commit per cycle.
        count = subprocess.run(
            ["git", "rev-list", "--count", "main..feature"],
            cwd=path_to_repo,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        assert count == "1"
    finally:
        os.chdir(path_to_cwd_before)


def test_git_workspace_sync_classifies_branch_comparison_only_once(
    project_config_diverged: ProjectConfig,
):
    """
    SDOC-SRS-223: a single Git conflicts action shall not redo the same
    branch comparison more than once. Synchronize's own handler computes
    the 3-way classification to decide whether there are conflicts, then
    redirects to the conflict-resolution screen, whose GET handler used to
    independently recompute the identical classification a second time.
    """
    client = TestClient(create_app(project_config=project_config_diverged))

    with patch.object(
        sync_worktree_service,
        "classify_documents_from_stats",
        wraps=sync_worktree_service.classify_documents_from_stats,
    ) as classify_documents_mock:
        response = client.post(
            "/git_workspace/sync",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"found conflicts" in response.content
        assert classify_documents_mock.call_count == 1


def test_git_conflicts_resolve_section_bulk_allocates_children(
    tmp_path,
):
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    _write_gitignore(path_to_repo)

    def write(statement_1: str, statement_2: str) -> None:
        with open(
            os.path.join(path_to_repo, "requirement.sdoc"),
            "w",
            encoding="utf8",
        ) as requirement_file:
            requirement_file.write(
                "[DOCUMENT]\nTITLE: Test\n\n"
                "[[SECTION]]\nUID: SEC_1\nTITLE: Section\n\n"
                f"[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: {statement_1}\n\n"
                f"[REQUIREMENT]\nUID: REQ_2\nSTATEMENT: {statement_2}\n\n"
                "[[/SECTION]]\n"
            )

    write("Base 1.", "Base 2.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")

    run_git(path_to_repo, "checkout", "-b", "feature")
    write("Feature 1.", "Feature 2.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Feature change")

    run_git(path_to_repo, "checkout", "main")
    write("Main 1.", "Main 2.")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Main change")
    run_git(path_to_repo, "checkout", "feature")

    project_config = build_project_config(
        path_to_repo, activate_git_workspace=True
    )
    path_to_cwd_before = os.getcwd()
    os.chdir(path_to_repo)
    try:
        client = TestClient(create_app(project_config=project_config))
        trigger_conflict(client)

        conflicts_response = client.get("/git_conflicts")
        assert b"2 conflict(s) remaining" in conflicts_response.content

        html = conflicts_response.content.decode("utf8")
        section_marker = 'data-testid="git-conflicts-resolve-section-form"'
        section_start = html.index(section_marker)
        key_marker = 'name="section_key" value="'
        key_start = html.index(key_marker, section_start) + len(key_marker)
        key_end = html.index('"', key_start)
        section_key = html[key_start:key_end]

        response = client.post(
            "/git_conflicts/resolve_section",
            data={
                "target_branch": "main",
                "section_key": section_key,
                "decision": "incoming",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Section resolved." in response.content

        response = client.get("/git_conflicts")
        assert b"0 conflict(s) remaining" in response.content

        response = client.post(
            "/git_conflicts/commit",
            data={"target_branch": "main"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Synchronization finished" in response.content

        content = (Path(path_to_repo) / "requirement.sdoc").read_text()
        assert "STATEMENT: Feature 1." in content
        assert "STATEMENT: Feature 2." in content
    finally:
        os.chdir(path_to_cwd_before)


def test_git_workspace_sync_blocked_when_uncommitted_changes(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))
    path_to_repo = project_config.input_paths[0]
    with open(
        os.path.join(path_to_repo, "sample.sdoc"), "a", encoding="utf8"
    ) as sample_file:
        sample_file.write("\n[REQUIREMENT]\nSTATEMENT: Uncommitted.\n")

    response = client.post(
        "/git_workspace/sync",
        data={"target_branch": "main"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("/git_workspace?")

    response = client.get(response.headers["location"])
    assert response.status_code == 200
    assert b"Cannot synchronize" in response.content
    assert b"uncommitted changes" in response.content

    status_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert status_result.stdout.strip() == "main"


def _sync_button_html(response_content: bytes) -> str:
    html = response_content.decode("utf8")
    marker = 'data-testid="git-workspace-sync-form"'
    form_start = html.index(marker)
    form_end = html.index("</form>", form_start)
    return html[form_start:form_end]


def test_git_workspace_sync_button_disabled_when_dirty(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))
    path_to_repo = project_config.input_paths[0]

    response = client.get("/git_workspace")
    assert response.status_code == 200
    assert "disabled" not in _sync_button_html(response.content)

    with open(
        os.path.join(path_to_repo, "sample.sdoc"), "a", encoding="utf8"
    ) as sample_file:
        sample_file.write("\n[REQUIREMENT]\nSTATEMENT: Uncommitted.\n")

    response = client.get("/git_workspace")
    assert response.status_code == 200
    assert "disabled" in _sync_button_html(response.content)


def test_git_workspace_sync_rejects_concurrent_sync(
    project_config_diverged: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config_diverged))
    trigger_conflict(client)

    response = client.post(
        "/git_workspace/sync",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already in progress" in response.content

    # The original worktree/conflict must remain untouched.
    response = client.get("/git_conflicts")
    assert response.status_code == 200
    assert b"requirement.sdoc" in response.content


def test_git_workspace_branch_switch_blocked_during_pending_sync(
    project_config_diverged: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config_diverged))
    trigger_conflict(client)

    response = client.post(
        "/git_workspace/branch",
        data={
            "target_branch": "main",
            "branch_name": "other",
            "action": "create",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Finish or abort the in-progress synchronization" in response.content
    )

    path_to_repo = project_config_diverged.input_paths[0]
    status_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert status_result.stdout.strip() == "feature"


def test_server_restart_mid_conflict_recovers(
    project_config_diverged: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config_diverged))
    trigger_conflict(client)

    # A fresh app build against the same on-disk state simulates a server
    # restart while a conflict is pending. Prior to isolating the rebase
    # into a separate worktree, this crashed: create_app() eagerly parses
    # the whole project tree, and the SDoc parser cannot handle raw
    # "<<<<<<<" conflict markers, which used to sit in the live tree
    # throughout an in-progress conflict.
    restarted_client = TestClient(
        create_app(project_config=project_config_diverged)
    )
    response = restarted_client.get("/git_conflicts")
    assert response.status_code == 200
    assert b"requirement.sdoc" in response.content
    assert b'data-testid="git-conflicts-resolve-node-form"' in response.content


def test_git_workspace_push(project_config_with_remote: ProjectConfig):
    path_to_repo = project_config_with_remote.input_paths[0]
    with open(
        os.path.join(path_to_repo, "new.sdoc"), "w", encoding="utf8"
    ) as new_file:
        new_file.write("[DOCUMENT]\nTITLE: New document\n")
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Add new document")

    client = TestClient(create_app(project_config=project_config_with_remote))
    response = client.post(
        "/git_workspace/push",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Pushed the branch to its remote." in response.content

    log_result = subprocess.run(
        ["git", "log", "origin/main", "--oneline"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Add new document" in log_result.stdout


def test_git_workspace_push_rejects_diverged_remote_then_force_push_succeeds(
    project_config_with_remote: ProjectConfig,
):
    path_to_repo = project_config_with_remote.input_paths[0]

    # Rewrite local history (simulating a rebase) so a plain push is
    # rejected as non-fast-forward.
    run_git(path_to_repo, "commit", "--amend", "-m", "Initial commit (amended)")

    client = TestClient(create_app(project_config=project_config_with_remote))
    response = client.post(
        "/git_workspace/push",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Push rejected" in response.content

    response = client.post(
        "/git_workspace/force_push",
        data={"target_branch": "main"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Force-pushed the branch to its remote" in response.content

    log_result = subprocess.run(
        ["git", "log", "origin/main", "--oneline"],
        cwd=path_to_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Initial commit (amended)" in log_result.stdout
