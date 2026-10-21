from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen


class Screen_ProjectConfiguration(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="project-configuration-page"]',
            by=By.XPATH,
        )

    def assert_project_tree_configuration_present(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="project-tree-configuration"]',
            by=By.XPATH,
        )

    def assert_project_features_value_contains(self, text: str) -> None:
        self.test_case.assert_text(
            text,
            '[data-testid="table-row-value-project-features"]',
        )

    #
    # Dashboard: external path prefix reveal/hide toggle.
    #

    def assert_dashboard_input_path_present(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="project-configuration-input-path"]',
            by=By.XPATH,
        )

    def assert_dashboard_input_path_external_toggle_present(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="project-configuration-input-path-external"]',
            by=By.XPATH,
        )

    def assert_dashboard_input_path_external_full_hidden(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="project-configuration-input-path"]'
            '//*[@class="dashboard-path-external-full"]',
            by=By.XPATH,
        )

    def assert_dashboard_input_path_external_full_visible(self) -> None:
        self.test_case.assert_element_visible(
            '//*[@data-testid="project-configuration-input-path"]'
            '//*[@class="dashboard-path-external-full"]',
            by=By.XPATH,
        )

    def do_click_dashboard_input_path_external_toggle(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="project-configuration-input-path-external"]'
        )

    def assert_dashboard_input_path_external_expanded(self) -> None:
        self.test_case.assert_attribute(
            '[data-testid="project-configuration-input-path-external"]',
            "aria-expanded",
            "true",
        )

    def assert_dashboard_source_root_path_present(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="project-configuration-source-root-path"]',
            by=By.XPATH,
        )

    def assert_dashboard_source_root_path_external_toggle_present(
        self,
    ) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="project-configuration-source-root-path-external"]',
            by=By.XPATH,
        )

    def assert_dashboard_source_root_path_external_full_hidden(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="project-configuration-source-root-path"]'
            '//*[@class="dashboard-path-external-full"]',
            by=By.XPATH,
        )

    def assert_dashboard_source_root_path_external_full_visible(
        self,
    ) -> None:
        self.test_case.assert_element_visible(
            '//*[@data-testid="project-configuration-source-root-path"]'
            '//*[@class="dashboard-path-external-full"]',
            by=By.XPATH,
        )

    def do_click_on_dashboard_source_root_path_external_toggle(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="project-configuration-source-root-path-external"]'
        )
