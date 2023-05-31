from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen


class Screen_StandaloneDocument(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # overridden for Screen_Document

    def assert_on_standalone_screen_document(self) -> None:
        super().assert_on_screen("standalone_document")

    def assert_empty_document(self) -> None:
        super().assert_empty_view("document-root-placeholder")

    def assert_not_empty_document(self) -> None:
        super().assert_not_empty_view("document-root-placeholder")
