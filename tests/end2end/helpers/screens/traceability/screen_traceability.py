from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen


class Screen_Traceability(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # overridden for Screen_Traceability

    def assert_on_screen_traceability(self) -> None:
        super().assert_on_screen("traceability")

    # Specific methods
