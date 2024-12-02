# mypy: disable-error-code="no-untyped-def"
import os
import subprocess
from typing import Optional


class GitClient:
    def __init__(self, commit_hash: Optional[str]):
        self._commit_hash: Optional[str] = commit_hash
        self._branch: Optional[str] = None

    @staticmethod
    def create():
        commit_hash: Optional[str] = None
        try:
            commit_hash = (
                subprocess.check_output(
                    ["git", "describe", "--always", "--tags"], cwd=os.getcwd()
                )
                .decode("ascii")
                .strip()
            )
        except subprocess.CalledProcessError:
            commit_hash = "Git information is not available"
        except FileNotFoundError:
            commit_hash = "Git not available"
        return GitClient(commit_hash=commit_hash)

    def get_commit_hash(self) -> Optional[str]:
        if self._commit_hash is not None:
            return self._commit_hash
        try:
            process_result = subprocess.run(
                ["git", "describe", "--always", "--tags"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                check=False,
            )
            if process_result.returncode != 0:
                return "N/A"
            commit_hash = process_result.stdout
        except subprocess.CalledProcessError:
            commit_hash = "N/A"
        except FileNotFoundError:
            commit_hash = "Git not available"
        self._commit_hash = commit_hash.strip()
        return self._commit_hash

    def get_branch(self) -> Optional[str]:
        if self._branch is not None:
            return self._branch
        try:
            process_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                check=False,
            )
            if process_result.returncode != 0:
                return "N/A"
            branch = process_result.stdout
        except subprocess.CalledProcessError:
            branch = "N/A"
        except FileNotFoundError:
            branch = "Git not available"
        self._branch = branch.strip()
        return self._branch
