import os
import subprocess
from typing import List, Optional


class GitClient:
    def __init__(self) -> None:
        self._commit_hash: Optional[str] = None
        self._commit_date: Optional[str] = None
        self._commit_datetime: Optional[str] = None
        self._branch: Optional[str] = None

    def get_commit_hash(self) -> Optional[str]:
        if self._commit_hash is not None:
            return self._commit_hash
        commit_hash = self._run_git_command(
            ["git", "describe", "--always", "--tags"],
        )
        self._commit_hash = commit_hash.strip()
        return self._commit_hash

    def get_commit_date(self) -> Optional[str]:
        if self._commit_date is not None:
            return self._commit_date
        commit_date = self._run_git_command(
            ["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d"]
        )
        self._commit_date = commit_date.strip()
        return self._commit_date

    def get_commit_datetime(self) -> Optional[str]:
        if self._commit_datetime is not None:
            return self._commit_datetime
        commit_datetime = self._run_git_command(
            [
                "git",
                "log",
                "-1",
                "--format=%cd",
                "--date=format:%Y-%m-%d %H:%M:%S",
            ],
        )
        self._commit_datetime = commit_datetime.strip()
        return self._commit_datetime

    def get_branch(self) -> Optional[str]:
        if self._branch is not None:
            return self._branch
        branch = self._run_git_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        )
        self._branch = branch.strip()
        return self._branch

    @staticmethod
    def _run_git_command(args: List[str]) -> str:
        result: str
        try:
            process_result = subprocess.run(
                args,
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                check=False,
            )
            if process_result.returncode != 0:
                return "N/A"
            result = process_result.stdout
        except subprocess.CalledProcessError:
            result = "N/A"
        except FileNotFoundError:
            result = "Git not available"
        return result
