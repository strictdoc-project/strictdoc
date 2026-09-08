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

            # table_view_edit.js checks isEditRequestCurrent() once, right
            # when the field's inline-editor fetch resolves, to decide
            # whether to apply the response at all. That check is not the
            # race: it already rejects a response for a cell cancelled
            # *before* the fetch resolved. The race is narrower: Turbo
            # applies a *passed* check's <turbo-stream> on its own
            # requestAnimationFrame, and the cell can still be cancelled in
            # the single frame between the check passing and that callback
            # firing. Reproducing it means widening that one-frame window,
            # not delaying the fetch. Delaying every requestAnimationFrame
            # callback on the page does that: Turbo's deferred mutation and
            # the fix's own deferred revert check are both registered (in
            # that order) the instant the real, undelayed fetch resolves,
            # then both fire this many ms later instead of one frame later
            # — giving Escape a wide window to land in between, instead of
            # a ~16ms one no WebDriver command can reliably hit.
            # Left permanently overridden, this would also delay whatever
            # else on the page uses requestAnimationFrame (e.g. the dev
            # server's own live-reload client), which broke this test's own
            # teardown when tried. Restore the original once the race window
            # this test needs has passed.
            self.execute_script(
                """
                window.__originalRAF = window.requestAnimationFrame;
                window.requestAnimationFrame = function (callback) {
                    return setTimeout(() => callback(performance.now()), 300);
                };
                """
            )

            self.click(field)
            # Fires while the fetch has already resolved and both the
            # pending Turbo mutation and the fix's revert check are queued,
            # but before either has run (see the delay above).
            screen_table.do_cancel_inline_cell_by_escape()

            # Wait past the artificial 300ms delay so Turbo's queued mutation
            # and the fix's revert check have both had a chance to run, then
            # confirm the cancel stuck rather than being overwritten.
            self.sleep(0.6)

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
