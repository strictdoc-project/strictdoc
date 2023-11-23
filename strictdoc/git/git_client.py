import os.path
import subprocess
from typing import Optional


class GitClient:
    def __init__(self, path_to_git_root: str):
        assert os.path.isdir(path_to_git_root)
        self.path_to_git_root: str = path_to_git_root

    def add_file(self, path_to_file):
        result = subprocess.run(
            ["git", "add", path_to_file],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result

    def add_all(self):
        result = subprocess.run(
            ["git", "add", "."],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result

    def commit(self, message: str):
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result

    def check_revision(self, revision: str):
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
        raise LookupError(f"Non-existing revision: {revision}")

    def commit_all(self, message: str):
        result = subprocess.run(
            ["git", "commit", "-a", "-m", message],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result

    def rebase_from_main(self):
        result = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result
        result = subprocess.run(
            ["git", "rebase", "origin/main"],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result

    def push(self):
        result = subprocess.run(
            ["git", "push", "origin"],
            cwd=self.path_to_git_root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result

    def hard_reset(self, revision: Optional[str] = None):
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

    def clean(self):
        result = subprocess.run(
            ["git", "clean", "-fd"],
            cwd=self.path_to_git_root,
            capture_output=False,
            text=True,
            check=True,
        )
        assert result.returncode == 0, result
