from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_grammar import (
    Form_EditGrammar,
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
            screen_document.assert_text("Hello world!")

            screen_document.assert_text("Requirement title")

            form_edit_grammar: Form_EditGrammar = (
                screen_document.do_open_modal_form_edit_grammar()
            )
            form_edit_grammar.assert_on_grammar()

            form_edit_grammar.do_open_tab("Relations")
            relation1_mid = form_edit_grammar.do_add_grammar_relation()
            form_edit_grammar.do_fill_in_grammar_relation_role(
                relation1_mid, "ROLE"
            )

            relation2_mid = form_edit_grammar.do_add_grammar_relation()
            form_edit_grammar.do_fill_in_grammar_relation_role(
                relation2_mid, "ROLE"
            )

            form_edit_grammar.do_form_submit_and_catch_error(
                "A duplicated relation and role: Parent (ROLE). "
                "A grammar must have zero or one relations with a given type "
                "and a given role."
            )

        assert test_setup.compare_sandbox_and_expected_output()
