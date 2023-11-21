from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen


class Screen_PDFDocument(Screen):
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def assert_on_pdf_document(self) -> None:
        super().assert_on_screen("html2pdf")
