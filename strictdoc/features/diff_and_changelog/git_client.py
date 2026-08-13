import os.path
import shutil
import subprocess
import tempfile
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterator, List, Optional

fcntl: Optional[Any]
try:  # pragma: no cover
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.timing import measure_performance


@dataclass
class GitStatusEntry:
    path: str
    index_status: str
    worktree_status: str
    is_conflicted: bool
    original_path: Optional[str] = None


@dataclass
class GitCheckoutResult:
    success: bool
    error_message: Optional[str] = None


@dataclass
class GitPushResult:
    success: bool
    rejected_non_fast_forward: bool = False
    error_message: Optional[str] = None


class GitClient:
    _fallback_locks: Dict[str, threading.Lock] = {}
    _fallback_locks_guard = threading.Lock()

    _CONFLICT_STATUS_CODES: FrozenSet[str] = frozenset(
        {"UU", "AA", "DD", "AU", "UA", "UD", "DU"}
    )

    def __init__(self, path_to_git_root: str) -> None:
        assert os.path.isdir(path_to_git_root)
        self.path_to_git_root: str = path_to_git_root

    @staticmethod
    def open_workspace(project_config: ProjectConfig) -> "GitClient":
        # The seam for future multi-user workspace support: today there is
        # exactly one active workspace, the server's own working directory.
        # A future multi-user implementation can key a dedicated worktree by
        # session id under project_config.get_path_to_cache_dir()/git/
        # workspaces/<session_id> and return that instead.
        assert project_config is not None
        return GitClient(os.getcwd())

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
        revision: str,
        project_config: ProjectConfig,
        *,
        sparse_doc_paths_only: bool = False,
    ) -> Iterator["GitClient"]:
        """
        `sparse_doc_paths_only` (SDOC-LLR-211): check out only paths that
        look like SDoc/Markdown documents (``*.sdoc``, ``*.md``), not the
        full working tree. Safe wherever the caller only reads document
        structure (never source files, assets, or other non-document
        content) -- e.g. the Git workspace 3-way classifier, which always
        parses with ``skip_source_files=True``. Kept in a separate cache
        bucket from the default full checkout, since a sparse worktree
        cannot be safely handed to a caller expecting the full tree, or
        vice versa. Off by default so other callers (e.g. the Diff
        feature) keep getting a full checkout.

        Unlike `create_unique_repo_from_local_copy` (a fresh worktree torn
        down on every call), this reuses one worktree per revision across
        calls -- a revision's content is immutable, so the reuse is always
        correct, and it lets `PickleCache` (keyed partly by each file's
        absolute path) actually hit on repeated requests for the same
        revision instead of always missing because the previous checkout
        no longer exists.
        """
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
            cache_bucket = (
                "by_sha_sparse_docs" if sparse_doc_paths_only else "by_sha"
            )
            path_to_cached_repos = os.path.join(
                path_to_git_cache_root, cache_bucket
            )
            path_to_lock_dir = os.path.join(path_to_git_cache_root, "locks")
            Path(path_to_cached_repos).mkdir(parents=True, exist_ok=True)
            Path(path_to_lock_dir).mkdir(parents=True, exist_ok=True)

            cached_repo_path = os.path.join(path_to_cached_repos, revision)
            lock_file_path = os.path.join(
                path_to_lock_dir, f"{cache_bucket}_{revision}.lock"
            )

            with GitClient._acquire_cache_lock(lock_file_path):
                if not GitClient._is_cached_worktree_ready(
                    cached_repo_path, revision
                ):
                    GitClient._remove_worktree_path(
                        path_to_cwd, cached_repo_path
                    )

                    add_args = ["--detach", "--force"]
                    if sparse_doc_paths_only:
                        # No initial checkout -- populate the working tree
                        # after sparse-checkout patterns are configured
                        # below, so only matching paths ever get written.
                        add_args.append("--no-checkout")

                    result = subprocess.run(
                        [
                            "git",
                            "worktree",
                            "add",
                            *add_args,
                            cached_repo_path,
                            revision,
                        ],
                        cwd=path_to_cwd,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    assert result.returncode == 0, result

                    if sparse_doc_paths_only:
                        init_result = subprocess.run(
                            ["git", "sparse-checkout", "init", "--no-cone"],
                            cwd=cached_repo_path,
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        assert init_result.returncode == 0, init_result

                        for sparse_args in (
                            ["sparse-checkout", "set", "*.sdoc", "*.md"],
                            ["checkout", revision],
                        ):
                            sparse_result = subprocess.run(
                                ["git", *sparse_args],
                                cwd=cached_repo_path,
                                capture_output=True,
                                text=True,
                                check=False,
                            )
                            assert sparse_result.returncode == 0, sparse_result

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

    #
    # Isolated sync worktree.
    #
    # Unlike create_unique_repo_from_local_copy (auto-removed on context
    # exit) or create_repo_from_local_copy (revision-keyed, reused by SHA),
    # the sync worktree lives at one fixed path and survives across multiple
    # HTTP requests (sync -> view conflicts -> resolve_node*/resolve_section*
    # -> commit/abort), analogous to how there is only ever one in-progress
    # synchronization at a time under this feature's single-active-workspace
    # scope. It holds no live git rebase/merge state -- conflict detection
    # and resolution are computed entirely by StrictDoc's own 3-way node
    # classifier (three_way_merge_analyzer.py). This worktree is only used
    # as a `cwd` for the git-plumbing commands that materialize the final
    # single commit (read-tree/hash-object/write-tree/commit-tree) -- never
    # checked out for editing.
    #

    @staticmethod
    def create_sync_worktree(
        path_to_worktree: str,
        revision: str,
        project_config: ProjectConfig,
    ) -> "GitClient":
        assert project_config is not None
        path_to_cwd = os.getcwd()
        Path(path_to_worktree).parent.mkdir(parents=True, exist_ok=True)
        GitClient._remove_worktree_path(path_to_cwd, path_to_worktree)

        result = subprocess.run(
            [
                "git",
                "worktree",
                "add",
                "--detach",
                "--force",
                path_to_worktree,
                revision,
            ],
            cwd=path_to_cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            shutil.rmtree(path_to_worktree, ignore_errors=True)
            assert result.returncode == 0, result

        return GitClient(path_to_worktree)

    @staticmethod
    def open_sync_worktree(path_to_worktree: str) -> Optional["GitClient"]:
        # A worktree's ".git" is a file (pointing back at the main repo's
        # git-dir), not a directory, which distinguishes a valid worktree
        # from a stray/leftover directory at the same path.
        path_to_worktree_git_file = os.path.join(path_to_worktree, ".git")
        if not os.path.isfile(path_to_worktree_git_file):
            return None
        return GitClient(path_to_worktree)

    @staticmethod
    def remove_sync_worktree(path_to_worktree: str) -> None:
        GitClient._remove_worktree_path(os.getcwd(), path_to_worktree)

    def commit_tree_with_overrides(
        self,
        base_revision: str,
        overrides: Dict[str, Optional[bytes]],
        parent_revision: str,
        message: str,
    ) -> str:
        """
        Builds one new commit whose tree is `base_revision`'s tree with
        `overrides` applied on top -- a path mapped to `bytes` replaces that
        path's blob, a path mapped to `None` removes it -- and whose sole
        parent is `parent_revision`. Uses a scratch temporary index (never
        touches self's real index/working tree), following the same pattern
        as `_create_head_plus_snapshot_revision`.
        """
        temp_index_fd, temp_index_path = tempfile.mkstemp(
            prefix="strictdoc_merge_index_"
        )
        os.close(temp_index_fd)
        try:
            env = dict(os.environ)
            env["GIT_INDEX_FILE"] = temp_index_path
            env.setdefault("GIT_AUTHOR_NAME", "StrictDoc")
            env.setdefault("GIT_AUTHOR_EMAIL", "strictdoc@example.com")
            env.setdefault("GIT_COMMITTER_NAME", "StrictDoc")
            env.setdefault("GIT_COMMITTER_EMAIL", "strictdoc@example.com")

            read_tree_result = subprocess.run(
                ["git", "read-tree", base_revision],
                cwd=self.path_to_git_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert read_tree_result.returncode == 0, read_tree_result

            for path, content in overrides.items():
                if content is None:
                    remove_result = subprocess.run(
                        ["git", "update-index", "--force-remove", path],
                        cwd=self.path_to_git_root,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    assert remove_result.returncode == 0, remove_result
                    continue

                hash_result = subprocess.run(
                    ["git", "hash-object", "-w", "--stdin"],
                    input=content,
                    cwd=self.path_to_git_root,
                    env=env,
                    capture_output=True,
                    check=False,
                )
                assert hash_result.returncode == 0, hash_result
                blob_sha = hash_result.stdout.decode("utf-8").strip()

                update_result = subprocess.run(
                    [
                        "git",
                        "update-index",
                        "--add",
                        "--cacheinfo",
                        f"100644,{blob_sha},{path}",
                    ],
                    cwd=self.path_to_git_root,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert update_result.returncode == 0, update_result

            write_tree_result = subprocess.run(
                ["git", "write-tree"],
                cwd=self.path_to_git_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert write_tree_result.returncode == 0, write_tree_result
            tree_sha = write_tree_result.stdout.strip()

            commit_result = subprocess.run(
                ["git", "commit-tree", tree_sha, "-p", parent_revision],
                input=message,
                cwd=self.path_to_git_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert commit_result.returncode == 0, commit_result
            return commit_result.stdout.strip()
        finally:
            if os.path.exists(temp_index_path):
                os.remove(temp_index_path)

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

    def get_short_revision(self, revision: str) -> str:
        assert isinstance(revision, str)
        assert len(revision) > 0
        result = subprocess.run(
            ["git", "rev-parse", "--short", revision],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        raise LookupError(f"Non-existing Git revision: {revision}.")

    def get_tags_for_revision(self, revision: str) -> List[str]:
        assert isinstance(revision, str)
        assert len(revision) > 0
        result = subprocess.run(
            ["git", "tag", "--points-at", revision],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [tag for tag in result.stdout.splitlines() if len(tag) > 0]

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

    #
    # Branches.
    #

    def list_branches(self) -> List[str]:
        result = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result
        return [
            branch for branch in result.stdout.splitlines() if len(branch) > 0
        ]

    def get_current_branch(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result
        return result.stdout.strip()

    def checkout_branch(
        self, branch_name: str, *, create: bool = False
    ) -> GitCheckoutResult:
        if not self.is_clean_branch():
            return GitCheckoutResult(
                success=False,
                error_message=(
                    "Cannot switch branches: the workspace has uncommitted "
                    "changes. Commit or discard them first."
                ),
            )
        checkout_args = ["git", "checkout"]
        if create:
            checkout_args.append("-b")
        checkout_args.append(branch_name)
        result = subprocess.run(
            checkout_args,
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return GitCheckoutResult(success=False, error_message=result.stderr)
        return GitCheckoutResult(success=True)

    #
    # Status / staging / commit.
    #

    def get_status_porcelain(self) -> List[GitStatusEntry]:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z"],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result

        entries: List[GitStatusEntry] = []
        records = result.stdout.split("\0")
        record_idx = 0
        while record_idx < len(records):
            record = records[record_idx]
            record_idx += 1
            if len(record) == 0:
                continue
            status_code = record[:2]
            path = record[3:]
            original_path: Optional[str] = None
            # Renames/copies carry the original path as a second, separate
            # NUL-terminated record right after the current one.
            if status_code[0] in ("R", "C"):
                original_path = path
                path = records[record_idx]
                record_idx += 1
            entries.append(
                GitStatusEntry(
                    path=path,
                    index_status=status_code[0],
                    worktree_status=status_code[1],
                    is_conflicted=status_code
                    in GitClient._CONFLICT_STATUS_CODES,
                    original_path=original_path,
                )
            )
        return entries

    def stage_paths(self, paths: List[str]) -> None:
        assert len(paths) > 0
        result = subprocess.run(
            ["git", "add", "--", *paths],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result

    def commit(self, message: str) -> str:
        assert len(message.strip()) > 0, "Commit message must not be empty."
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result
        return self.check_revision("HEAD")

    #
    # Remote sync.
    #

    def merge_base(self, ref_a: str, ref_b: str) -> str:
        result = subprocess.run(
            ["git", "merge-base", ref_a, ref_b],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result
        return result.stdout.strip()

    def get_changed_paths(
        self, from_revision: str, to_revision: str
    ) -> List[str]:
        """
        Relative paths that differ between two revisions (added, removed, or
        modified) -- works directly against any two revisions already in
        this repo, no checkout/worktree needed.
        """
        result = subprocess.run(
            ["git", "diff", "--name-only", from_revision, to_revision],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result
        return [line for line in result.stdout.splitlines() if len(line) > 0]

    def push(
        self,
        remote: str = "origin",
        branch: Optional[str] = None,
        *,
        target_ref: Optional[str] = None,
        force_with_lease: bool = False,
    ) -> GitPushResult:
        branch_name = (
            branch if branch is not None else self.get_current_branch()
        )
        destination_ref = target_ref if target_ref is not None else branch_name
        push_args = ["git", "push"]
        if force_with_lease:
            push_args.append("--force-with-lease")
        push_args.extend([remote, f"{branch_name}:{destination_ref}"])
        result = subprocess.run(
            push_args,
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return GitPushResult(success=True)
        rejected_non_fast_forward = (
            "[rejected]" in result.stderr
            or "non-fast-forward" in result.stderr
            or "stale info" in result.stderr
        )
        return GitPushResult(
            success=False,
            rejected_non_fast_forward=rejected_non_fast_forward,
            error_message=result.stderr,
        )
