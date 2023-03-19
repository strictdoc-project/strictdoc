from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen


class Screen_Table(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # overridden for Screen_Table

    def assert_on_screen_table(self) -> None:
        super().assert_on_screen("table")

    # Specific methods
