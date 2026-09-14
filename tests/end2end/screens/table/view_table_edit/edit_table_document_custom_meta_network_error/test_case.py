from selenium.webdriver.support.wait import WebDriverWait

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
            error = '[data-testid="table-inline-field-error"]'

            # An HTTP error while loading the editor must restore display mode.
            # Otherwise, the cell remains marked as editing without an input
            # that the user can correct or close.
            self.execute_script(
                """
                const originalFetch = window.fetch;
                window.fetch = async function(input, init) {
                    if (
                        String(input).includes(
                            '/actions/table/get_document_custom_meta_inline'
                        )
                    ) {
                        window.fetch = originalFetch;
                        return new Response('Editor load failed', {
                            status: 500,
                        });
                    }
                    return originalFetch(input, init);
                };
                """
            )

            self.click(field)
            WebDriverWait(self.driver, 10).until(
                lambda _: (
                    (
                        self.get_attribute(field, "data-mode", hard_fail=False)
                        or ""
                    )
                    != "editing"
                )
            )
            self.assert_text("First value", selector=row)

            # A rejected fetch follows a different JavaScript path from an HTTP
            # error. The rejected fetch must also restore display mode so the
            # user can open the cell again.
            self.execute_script(
                """
                const originalFetch = window.fetch;
                window.fetch = function(input, init) {
                    if (
                        String(input).includes(
                            '/actions/table/get_document_custom_meta_inline'
                        )
                    ) {
                        window.fetch = originalFetch;
                        return Promise.reject(new TypeError('Network error'));
                    }
                    return originalFetch(input, init);
                };
                """
            )

            self.click(field)
            WebDriverWait(self.driver, 10).until(
                lambda _: (
                    (
                        self.get_attribute(field, "data-mode", hard_fail=False)
                        or ""
                    )
                    != "editing"
                )
            )
            self.assert_text("First value", selector=row)

            # A network failure while saving must keep the input available.
            # The next outside click retries the same value and closes the
            # editor only after the server accepts it.
            self.execute_script(
                """
                const originalFetch = window.fetch;
                window.fetch = function(input, init) {
                    if (
                        String(input).includes(
                            '/actions/table/update_document_custom_meta'
                        )
                    ) {
                        window.fetch = originalFetch;
                        return Promise.reject(new TypeError('Network error'));
                    }
                    return originalFetch(input, init);
                };
                """
            )

            self.click(field)
            self.type(editor, "Saved after retry")
            screen_table.do_save_inline_cell_by_outside_click()

            self.assert_exact_text("Unable to save this field.", error)
            assert self.get_text(editor) == "Saved after retry"

            self.click(field)
            screen_table.do_save_inline_cell_by_outside_click()
            self.assert_element_not_present(editor)
            self.assert_text("Saved after retry", selector=row)

        assert test_setup.compare_sandbox_and_expected_output()
