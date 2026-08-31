from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.project_configuration.modal_project_settings import (
    Modal_ProjectSettings,
)
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

    def assert_edit_action_present(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="project-configuration-edit"]',
            by=By.XPATH,
        )

    def assert_edit_unavailable_message(self, text: str) -> None:
        self.test_case.assert_text(
            text,
            '[data-testid="project-configuration-edit-unavailable"]',
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

    def do_click_edit(self) -> Modal_ProjectSettings:
        self.test_case.click('[data-testid="project-configuration-edit"]')
        return Modal_ProjectSettings(self.test_case)

    #
    # Failed request handling. Simulates a network error / non-2xx response
    # so the "Enable / disable features" click hits the failure path instead
    # of a real server round trip.
    #

    def do_simulate_request_failure(self) -> None:
        self.test_case.execute_script(
            "window.__originalFetch = window.fetch;"
            "window.fetch = () => Promise.resolve("
            "new Response('', { status: 500 }));"
        )

    def do_restore_request_handling(self) -> None:
        self.test_case.execute_script("window.fetch = window.__originalFetch;")

    def assert_request_error_present(self) -> None:
        self.test_case.assert_element(
            '[data-testid="project-settings-request-error"]'
        )

    def assert_request_error_absent(self) -> None:
        self.test_case.assert_element_absent(
            '[data-testid="project-settings-request-error"]'
        )

    def do_click_generic_modal_close(self) -> None:
        self.test_case.click("[data-js-modal-cancel-button]")
