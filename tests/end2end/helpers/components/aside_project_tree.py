from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class AsideProjectTree:  # pylint: disable=invalid-name
    """Table of contents"""

    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # data-testid="tree-bar"
    # data-testid="aside-project-tree"

    # base actions

    def assert_is_aside_tree(self) -> None:
        self.assert_tree_panel()
        self.assert_aside_project_tree()

    def assert_tree_panel(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="tree-bar"]',
            by=By.XPATH,
        )

    def assert_aside_project_tree(self) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='aside-project-tree']",
            by=By.XPATH,
        )

    def assert_tree_opened(self) -> None:
        # tree bar has attribute
        self.test_case.assert_element(
            '//*[@data-testid="tree-bar"][@data-state="open"]',
            by=By.XPATH,
        )
        # tree is visible
        self.test_case.assert_element_visible(
            '//*[@data-testid="aside-project-tree"]',
            by=By.XPATH,
        )

    def assert_tree_closed(self) -> None:
        # tree bar has attribute
        self.test_case.assert_element(
            '//*[@data-testid="tree-bar"][@data-state="closed"]',
            by=By.XPATH,
        )
        # tree is hidden
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="aside-project-tree"]',
            by=By.XPATH,
        )

    def do_toggle_tree(self) -> None:
        self.test_case.click_xpath("//*[@data-testid='tree-handler-button']")

    def assert_tree_contains(self, string: str) -> None:
        """The string does not need be visible (tree may be hidden)."""
        self.test_case.assert_element_present(
            (
                "//*[@data-testid='aside-project-tree']"
                f"//*[contains(., '{string}')]"
            ),
            by=By.XPATH,
        )

    def assert_tree_contains_not(self, string: str) -> None:
        """The string should not be contained in the tree (it may be hidden)."""
        self.test_case.assert_element_not_present(
            (
                "//*[@data-testid='aside-project-tree']"
                f"//*[contains(., '{string}')]"
            ),
            by=By.XPATH,
        )

    def assert_tree_contains_document_title(self, title: str) -> None:
        """The string does not need be visible (tree may be hidden)."""
        self.test_case.assert_element_present(
            (
                "//*[@data-testid='aside-project-tree']"
                "//a[@data-testid='tree-document-link']"
                f"/div[@title='{title}']"
            ),
            by=By.XPATH,
        )

    # TREE links

    def do_tree_go_to_document(self, title) -> None:
        self.test_case.click_xpath(
            "//*[@data-testid='aside-project-tree']"
            "//a[@data-testid='tree-document-link']"
            f"/div[@title='{title}']"
        )
