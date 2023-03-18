from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.toc import TOC
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC112_T01_UI_toc(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document title")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document title")
            screen_document.assert_text("Hello world!")

            screen_toc: TOC = screen_document.get_toc()

            # toc is on the page, open and contains Section title
            screen_toc.assert_toc_opened()
            screen_toc.assert_toc_contains("Section title")

            # hide the toc
            screen_toc.do_toggle_toc()

            # toc is hidden, but still contains Section title
            screen_toc.assert_toc_closed()
            screen_toc.assert_toc_contains("Section title")

            # show the toc
            screen_toc.do_toggle_toc()

            # toc is open
            screen_toc.assert_toc_opened()

        assert test_setup.compare_sandbox_and_expected_output()
