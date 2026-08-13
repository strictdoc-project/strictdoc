from tests.end2end.helpers.screens.screen import Screen


class Screen_GitConflicts(Screen):  # pylint: disable=invalid-name
    def do_use_incoming(self, path: str) -> None:
        xpath = (
            f"//*[@data-testid='git-conflicts-document'][@data-conflict-path='{path}']"
            "//*[@data-testid='git-conflicts-use-incoming-action']"
        )
        self.test_case.click_xpath(xpath)

    def do_use_target(self, path: str) -> None:
        xpath = (
            f"//*[@data-testid='git-conflicts-document-target'][@data-conflict-path='{path}']"
            "//*[@data-testid='git-conflicts-use-target-action']"
        )
        self.test_case.click_xpath(xpath)

    def do_commit(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="git-conflicts-commit-action"]'
        )

    def do_abort(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="git-conflicts-abort-action"]'
        )

    def assert_conflict_present(self, path: str) -> None:
        self.test_case.assert_element(
            f"//*[@data-testid='git-conflicts-document'][@data-conflict-path='{path}']"
        )

    def assert_incoming_content(self, text: str) -> None:
        self.assert_xpath_contains(
            "//*[@data-testid='git-conflicts-document']", text
        )

    def assert_target_content(self, text: str) -> None:
        self.assert_xpath_contains(
            "//*[@data-testid='git-conflicts-document-target']", text
        )

    def assert_node_expanded(self, node_key: str) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='git-conflicts-node']"
            f"[@data-node-key='{node_key}'][@open]"
        )

    def assert_node_collapsed(self, node_key: str) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='git-conflicts-node']"
            f"[@data-node-key='{node_key}'][not(@open)]"
        )

    def do_drag_node_after(self, node_key: str, after_key: str) -> None:
        # Drags a genuinely-new (auto-merged, non-conflicting) node from
        # the left/incoming column onto the drop zone in the right/target
        # column keyed by `after_key` (or "__start__" for "before all
        # siblings") -- see git_conflicts_reorder.js. Submitting the drop's
        # hidden form is a normal full-page POST-redirect-GET, so no extra
        # polling is needed afterward (unlike the TOC's Turbo-based drag,
        # e.g. Screen_Document.do_drag_toc_node) -- the next assertion just
        # runs against the freshly reloaded page.
        xpath_from = (
            "//*[@data-testid='git-conflicts-node']"
            f"[@data-node-key='{node_key}'][@draggable='true']"
        )
        xpath_to = (
            "//*[@data-testid='git-conflicts-drop-zone']"
            f"[@data-after-key='{after_key}']"
        )
        self.test_case.drag_and_drop(xpath_from, xpath_to)
