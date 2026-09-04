import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_configuration.screen_project_configuration import (
    Screen_ProjectConfiguration,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self) -> None:
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            Screen_ProjectIndex(self).assert_on_screen()

            self.click('[data-testid="project-configuration-link"]')
            project_configuration = Screen_ProjectConfiguration(self)
            project_configuration.assert_on_screen()
            project_configuration.assert_project_tree_configuration_present()
            project_configuration.assert_project_features_value_contains(
                "ALL_FEATURES:"
            )

            # A failed request (network error or a non-2xx response) must
            # show a compact, dismissible notice instead of injecting the
            # raw server response into the page.
            project_configuration.do_simulate_request_failure()
            project_configuration.do_click_edit()
            project_configuration.assert_request_error_present()
            project_configuration.do_click_generic_modal_close()
            project_configuration.assert_request_error_absent()
            project_configuration.do_restore_request_handling()

            project_configuration.do_click_dashboard_input_path_external_toggle()
            project_configuration.assert_dashboard_input_path_external_expanded()

            modal = project_configuration.do_click_edit()
            modal.assert_on_modal()
            modal.assert_apply_disabled()
            modal.assert_dismiss_label("Close")

            modal.assert_all_features_checked()
            modal.assert_feature_checked("SEARCH")
            modal.do_click_all_features()
            modal.assert_feature_checked("SEARCH")
            modal.assert_apply_enabled()
            modal.assert_dismiss_label("Cancel")

            modal.do_press_escape()
            modal.assert_discard_confirmation_visible()
            modal.do_click_continue_editing()
            modal.do_press_escape()
            modal.do_press_escape()
            modal.assert_not_on_modal()

            modal = project_configuration.do_click_edit()
            modal.do_click_all_features()
            modal.do_click_feature("DIFF")
            modal.do_click_apply()
            project_configuration.assert_on_screen()

        config_path = os.path.join(
            test_setup.path_to_sandbox, "strictdoc_config.py"
        )
        with open(config_path, encoding="utf8") as config_file:
            config_source = config_file.read()
        assert "SEARCH" in config_source
        assert "DIFF" in config_source
        assert "ALL_FEATURES" not in config_source
        assert (
            len(
                [
                    filename_
                    for filename_ in os.listdir(test_setup.path_to_sandbox)
                    if filename_.startswith("strictdoc_config.py.saved.")
                ]
            )
            == 1
        )
