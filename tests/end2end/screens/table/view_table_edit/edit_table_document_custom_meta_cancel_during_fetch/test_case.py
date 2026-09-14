from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
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
            screen_project_index.do_click_on_first_document()

            self.clear_local_storage()

            screen_table = ViewType_Selector(self).do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.do_toggle_edit_mode()

            row = '[data-testid="document-config-metadata-row-custom_meta_0"]'
            field = f'{row} [data-testid="document-config-metadata-field"]'
            editor = '[data-testid="form-field-metadata-custom_meta_0"]'

            # Editor fetches must not depend on Turbo's deferred RAF render.
            self.execute_script(
                """
                window.__originalRAF = window.requestAnimationFrame;
                window.requestAnimationFrame = function () {
                    return 1;
                };
                """
            )

            try:
                self.click(field)
                self.wait_for_element(editor)
                screen_table.do_cancel_inline_cell_by_escape()
            finally:
                self.execute_script(
                    "window.requestAnimationFrame = window.__originalRAF;"
                )

            assert (
                self.get_attribute(field, "data-mode", hard_fail=False) or ""
            ) != "editing"
            # sdoc-contenteditable and active_form_key only exist in the
            # field's edit-mode markup (see document_custom_meta.jinja);
            # display mode has neither, so their absence confirms the cell
            # actually stayed in display mode rather than merely losing the
            # data-mode attribute while edit-mode markup lingered.
            self.assert_element_not_present(
                f"{field} sdoc-contenteditable, "
                f'{field} input[name="active_form_key"]'
            )
            self.assert_text("First value", selector=row)

        assert test_setup.compare_sandbox_and_expected_output()
