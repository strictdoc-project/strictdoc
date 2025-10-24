import os.path
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.timing import measure_performance


class GitClient:
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
