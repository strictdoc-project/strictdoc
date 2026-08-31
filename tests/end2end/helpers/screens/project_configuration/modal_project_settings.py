from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Modal_ProjectSettings:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_modal(self) -> None:
        self.test_case.assert_element('[data-testid="project-settings-form"]')

    def assert_not_on_modal(self) -> None:
        self.test_case.assert_element_absent(
            '[data-testid="project-settings-form"]'
        )

    #
    # Apply / dismiss state.
    #

    def assert_apply_disabled(self) -> None:
        apply_button = self.test_case.find_element(
            '[data-testid="project-settings-apply"]'
        )
        assert apply_button.is_enabled() is False

    def assert_apply_enabled(self) -> None:
        apply_button = self.test_case.find_element(
            '[data-testid="project-settings-apply"]'
        )
        assert apply_button.is_enabled() is True

    def assert_dismiss_label(self, text: str) -> None:
        self.test_case.assert_text(
            text, '[data-testid="project-settings-dismiss-label"]'
        )

    #
    # Features.
    #

    def assert_all_features_checked(self) -> None:
        checkbox = self.test_case.find_element(
            '[data-testid="project-settings-control-all-features"]'
        )
        assert checkbox.is_selected() is True

    def assert_feature_checked(self, feature_name: str) -> None:
        checkbox = self.test_case.find_element(
            f'[data-testid="project-settings-feature-{feature_name}"]'
        )
        assert checkbox.is_selected() is True

    def do_click_all_features(self) -> None:
        self.test_case.click(
            '[data-testid="project-settings-control-all-features"]'
        )

    def do_click_feature(self, feature_name: str) -> None:
        self.test_case.click(
            f'[data-testid="project-settings-feature-{feature_name}"]'
        )

    #
    # Apply / Close / Escape / discard confirmation.
    #

    def do_click_apply(self) -> None:
        self.test_case.click('[data-testid="project-settings-apply"]')
        self.test_case.wait_for_element_absent(
            '[data-testid="project-settings-reloading"]', timeout=20
        )

    def do_press_escape(self) -> None:
        self.test_case.send_keys("body", "", by=By.CSS_SELECTOR)

    def assert_discard_confirmation_visible(self) -> None:
        self.test_case.assert_element_visible(
            '[data-testid="project-settings-discard-confirmation"]'
        )

    def do_click_continue_editing(self) -> None:
        self.test_case.click(
            '[data-testid="project-settings-continue-editing"]'
        )
