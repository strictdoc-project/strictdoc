from tests.end2end.helpers.screens.screen import Screen


class Screen_Diff(Screen):  # pylint: disable=invalid-name
    def do_enter_field_lhs(self, field_value: str):
        xpath_to_lhs_field = "(//*[@data-testid='diff-screen-field-lhs'])"

        self.do_fill_in_field_value(xpath_to_lhs_field, field_value=field_value)

    def do_enter_field_rhs(self, field_value: str):
        xpath_to_lhs_field = "(//*[@data-testid='diff-screen-field-rhs'])"

        self.do_fill_in_field_value(xpath_to_lhs_field, field_value=field_value)

    def do_submit(self):
        self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')

    def do_switch_tab_to_changelog(self):
        self.test_case.click_xpath(
            '//*[@data-testid="diff-screen-tab-changelog"]'
        )

    def assert_documents_modified(self, stats: str) -> None:
        xpath = '//*[@data-testid="table-row-value-documents-modified"]'
        self.assert_xpath_contains(xpath, stats)

    def assert_nodes_modified(self, node_type: str, stats: str) -> None:
        node_type_string = node_type.lower() + "-nodes"
        xpath = f'//*[@data-testid="table-row-value-{node_type_string}"]'
        self.assert_xpath_contains(xpath, stats)
