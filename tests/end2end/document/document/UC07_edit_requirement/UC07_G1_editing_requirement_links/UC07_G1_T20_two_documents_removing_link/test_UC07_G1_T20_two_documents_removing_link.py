from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC07_G1_T20_TwoDocumentsRemovingLink(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)
            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            # First, go to first document and check that the first document's
            # requirement REQ-001 does contain a child link to REQ-002.
            screen_document1 = screen_document_tree.do_click_on_the_document(1)
            screen_document1.assert_text("Hello world!")
            requirement1 = screen_document1.get_requirement()
            requirement1.assert_requirement_has_child_link("REQ-002")

            # Go back to tree
            self.open(test_server.get_host_and_port())

            # Go to second document and check that the first document's
            # requirement REQ-001 does contain a parent link to REQ-001,
            screen_document2 = screen_document_tree.do_click_on_the_document(2)
            screen_document2.assert_text("Hello world 2!")
            requirement2 = screen_document2.get_requirement()
            requirement2.assert_requirement_has_parent_link("REQ-001")

            # and remove the parent link to REQ-001.
            form_edit_requirement: Form_EditRequirement = (
                requirement2.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_delete_parent_link()
            # Make sure that the field is removed from the form:
            form_edit_requirement.assert_form_has_no_parents()
            form_edit_requirement.do_form_submit()

            # Now check that the documents do not have the link anymore.
            self.open(test_server.get_host_and_port())
            screen_document1 = screen_document_tree.do_click_on_the_document(1)
            screen_document1.assert_text("Hello world!")
            requirement1 = screen_document1.get_requirement()
            requirement1.assert_requirement_has_not_child_link("REQ-002")

            self.open(test_server.get_host_and_port())
            screen_document2 = screen_document_tree.do_click_on_the_document(2)
            screen_document2.assert_text("Hello world 2!")
            requirement2 = screen_document2.get_requirement()
            requirement2.assert_requirement_has_not_parent_link("REQ-001")

        assert test_setup.compare_sandbox_and_expected_output()
