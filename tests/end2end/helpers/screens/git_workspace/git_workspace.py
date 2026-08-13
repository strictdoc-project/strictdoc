from selenium.webdriver.common.by import By

from tests.end2end.helpers.screens.git_conflicts.git_conflicts import (
    Screen_GitConflicts,
)
from tests.end2end.helpers.screens.screen import Screen


class Screen_GitWorkspace(Screen):  # pylint: disable=invalid-name
    def do_check_status_row(self, path: str) -> None:
        xpath = (
            f"//*[@data-testid='git-workspace-status-row'][@data-status-path='{path}']"
            "//*[@data-testid='git-workspace-status-row-checkbox']"
        )
        self.test_case.click_xpath(xpath)

    def do_stage_selected(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-stage-action"]'
        )

    def do_fill_in_commit_message(self, message: str) -> None:
        self.do_fill_in_field_value(
            "//*[@data-testid='git-workspace-commit-message-field']",
            field_value=message,
        )

    def do_commit(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-commit-action"]'
        )

    def do_create_and_switch_branch(self, branch_name: str) -> None:
        self.do_fill_in_field_value(
            "//*[@data-testid='git-workspace-branch-name-field']",
            field_value=branch_name,
        )
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-branch-create-action"]'
        )

    def do_select_target_branch(self, branch_name: str) -> None:
        self.test_case.select_option_by_text(
            "//*[@data-testid='git-workspace-target-branch-field']",
            branch_name,
            dropdown_by=By.XPATH,
        )
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-target-branch-submit"]'
        )

    def do_sync(self) -> Screen_GitConflicts:
        # Per SDOC-SRS-217, Synchronize always lands on the git_conflicts
        # review screen by default (even with zero true conflicts, where
        # it's just an immediate Commit click) -- see do_sync_fast_forward
        # for the opt-in checkbox that restores the old auto-publish
        # shortcut.
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-sync-action"]'
        )
        return Screen_GitConflicts(self.test_case)

    def do_sync_fast_forward(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-fast-forward-checkbox"]'
        )
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-sync-action"]'
        )

    def do_push(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-push-action"]'
        )

    def do_force_push(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="git-workspace-force-push-action"]'
        )

    def assert_current_branch(self, branch_name: str) -> None:
        self.assert_xpath_contains(
            "//*[@data-testid='git-workspace-current-branch']", branch_name
        )

    def assert_message(self, text: str) -> None:
        self.assert_xpath_contains(
            "//*[@data-testid='git-workspace-message']", text
        )

    def assert_status_row_present(self, path: str) -> None:
        self.test_case.assert_element(
            f"//*[@data-testid='git-workspace-status-row'][@data-status-path='{path}']",
            by=By.XPATH,
        )
