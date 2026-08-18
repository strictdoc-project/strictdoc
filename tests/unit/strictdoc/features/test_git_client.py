import os
import subprocess
from pathlib import Path

from strictdoc.features.diff_and_changelog.git_client import GitClient


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


def configure_git_identity(path_to_repo: str) -> None:
    # GitClient's own subprocess calls (e.g. commit()) run without any
    # special env, so the test repos need a local identity configured
    # rather than relying on GIT_AUTHOR_*/GIT_COMMITTER_* env vars, which
    # only cover the run_git() helper calls above.
    run_git(path_to_repo, "config", "user.name", "Test")
    run_git(path_to_repo, "config", "user.email", "test@example.com")


def init_repo_with_commit(path_to_repo: str) -> None:
    run_git(path_to_repo, "init", "-b", "main")
    configure_git_identity(path_to_repo)
    (Path(path_to_repo) / "requirement.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Test\n\n[REQUIREMENT]\nSTATEMENT: Base.\n"
    )
    run_git(path_to_repo, "add", ".")
    run_git(path_to_repo, "commit", "-m", "Initial commit")


class TestGitClientBranches:
    def test_list_and_get_current_branch(self, tmp_path):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)

        git_client = GitClient(path_to_repo)
        assert git_client.get_current_branch() == "main"
        assert git_client.list_branches() == ["main"]

    def test_checkout_branch_create(self, tmp_path):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)

        git_client = GitClient(path_to_repo)
        checkout_result = git_client.checkout_branch("feature", create=True)
        assert checkout_result.success
        assert git_client.get_current_branch() == "feature"
        assert set(git_client.list_branches()) == {"main", "feature"}

    def test_checkout_branch_refuses_when_dirty(self, tmp_path):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)
        (tmp_path / "requirement.sdoc").write_text("dirty content")

        git_client = GitClient(path_to_repo)
        checkout_result = git_client.checkout_branch("feature", create=True)
        assert not checkout_result.success
        assert checkout_result.error_message is not None
        assert git_client.get_current_branch() == "main"


class TestGitClientStatusAndCommit:
    def test_status_porcelain_reports_untracked_file(self, tmp_path):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)
        (tmp_path / "new.sdoc").write_text("[DOCUMENT]\nTITLE: New\n")

        git_client = GitClient(path_to_repo)
        entries = git_client.get_status_porcelain()
        assert len(entries) == 1
        assert entries[0].path == "new.sdoc"
        assert entries[0].index_status == "?"
        assert entries[0].worktree_status == "?"
        assert not entries[0].is_conflicted

    def test_stage_and_commit(self, tmp_path):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)
        (tmp_path / "new.sdoc").write_text("[DOCUMENT]\nTITLE: New\n")

        git_client = GitClient(path_to_repo)
        git_client.stage_paths(["new.sdoc"])
        new_sha = git_client.commit("Add new document")

        assert git_client.check_revision("HEAD") == new_sha
        assert git_client.is_clean_branch()

    def test_commit_rejects_empty_message(self, tmp_path):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)
        (tmp_path / "new.sdoc").write_text("[DOCUMENT]\nTITLE: New\n")

        git_client = GitClient(path_to_repo)
        git_client.stage_paths(["new.sdoc"])
        try:
            git_client.commit("   ")
            raise AssertionError("Expected an AssertionError.")
        except AssertionError as exception:
            assert "Commit message must not be empty." in str(exception)


class TestGitClientMergeBase:
    def test_merge_base_finds_common_ancestor(self, tmp_path):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)
        git_client = GitClient(path_to_repo)
        common_ancestor = git_client.check_revision("HEAD")

        git_client.checkout_branch("feature", create=True)
        (tmp_path / "feature.sdoc").write_text("[DOCUMENT]\nTITLE: Feature\n")
        git_client.stage_paths(["feature.sdoc"])
        git_client.commit("Feature change")

        run_git(path_to_repo, "checkout", "main")
        (tmp_path / "main.sdoc").write_text("[DOCUMENT]\nTITLE: Main\n")
        run_git(path_to_repo, "add", ".")
        run_git(path_to_repo, "commit", "-m", "Main change")

        assert git_client.merge_base("main", "feature") == common_ancestor

    def test_commit_tree_with_overrides_builds_single_commit_on_parent(
        self, tmp_path
    ):
        path_to_repo = str(tmp_path)
        init_repo_with_commit(path_to_repo)
        git_client = GitClient(path_to_repo)
        parent_sha = git_client.check_revision("HEAD")

        new_sha = git_client.commit_tree_with_overrides(
            base_revision="HEAD",
            overrides={"requirement.sdoc": b"[DOCUMENT]\nTITLE: Overridden\n"},
            parent_revision=parent_sha,
            message="Merged changes",
        )

        assert (
            run_git(
                path_to_repo, "rev-list", "--count", f"{parent_sha}..{new_sha}"
            ).stdout.strip()
            == "1"
        )
        show_result = run_git(
            path_to_repo, "show", f"{new_sha}:requirement.sdoc"
        )
        assert "TITLE: Overridden" in show_result.stdout


class TestGitClientPush:
    def test_push_to_bare_remote(self, tmp_path):
        path_to_remote = str(tmp_path / "remote.git")
        path_to_repo = str(tmp_path / "repo")
        os.makedirs(path_to_repo)

        run_git(str(tmp_path), "init", "--bare", "-b", "main", path_to_remote)
        init_repo_with_commit(path_to_repo)
        run_git(path_to_repo, "remote", "add", "origin", path_to_remote)

        git_client = GitClient(path_to_repo)
        push_result = git_client.push("origin", "main")
        assert push_result.success

    def test_push_rejects_non_fast_forward(self, tmp_path):
        path_to_remote = str(tmp_path / "remote.git")
        path_to_repo_a = str(tmp_path / "repo_a")
        path_to_repo_b = str(tmp_path / "repo_b")
        os.makedirs(path_to_repo_a)

        run_git(str(tmp_path), "init", "--bare", "-b", "main", path_to_remote)
        init_repo_with_commit(path_to_repo_a)
        run_git(path_to_repo_a, "remote", "add", "origin", path_to_remote)
        GitClient(path_to_repo_a).push("origin", "main")

        run_git(str(tmp_path), "clone", path_to_remote, path_to_repo_b)
        configure_git_identity(path_to_repo_b)
        git_client_b = GitClient(path_to_repo_b)
        (Path(path_to_repo_b) / "other.sdoc").write_text(
            "[DOCUMENT]\nTITLE: Other\n"
        )
        git_client_b.stage_paths(["other.sdoc"])
        git_client_b.commit("Second commit")
        git_client_b.push("origin", "main")

        (Path(path_to_repo_a) / "third.sdoc").write_text(
            "[DOCUMENT]\nTITLE: Third\n"
        )
        git_client_a = GitClient(path_to_repo_a)
        git_client_a.stage_paths(["third.sdoc"])
        git_client_a.commit("Diverged commit")

        push_result = git_client_a.push("origin", "main")
        assert not push_result.success
        assert push_result.rejected_non_fast_forward
