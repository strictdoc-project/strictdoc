# mypy: disable-error-code="no-untyped-def"
import os
import subprocess
from typing import Optional


class GitClient:
    def __init__(self) -> None:
        self._commit_hash: Optional[str] = None
        self._commit_date: Optional[str] = None
        self._commit_datetime: Optional[str] = None
        self._branch: Optional[str] = None

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

    def get_commit_date(self) -> Optional[str]:
        if self._commit_date is not None:
            return self._commit_date
        try:
            process_result = subprocess.run(
                ["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                check=False,
            )
            if process_result.returncode != 0:
                return "N/A"
            commit_date = process_result.stdout
        except subprocess.CalledProcessError:
            commit_date = "N/A"
        except FileNotFoundError:
            commit_date = "Git not available"
        self._commit_date = commit_date.strip()
        return self._commit_date

    def get_commit_datetime(self) -> Optional[str]:
        if self._commit_datetime is not None:
            return self._commit_datetime
        try:
            process_result = subprocess.run(
                [
                    "git",
                    "log",
                    "-1",
                    "--format=%cd",
                    "--date=format:%Y-%m-%d %H:%M:%S",
                ],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                check=False,
            )
            if process_result.returncode != 0:
                return "N/A"
            commit_datetime = process_result.stdout
        except subprocess.CalledProcessError:
            commit_datetime = "N/A"
        except FileNotFoundError:
            commit_datetime = "Git not available"
        self._commit_datetime = commit_datetime.strip()
        return self._commit_datetime

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
