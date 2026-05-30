import os.path
import shutil
import subprocess
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

fcntl: Optional[Any]
try:  # pragma: no cover
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.timing import measure_performance


class GitClient:
    _fallback_locks: Dict[str, threading.Lock] = {}
    _fallback_locks_guard = threading.Lock()

    def __init__(self, path_to_git_root: str) -> None:
        assert os.path.isdir(path_to_git_root)
        self.path_to_git_root: str = path_to_git_root

    @staticmethod
    def create_repo_from_local_copy(
        revision: str, project_config: ProjectConfig
    ) -> "GitClient":
        with measure_performance(f"Copy Git repo: {revision}"):
            path_to_cwd = os.getcwd()
            if revision == "HEAD+":
                path_to_project_git_dir = os.path.join(path_to_cwd, ".git")
                assert os.path.isdir(path_to_project_git_dir)
                return GitClient(path_to_cwd)

            path_to_sandbox = os.path.join(
                project_config.get_path_to_cache_dir(), "git"
            )
            path_to_sandbox_git_repo = os.path.join(path_to_sandbox, revision)
            path_to_sandbox_git_repo_git = os.path.join(
                path_to_sandbox_git_repo, ".git"
            )
            if revision != "HEAD+" and os.path.exists(
                path_to_sandbox_git_repo_git
            ):
                git_client = GitClient(path_to_sandbox_git_repo)

                if git_client.is_clean_branch():
                    return git_client

            Path(path_to_sandbox).mkdir(parents=True, exist_ok=True)

            # Running git worktree add ... below results with "path already
            # exists" error if the destination folder already exists, even if
            # empty.
            if os.path.exists(path_to_sandbox_git_repo):
                shutil.rmtree(path_to_sandbox_git_repo)

            result = subprocess.run(
                [
                    "git",
                    "worktree",
                    "add",
                    "--force",
                    path_to_sandbox_git_repo,
                    revision,
                ],
                cwd=path_to_cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0, result

            git_client = GitClient(path_to_sandbox_git_repo)

            if revision != "HEAD+":
                git_client.hard_reset(revision=revision)
                git_client.clean()

            return git_client

    @staticmethod
    @contextmanager
    def create_unique_repo_from_local_copy(
        revision: str, project_config: ProjectConfig
    ) -> Iterator["GitClient"]:
        with measure_performance(f"Copy unique Git repo: {revision}"):
            path_to_cwd = os.getcwd()
            if revision == "HEAD+":
                path_to_project_git_dir = os.path.join(path_to_cwd, ".git")
                assert os.path.isdir(path_to_project_git_dir)
                yield GitClient(path_to_cwd)
                return

            path_to_sandbox = os.path.join(
                project_config.get_path_to_cache_dir(), "git"
            )
            Path(path_to_sandbox).mkdir(parents=True, exist_ok=True)

            sanitized_revision = "".join(
                character if character.isalnum() else "_"
                for character in revision[:32]
            )
            path_to_unique_worktree = tempfile.mkdtemp(
                prefix=f"{sanitized_revision}_",
                dir=path_to_sandbox,
            )

            result = subprocess.run(
                [
                    "git",
                    "worktree",
                    "add",
                    "--detach",
                    "--force",
                    path_to_unique_worktree,
                    revision,
                ],
                cwd=path_to_cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                shutil.rmtree(path_to_unique_worktree, ignore_errors=True)
                assert result.returncode == 0, result

            try:
                yield GitClient(path_to_unique_worktree)
            finally:
                remove_result = subprocess.run(
                    [
                        "git",
                        "worktree",
                        "remove",
                        "--force",
                        path_to_unique_worktree,
                    ],
                    cwd=path_to_cwd,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if remove_result.returncode != 0 and os.path.exists(
                    path_to_unique_worktree
                ):
                    shutil.rmtree(path_to_unique_worktree, ignore_errors=True)

    @staticmethod
    @contextmanager
    def create_cached_repo_from_local_copy(
        revision: str, project_config: ProjectConfig
    ) -> Iterator["GitClient"]:
        if revision == "HEAD+":
            path_to_cwd = os.getcwd()
            snapshot_revision = GitClient._create_head_plus_snapshot_revision(
                path_to_cwd
            )
            with GitClient.create_unique_repo_from_local_copy(
                snapshot_revision, project_config
            ) as git_client:
                yield git_client
            return

        with measure_performance(f"Copy/reuse cached Git repo: {revision}"):
            path_to_cwd = os.getcwd()
            path_to_git_cache_root = os.path.join(
                project_config.get_path_to_cache_dir(), "git"
            )
            path_to_cached_repos = os.path.join(
                path_to_git_cache_root, "by_sha"
            )
            path_to_lock_dir = os.path.join(path_to_git_cache_root, "locks")
            Path(path_to_cached_repos).mkdir(parents=True, exist_ok=True)
            Path(path_to_lock_dir).mkdir(parents=True, exist_ok=True)

            cached_repo_path = os.path.join(path_to_cached_repos, revision)
            lock_file_path = os.path.join(path_to_lock_dir, f"{revision}.lock")

            with GitClient._acquire_cache_lock(lock_file_path):
                if not GitClient._is_cached_worktree_ready(
                    cached_repo_path, revision
                ):
                    GitClient._remove_worktree_path(
                        path_to_cwd, cached_repo_path
                    )

                    result = subprocess.run(
                        [
                            "git",
                            "worktree",
                            "add",
                            "--detach",
                            "--force",
                            cached_repo_path,
                            revision,
                        ],
                        cwd=path_to_cwd,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    assert result.returncode == 0, result

                    ready_marker_path = GitClient._get_ready_marker_path(
                        cached_repo_path
                    )
                    with open(ready_marker_path, "w", encoding="utf8") as file_:
                        file_.write("ready\n")

            yield GitClient(cached_repo_path)

    @staticmethod
    def _create_head_plus_snapshot_revision(path_to_cwd: str) -> str:
        # Resolve HEAD first so we can fall back to it when there are no local
        # modifications to snapshot.
        head_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path_to_cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        assert head_result.returncode == 0, head_result
        head_revision = head_result.stdout.strip()

        # Build a snapshot commit from a temporary index file:
        # - does not mutate real index/stash/refs
        # - includes tracked and untracked files (`git add -A`)
        temp_index_fd, temp_index_path = tempfile.mkstemp(
            prefix="strictdoc_head_plus_index_"
        )
        os.close(temp_index_fd)
        try:
            snapshot_env = dict(os.environ)
            snapshot_env["GIT_INDEX_FILE"] = temp_index_path
            snapshot_env.setdefault("GIT_AUTHOR_NAME", "StrictDoc")
            snapshot_env.setdefault("GIT_AUTHOR_EMAIL", "strictdoc@example.com")
            snapshot_env.setdefault("GIT_COMMITTER_NAME", "StrictDoc")
            snapshot_env.setdefault(
                "GIT_COMMITTER_EMAIL", "strictdoc@example.com"
            )

            read_tree_result = subprocess.run(
                ["git", "read-tree", "HEAD"],
                cwd=path_to_cwd,
                env=snapshot_env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert read_tree_result.returncode == 0, read_tree_result

            add_result = subprocess.run(
                ["git", "add", "-A"],
                cwd=path_to_cwd,
                env=snapshot_env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert add_result.returncode == 0, add_result

            write_tree_result = subprocess.run(
                ["git", "write-tree"],
                cwd=path_to_cwd,
                env=snapshot_env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert write_tree_result.returncode == 0, write_tree_result
            tree_revision = write_tree_result.stdout.strip()

            commit_result = subprocess.run(
                ["git", "commit-tree", tree_revision, "-p", head_revision],
                cwd=path_to_cwd,
                env=snapshot_env,
                input="strictdoc HEAD+ snapshot\n",
                capture_output=True,
                text=True,
                check=False,
            )
            assert commit_result.returncode == 0, commit_result
            snapshot_revision = commit_result.stdout.strip()
            return (
                snapshot_revision
                if len(snapshot_revision) > 0
                else head_revision
            )
        finally:
            if os.path.exists(temp_index_path):
                os.remove(temp_index_path)

    @staticmethod
    @contextmanager
    def _acquire_cache_lock(lock_file_path: str) -> Iterator[None]:
        Path(lock_file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(lock_file_path, "a", encoding="utf8") as lock_file:
            if fcntl is not None:
                # POSIX path: advisory file lock that coordinates all server
                # threads/processes that lock the same file, including workers
                # from separate Python processes.
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                return

            # Non-POSIX fallback (e.g. Windows): no cross-process file lock is
            # available here, so we at least serialize access within this
            # Python process.
            with GitClient._acquire_fallback_thread_lock(lock_file_path):
                yield

    @staticmethod
    @contextmanager
    def _acquire_fallback_thread_lock(lock_key: str) -> Iterator[None]:
        # Keep one in-memory mutex per lock key so concurrent threads in this
        # process serialize creation/reuse of the same cached worktree.
        # This is intentionally a weaker guarantee than fcntl-based locking.
        with GitClient._fallback_locks_guard:
            lock = GitClient._fallback_locks.get(lock_key)
            if lock is None:
                lock = threading.Lock()
                GitClient._fallback_locks[lock_key] = lock
        with lock:
            yield

    @staticmethod
    def _get_ready_marker_path(worktree_path: str) -> str:
        return os.path.join(worktree_path, ".strictdoc_worktree_ready")

    @staticmethod
    def _is_cached_worktree_ready(worktree_path: str, revision: str) -> bool:
        git_dir_path = os.path.join(worktree_path, ".git")
        ready_marker_path = GitClient._get_ready_marker_path(worktree_path)
        if not os.path.isdir(worktree_path) or not os.path.exists(git_dir_path):
            return False
        if not os.path.isfile(ready_marker_path):
            return False
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return False
        return result.stdout.strip() == revision

    @staticmethod
    def _remove_worktree_path(path_to_cwd: str, worktree_path: str) -> None:
        if not os.path.exists(worktree_path):
            return

        remove_result = subprocess.run(
            ["git", "worktree", "remove", "--force", worktree_path],
            cwd=path_to_cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if remove_result.returncode != 0 and os.path.exists(worktree_path):
            shutil.rmtree(worktree_path, ignore_errors=True)

    def is_clean_branch(self) -> bool:
        #
        # https://unix.stackexchange.com/a/155077/77389
        #
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return False
        return result.stdout == ""

    def check_revision(self, revision: str) -> str:
        assert isinstance(revision, str)
        assert len(revision) > 0
        result = subprocess.run(
            ["git", "rev-parse", revision],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        raise LookupError(f"Non-existing Git revision: {revision}.")

    def hard_reset(self, revision: Optional[str] = None) -> None:
        reset_args = ["git", "reset", "--hard"]
        if revision is not None:
            reset_args.append(revision)
        result = subprocess.run(
            reset_args,
            cwd=self.path_to_git_root,
            capture_output=False,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result

    def clean(self) -> None:
        result = subprocess.run(
            ["git", "clean", "-fd"],
            cwd=self.path_to_git_root,
            capture_output=False,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result
