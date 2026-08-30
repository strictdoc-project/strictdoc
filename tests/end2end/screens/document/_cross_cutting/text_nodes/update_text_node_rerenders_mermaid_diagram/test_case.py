import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()

            self.assert_element("pre.mermaid svg")

            node = screen_document.get_node(2)
            edit_form: Form_EditRequirement = (
                node.do_open_form_edit_requirement()
            )
            edit_form.assert_on_form()
            edit_form.do_fill_in_field_statement(
                ".. raw:: html\n\n"
                '    <pre class="mermaid">\n'
                "    graph TD\n"
                "    A[Enter Chart Definition] --> B(Preview again)\n"
                "    </pre>\n"
            )
            edit_form.do_form_submit()

            # The re-rendered diagram must appear without a page reload:
            # this is a regression test for a bug where the diagram
            # rendered on initial page load but not after a Turbo Stream
            # node update (i.e. after editing and saving the node).
            self.assert_element("pre.mermaid svg")

            assert test_setup.compare_sandbox_and_expected_output()
