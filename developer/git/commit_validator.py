import os
import re
import subprocess
from typing import List

ALLOWED_TYPES = [
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "refactor",
    "release",
    "test",
]


def is_github_ci() -> bool:
    return os.environ.get("GITHUB_ACTIONS") == "true"


def get_last_10_non_merge_commits():
    result = subprocess.run(
        [
            "git",
            "log",
            # Skip merge commits.
            "--no-merges",
            # Last 10 commits
            "-n",
            "10",
            # Full commit message + ASCII record separator.
            "--pretty=%B%x1e",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    # Split by the record separator and remove any empty strings.
    commit_messages = []
    for msg_ in result.stdout.split("\x1e"):
        msg = msg_.strip()
        if len(msg) == 0:
            continue
        # Merge commits still show up on GitHub CI because it does shallow checkouts.
        if "Merge" in msg:
            continue
        commit_messages.append(msg)
    return commit_messages


def validate_commits_locally_or_ci() -> None:
    commit_messages = get_last_10_non_merge_commits()
    if len(commit_messages) == 0:
        return
    validate_commits(commit_messages)


def validate_commits(commit_messages: List[str]):
    """
    Validate a commit message against conventional commit rules:

    <type>[optional scope]: <description>

    Conventional Commits spec:
    https://www.conventionalcommits.org/en/v1.0.0/
    """

    assert isinstance(commit_messages, list), commit_messages
    assert len(commit_messages) > 0, commit_messages

    bad_commits = 0
    commit_titles = []

    for commit_message_ in commit_messages:
        assert len(commit_message_) > 0

        # Only check the first line
        first_line = commit_message_.splitlines()[0]
        if "WIP" in first_line and not is_github_ci():
            commit_titles.append(f"WIP: {first_line}")
            continue

        # Regex breakdown:
        # ^(feat|fix|refactor|...)  -> type must be one of the allowed types
        # (\([^\)]+\))?         -> optional scope inside parentheses
        # :\s                   -> colon followed by a space
        # .+                    -> description must have at least one character
        pattern = r"^(" + "|".join(ALLOWED_TYPES) + r")(\([^\)]+\))?!?: .+"

        if re.match(pattern, first_line) is None:
            commit_titles.append(f"BAD: {first_line}")
            commit_titles.append(f"     {'^' * len(first_line)}")

            bad_commits += 1
        else:
            commit_titles.append(f"GOOD: {first_line}")

    if bad_commits > 0:
        commit_titles_list_line = "\n".join(commit_titles)

        message = f"""\
error: the commit message(s) do not match the Conventional Commits convention:

{commit_titles_list_line}

StrictDoc enforces the Conventional Commits starting from 2026.

The expected format of the commit line:

<type>[optional scope]: <description>

The <type> values accepted by StrictDoc are as follows:
{", ".join(ALLOWED_TYPES)}

The [optional scope] can be a strictdoc folder, e.g., 'export/html', or a
feature/topic, such as 'UI', 'html2pdf', 'Static HTML search'.

Examples:
- docs: update release notes
- feat(html2pdf): introduce a new "html2pdf_forced_page_break_nodes" option
- fix(backend/sdoc_source_code): enable support for requirement identifiers
- refactor(cli): migrate "import excel" and "import reqif" to a command pattern
- chore(cli): rename shared.py -> _shared.py
- chore(.github): switch the macOS tests to macos-latest

See the Conventional Commits spec:
https://www.conventionalcommits.org/en/v1.0.0/

NOTE: During local development, to bypass this check, include WIP anywhere in
the commit message.\
"""
        raise ValueError(message)
