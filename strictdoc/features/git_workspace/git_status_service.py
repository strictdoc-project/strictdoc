from dataclasses import dataclass, field
from typing import List

from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.diff_and_changelog.git_client import (
    GitClient,
    GitStatusEntry,
)
from strictdoc.features.git_workspace.sync_worktree_service import (
    SyncMergeService,
)

UNSTAGED_STATUS_CODES = frozenset({" ", "?"})


@dataclass
class GitWorkspaceStatus:
    current_branch: str
    branches: List[str]
    status_entries: List[GitStatusEntry] = field(default_factory=list)
    is_clean: bool = True
    is_sync_pending: bool = False

    @property
    def has_staged_changes(self) -> bool:
        return any(
            entry.index_status not in UNSTAGED_STATUS_CODES
            for entry in self.status_entries
        )

    @property
    def has_unstaged_changes(self) -> bool:
        return any(
            entry.worktree_status not in UNSTAGED_STATUS_CODES
            for entry in self.status_entries
        )


class GitWorkspaceStatusService:
    @staticmethod
    def get_status(project_config: ProjectConfig) -> GitWorkspaceStatus:
        git_client = GitClient.open_workspace(project_config)
        # Synchronize computes its 3-way merge/conflict state entirely in
        # isolated scratch worktrees (see SyncMergeService), never on this
        # live working directory -- so a pending sync is detected via
        # SyncMergeService's persisted state, not any git-level state on
        # this client.
        is_sync_pending = (
            SyncMergeService.get_active(project_config) is not None
        )
        return GitWorkspaceStatus(
            current_branch=git_client.get_current_branch(),
            branches=git_client.list_branches(),
            status_entries=git_client.get_status_porcelain(),
            is_clean=git_client.is_clean_branch(),
            is_sync_pending=is_sync_pending,
        )
