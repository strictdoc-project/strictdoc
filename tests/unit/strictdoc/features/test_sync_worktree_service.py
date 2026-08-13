import os
import subprocess
from pathlib import Path

from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.diff_and_changelog.git_client import GitClient
from strictdoc.features.git_workspace.sync_worktree_service import (
    SyncMergeService,
)
from strictdoc.features.git_workspace.three_way_merge_analyzer import (
    NodeClassification,
)


def run_git(path_to_repo: str, *args: str) -> subprocess.CompletedProcess:
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
    return result


def init_repo_with_commit(path_to_repo: str) -> None:
    run_git(path_to_repo, "init", "-b", "main")
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")
    (Path(path_to_repo) / "requirement.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Test\n\n"
        "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Base.\n"
    )
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")


def build_project_config(tmp_path, path_to_repo: str) -> ProjectConfig:
    project_config = ProjectConfig.default_config()
    project_config.input_paths = [path_to_repo]
    project_config.dir_for_sdoc_cache = str(tmp_path / "_cache")
    return project_config


def make_diverged_repo(tmp_path) -> GitClient:
    path_to_repo = str(tmp_path / "repo")
    os.makedirs(path_to_repo)
    init_repo_with_commit(path_to_repo)
    git_client = GitClient(path_to_repo)

    git_client.checkout_branch("feature", create=True)
    (Path(path_to_repo) / "requirement.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Test\n\n"
        "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Feature.\n"
    )
    git_client.stage_paths(["requirement.sdoc"])
    git_client.commit("Feature change")

    run_git(path_to_repo, "checkout", "main")
    (Path(path_to_repo) / "requirement.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Test\n\n"
        "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Main.\n"
    )
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Main change")

    run_git(path_to_repo, "checkout", "feature")
    return git_client


class TestSyncMergeServiceLifecycle:
    def test_compute_merge_and_get_active_round_trip(self, tmp_path):
        git_client = make_diverged_repo(tmp_path)
        project_config = build_project_config(
            tmp_path, git_client.path_to_git_root
        )
        os.chdir(git_client.path_to_git_root)
        try:
            meta, merge_result = SyncMergeService.compute_merge(
                project_config, git_client, "main"
            )
            assert meta.branch == "feature"
            assert meta.target_branch == "main"
            assert merge_result.total_true_conflicts == 1

            assert SyncMergeService.get_active(project_config) is None
            SyncMergeService.persist(project_config, meta)
            active = SyncMergeService.get_active(project_config)
            assert active is not None
            assert active.base_revision == meta.base_revision
        finally:
            os.chdir(str(tmp_path))

    def test_get_active_is_none_when_nothing_pending(self, tmp_path):
        path_to_repo = str(tmp_path / "repo")
        os.makedirs(path_to_repo)
        init_repo_with_commit(path_to_repo)
        project_config = build_project_config(tmp_path, path_to_repo)
        assert SyncMergeService.get_active(project_config) is None

    def test_allocate_and_is_fully_resolved(self, tmp_path):
        git_client = make_diverged_repo(tmp_path)
        project_config = build_project_config(
            tmp_path, git_client.path_to_git_root
        )
        os.chdir(git_client.path_to_git_root)
        try:
            meta, merge_result = SyncMergeService.compute_merge(
                project_config, git_client, "main"
            )
            assert not SyncMergeService.is_fully_resolved(merge_result, meta)

            conflict = next(
                r
                for r in merge_result.documents[0].iter_all()
                if r.is_conflict()
            )
            meta = SyncMergeService.allocate(
                project_config, meta, merge_result, conflict.key, "incoming"
            )
            assert SyncMergeService.is_fully_resolved(merge_result, meta)

            # Persisted, recoverable from disk.
            SyncMergeService.persist(project_config, meta)
            active = SyncMergeService.get_active(project_config)
            assert active is not None
            assert active.allocations == {conflict.key: "incoming"}
        finally:
            os.chdir(str(tmp_path))

    def test_materialize_and_publish_success_single_commit(self, tmp_path):
        git_client = make_diverged_repo(tmp_path)
        project_config = build_project_config(
            tmp_path, git_client.path_to_git_root
        )
        os.chdir(git_client.path_to_git_root)
        try:
            meta, merge_result = SyncMergeService.compute_merge(
                project_config, git_client, "main"
            )
            conflict = next(
                r
                for r in merge_result.documents[0].iter_all()
                if r.is_conflict()
            )
            meta = SyncMergeService.allocate(
                project_config, meta, merge_result, conflict.key, "incoming"
            )
            SyncMergeService.persist(project_config, meta)

            publish_result = SyncMergeService.materialize_and_publish(
                project_config, git_client, meta, merge_result
            )
            assert publish_result.success

            # Exactly one new commit on top of target's tip.
            target_sha = merge_result.target_revision
            new_head = git_client.check_revision("HEAD")
            count = run_git(
                git_client.path_to_git_root,
                "rev-list",
                "--count",
                f"{target_sha}..{new_head}",
            ).stdout.strip()
            assert count == "1"

            content = (
                Path(git_client.path_to_git_root) / "requirement.sdoc"
            ).read_text()
            assert "STATEMENT: Feature." in content

            assert SyncMergeService.get_active(project_config) is None
        finally:
            os.chdir(str(tmp_path))

    def test_materialize_fails_and_preserves_state_when_live_dirty(
        self, tmp_path
    ):
        git_client = make_diverged_repo(tmp_path)
        project_config = build_project_config(
            tmp_path, git_client.path_to_git_root
        )
        os.chdir(git_client.path_to_git_root)
        try:
            meta, merge_result = SyncMergeService.compute_merge(
                project_config, git_client, "main"
            )
            conflict = next(
                r
                for r in merge_result.documents[0].iter_all()
                if r.is_conflict()
            )
            meta = SyncMergeService.allocate(
                project_config, meta, merge_result, conflict.key, "incoming"
            )
            SyncMergeService.persist(project_config, meta)

            (Path(git_client.path_to_git_root) / "dirty.sdoc").write_text(
                "[DOCUMENT]\nTITLE: Dirty\n"
            )

            publish_result = SyncMergeService.materialize_and_publish(
                project_config, git_client, meta, merge_result
            )
            assert not publish_result.success
            assert SyncMergeService.get_active(project_config) is not None
        finally:
            os.chdir(str(tmp_path))

    def test_allocate_section_resolves_all_descendant_conflicts(self, tmp_path):
        path_to_repo = str(tmp_path / "repo")
        os.makedirs(path_to_repo)
        run_git(path_to_repo, "init", "-b", "main")
        run_git(path_to_repo, "config", "user.name", "Test")
        run_git(path_to_repo, "config", "user.email", "test@example.com")

        def write(statement_1: str, statement_2: str) -> None:
            (Path(path_to_repo) / "requirement.sdoc").write_text(
                "[DOCUMENT]\nTITLE: Test\n\n"
                "[[SECTION]]\nUID: SEC_1\nTITLE: Section\n\n"
                f"[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: {statement_1}\n\n"
                f"[REQUIREMENT]\nUID: REQ_2\nSTATEMENT: {statement_2}\n\n"
                "[[/SECTION]]\n"
            )

        write("Base 1.", "Base 2.")
        run_git(path_to_repo, "add", ".")
        run_git(path_to_repo, "commit", "-m", "Initial commit")

        git_client = GitClient(path_to_repo)
        git_client.checkout_branch("feature", create=True)
        write("Feature 1.", "Feature 2.")
        git_client.stage_paths(["requirement.sdoc"])
        git_client.commit("Feature change")

        run_git(path_to_repo, "checkout", "main")
        write("Main 1.", "Main 2.")
        run_git(path_to_repo, "add", ".")
        run_git(path_to_repo, "commit", "-m", "Main change")
        run_git(path_to_repo, "checkout", "feature")

        project_config = build_project_config(tmp_path, path_to_repo)
        os.chdir(path_to_repo)
        try:
            meta, merge_result = SyncMergeService.compute_merge(
                project_config, git_client, "main"
            )
            assert merge_result.total_true_conflicts == 2

            section_result = next(
                r
                for r in merge_result.documents[0].node_results
                if r.classification == NodeClassification.UNCHANGED
                and r.target_node is not None
                and r.target_node.node_type == "SECTION"
            )
            meta = SyncMergeService.allocate_section(
                project_config,
                meta,
                merge_result,
                section_result.key,
                "incoming",
            )
            assert SyncMergeService.is_fully_resolved(merge_result, meta)
            assert len(meta.allocations) == 2
        finally:
            os.chdir(str(tmp_path))

    def test_cleanup_removes_meta(self, tmp_path):
        git_client = make_diverged_repo(tmp_path)
        project_config = build_project_config(
            tmp_path, git_client.path_to_git_root
        )
        os.chdir(git_client.path_to_git_root)
        try:
            meta, _merge_result = SyncMergeService.compute_merge(
                project_config, git_client, "main"
            )
            SyncMergeService.persist(project_config, meta)
            assert SyncMergeService.get_active(project_config) is not None

            SyncMergeService.cleanup(project_config)
            assert SyncMergeService.get_active(project_config) is None
        finally:
            os.chdir(str(tmp_path))
