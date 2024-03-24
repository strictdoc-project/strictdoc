import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.document.form_edit_grammar_elements import (
    Form_EditGrammarElements,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_not_empty_document()

            screen_document.assert_text("abcdef123456")

            form_edit_grammar: Form_EditGrammarElements = (
                screen_document.do_open_modal_form_edit_grammar()
            )
            form_edit_grammar.assert_file_grammars_are_not_supported()
