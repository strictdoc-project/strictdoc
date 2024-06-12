from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_grammar import (
    Form_EditGrammar,
)
from tests.end2end.helpers.screens.document.form_edit_grammar_elements import (
    Form_EditGrammarElements,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")

            screen_document.assert_text("Requirement title")

            form_edit_grammar: Form_EditGrammarElements = (
                screen_document.do_open_modal_form_edit_grammar()
            )
            form_edit_grammar.assert_on_grammar()

            form_edit_grammar_element: Form_EditGrammar = (
                form_edit_grammar.do_click_edit_grammar_element(2)
            )
            form_edit_grammar_element.assert_on_grammar()

            form_edit_grammar_element.assert_tab_is_open("Fields")

            custom_field_mid = (
                form_edit_grammar_element.get_existing_mid_by_field_name(
                    "CUSTOM_FIELD"
                )
            )

            form_edit_grammar_element.do_fill_in_grammar_field_human_title_mid(
                custom_field_mid, "Custom Field 2"
            )

            form_edit_grammar_element.do_form_submit()

            screen_document.assert_text("CUSTOM FIELD 2")

        assert test_setup.compare_sandbox_and_expected_output()
