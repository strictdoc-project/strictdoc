# mypy: disable-error-code="no-untyped-def"
import os
import subprocess
from typing import Optional


class GitClient:
    def __init__(self, commit_hash: Optional[str]):
        self._commit_hash: Optional[str] = commit_hash

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
        return self._commit_hash
