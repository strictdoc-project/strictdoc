from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import BaseCase

from tests.end2end.helpers.components.modal import Modal


class MoveNodeModal(Modal):  # pylint: disable=invalid-name
    """
    Page object for the "Move node" project-tree picker modal.

    Visible rows and actions use stable data-testid hooks. Assertions about
    tree behavior use the data-js-move-node-tree-* contract shared with the
    controller. No selector depends on presentation classes.
    """

    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def assert_modal(self) -> None:
        self.test_case.assert_element(
            '//sdoc-modal//*[@data-testid="move-node-tree"]',
            by=By.XPATH,
        )

    @staticmethod
    def _row_xpath(node_title: str) -> str:
        return (
            "//*[@data-testid='move-node-title']"
            f"[normalize-space()='{node_title}']"
            "/ancestor::li[@data-testid='move-node-row'][1]"
        )

    @staticmethod
    def _document_xpath(document_title: str) -> str:
        return (
            "//*[@data-testid='move-node-title']"
            f"[normalize-space()='{document_title}']"
            "/ancestor::li[@data-testid='move-node-document'][1]"
        )

    def assert_row_present(self, node_title: str) -> None:
        self._ensure_item_visible(self._row_xpath(node_title))
        self.test_case.assert_element(
            self._row_xpath(node_title),
            by=By.XPATH,
        )

    def assert_row_has_node_type(self, node_title: str, node_type: str) -> None:
        row_xpath = self._row_xpath(node_title)
        self._ensure_item_visible(row_xpath)
        self.test_case.assert_element(
            f"{row_xpath}//*[@data-testid='move-node-type']/*"
            f"[@text='{node_type}']",
            by=By.XPATH,
        )

    def assert_row_precedes(
        self, first_node_title: str, second_node_title: str
    ) -> None:
        first_row_xpath = self._row_xpath(first_node_title)
        second_row_xpath = self._row_xpath(second_node_title)
        self._ensure_item_visible(first_row_xpath)
        self._ensure_item_visible(second_row_xpath)
        first_row = self.test_case.find_element(first_row_xpath, by=By.XPATH)
        second_row = self.test_case.find_element(second_row_xpath, by=By.XPATH)
        second_row_follows_first = self.test_case.driver.execute_script(
            """
            return Boolean(
              arguments[0].compareDocumentPosition(arguments[1]) &
              Node.DOCUMENT_POSITION_FOLLOWING
            );
            """,
            first_row,
            second_row,
        )
        assert second_row_follows_first

    def assert_row_is_child_of(
        self, child_node_title: str, parent_node_title: str
    ) -> None:
        child_row_xpath = self._row_xpath(child_node_title)
        parent_row_xpath = self._row_xpath(parent_node_title)
        self._ensure_item_visible(child_row_xpath)
        self._ensure_item_visible(parent_row_xpath)
        child_row = self.test_case.find_element(child_row_xpath, by=By.XPATH)
        parent_row = self.test_case.find_element(parent_row_xpath, by=By.XPATH)
        structural_parent_row = child_row.find_element(
            By.XPATH,
            "ancestor::ul[@data-js-move-node-tree-children][1]/parent::li",
        )
        assert structural_parent_row == parent_row

    def assert_row_marked_as_moved(self, node_title: str) -> None:
        self._ensure_item_visible(self._row_xpath(node_title))
        self.test_case.assert_element(
            f"{self._row_xpath(node_title)}[@data-js-move-node-tree-moved]",
            by=By.XPATH,
        )

    def assert_row_has_no_move_targets(self, node_title: str) -> None:
        """
        Asserts the row cannot receive pointer placement input.
        """
        row_xpath = self._row_xpath(node_title)
        self._ensure_item_visible(row_xpath)
        self.test_case.assert_element_absent(
            f"{row_xpath}/*[@data-js-move-node-tree-target]",
            by=By.XPATH,
        )

    def assert_row_has_move_targets(self, node_title: str) -> None:
        """
        Asserts the row accepts pointer placement input.
        """
        row_xpath = self._row_xpath(node_title)
        self._ensure_item_visible(row_xpath)
        self.test_case.assert_element(
            f"{row_xpath}/*[@data-js-move-node-tree-target]",
            by=By.XPATH,
        )

    def assert_row_has_no_collapse_control(self, node_title: str) -> None:
        row_xpath = self._row_xpath(node_title)
        self._ensure_item_visible(row_xpath)
        self.test_case.assert_element_absent(
            f"{row_xpath}/*/*[@data-js-move-node-tree-collapse]",
            by=By.XPATH,
        )

    def assert_row_has_collapse_control(self, node_title: str) -> None:
        row_xpath = self._row_xpath(node_title)
        self._ensure_item_visible(row_xpath)
        self.test_case.assert_element(
            f"{row_xpath}/*/*[@data-js-move-node-tree-collapse]",
            by=By.XPATH,
        )

    def assert_document_has_no_collapse_control(
        self, document_title: str
    ) -> None:
        self.test_case.assert_element_absent(
            f"{self._document_xpath(document_title)}"
            "/*/*[@data-js-move-node-tree-collapse]",
            by=By.XPATH,
        )

    def assert_document_collapsed(self, document_title: str) -> None:
        self.test_case.assert_attribute(
            f"{self._document_xpath(document_title)}"
            "/*/*[@data-js-move-node-tree-collapse]",
            "aria-expanded",
            "false",
            by=By.XPATH,
        )

    def assert_document_expanded(self, document_title: str) -> None:
        self.test_case.assert_attribute(
            f"{self._document_xpath(document_title)}"
            "/*/*[@data-js-move-node-tree-collapse]",
            "aria-expanded",
            "true",
            by=By.XPATH,
        )

    def do_toggle_document(self, document_title: str) -> None:
        self.test_case.click(
            f"{self._document_xpath(document_title)}"
            "/*/*[@data-js-move-node-tree-collapse]",
            by=By.XPATH,
        )

    def do_click_before(self, node_title: str) -> None:
        self._do_pointer_placement(self._row_xpath(node_title), "before")

    def do_click_after(self, node_title: str) -> None:
        self._do_pointer_placement(self._row_xpath(node_title), "after")

    def do_click_inside_document(self, document_title: str) -> None:
        self._do_pointer_placement(
            self._document_xpath(document_title), "child"
        )

    def do_click_inside(self, node_title: str) -> None:
        self._do_pointer_placement(self._row_xpath(node_title), "child")

    def _assert_move_confirmation_visible(self) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='move-node-confirmation' and not(@hidden)]",
            by=By.XPATH,
        )

    def assert_move_confirmation_for_node(
        self,
        *,
        document_title: str,
        placement_label: str,
        node_title: str,
        node_type: str,
    ) -> None:
        self._assert_move_confirmation_visible()
        self.test_case.assert_text(
            "Move to",
            "//*[@data-testid='move-node-confirm-message-label']",
            by=By.XPATH,
        )
        self.test_case.assert_text(
            document_title,
            "//*[@data-testid='move-node-confirm-target-document-title']",
            by=By.XPATH,
        )
        self.test_case.assert_attribute(
            "//*[@data-testid='move-node-confirm-target-document-title']",
            "title",
            document_title,
            by=By.XPATH,
        )
        self.test_case.assert_text(
            placement_label,
            "//*[@data-testid='move-node-confirm-placement-label']",
            by=By.XPATH,
        )
        self.test_case.assert_text(
            node_title,
            "//*[@data-testid='move-node-confirm-target-node-title']",
            by=By.XPATH,
        )
        self.test_case.assert_attribute(
            "//*[@data-testid='move-node-confirm-target-node-type']/*",
            "text",
            node_type,
            by=By.XPATH,
        )
        target_node_info = self.test_case.driver.find_element(
            By.XPATH,
            "//*[@data-js-move-node-tree-confirm-target-node-info]",
        )
        assert target_node_info.get_attribute("style") == "display: contents;"

    def assert_move_confirmation_for_document(
        self, document_title: str
    ) -> None:
        self._assert_move_confirmation_visible()
        self.test_case.assert_text(
            "Move into",
            "//*[@data-testid='move-node-confirm-message-label']",
            by=By.XPATH,
        )
        self.test_case.assert_text(
            document_title,
            "//*[@data-testid='move-node-confirm-target-document-title']",
            by=By.XPATH,
        )
        self.test_case.assert_attribute(
            "//*[@data-testid='move-node-confirm-target-document-title']",
            "title",
            document_title,
            by=By.XPATH,
        )
        target_node_info = self.test_case.driver.find_element(
            By.XPATH,
            "//*[@data-js-move-node-tree-confirm-target-node-info]",
        )
        assert target_node_info.get_attribute("style") == "display: none;"

    def assert_move_confirmation_absent(self) -> None:
        self.test_case.assert_element_not_visible(
            "//*[@data-testid='move-node-confirmation']",
            by=By.XPATH,
        )

    def do_confirm_move(self) -> None:
        self.test_case.click(
            '//*[@data-testid="move-node-confirm"]',
            by=By.XPATH,
        )

    def do_confirm_move_with_enter(self) -> None:
        self.test_case.send_keys(
            '//*[@data-testid="move-node-confirm"]',
            Keys.ENTER,
            by=By.XPATH,
        )

    def do_cancel_move(self) -> None:
        self.test_case.click(
            '//*[@data-testid="move-node-cancel"]',
            by=By.XPATH,
        )

    def do_cancel_move_with_escape(self) -> None:
        self.test_case.send_keys(
            '//*[@data-testid="move-node-confirm"]',
            Keys.ESCAPE,
            by=By.XPATH,
        )

    def do_force_inside_non_composite(self, node_title: str) -> None:
        item_xpath = self._row_xpath(node_title)
        self._ensure_item_visible(item_xpath)
        target = self.test_case.find_element(
            f"{item_xpath}/*[@data-js-move-node-tree-target]",
            by=By.XPATH,
        )
        tree = self.test_case.find_element(
            '//*[@data-testid="move-node-tree"]',
            by=By.XPATH,
        )
        response_status = self.test_case.driver.execute_async_script(
            """
            const tree = arguments[0];
            const target = arguments[1];
            const done = arguments[arguments.length - 1];
            const requestParameters = new URLSearchParams({
              moved_node_mid: tree.getAttribute(
                'data-js-move-node-tree-moved-node-mid'
              ),
              target_mid: target.getAttribute(
                'data-js-move-node-tree-target-mid'
              ),
              whereto: 'child',
              context_document_mid: tree.getAttribute(
                'data-js-move-node-tree-context-document-mid'
              ),
            });
            const endpoint = tree.getAttribute(
              'data-js-move-node-tree-endpoint'
            );
            fetch(`${endpoint}?${requestParameters}`, {
              method: 'POST',
              headers: {Accept: 'text/vnd.turbo-stream.html'},
            })
              .then(async (response) => {
                Turbo.renderStreamMessage(await response.text());
                done(response.status);
              })
              .catch((error) => done(String(error)));
            """,
            tree,
            target,
        )
        assert response_status == 422

    def _do_pointer_placement(self, item_xpath: str, placement: str) -> None:
        self._ensure_item_visible(item_xpath)
        target = self.test_case.find_element(
            f"{item_xpath}/*[@data-js-move-node-tree-target]",
            by=By.XPATH,
        )
        target_item = self.test_case.find_element(item_xpath, by=By.XPATH)
        self.test_case.driver.execute_script(
            """
            const target = arguments[0];
            const placement = arguments[1];
            const bounds = target.getBoundingClientRect();
            let clientX = bounds.left + 2;
            let clientY = bounds.top + bounds.height * 0.25;
            if (placement === 'after') {
              clientY = bounds.top + bounds.height * 0.75;
            } else if (placement === 'child') {
              clientX = bounds.left + 40;
              clientY = bounds.top + bounds.height * 0.75;
            }
            target.dispatchEvent(new PointerEvent('pointermove', {
              bubbles: true,
              clientX,
              clientY,
            }));
            """,
            target,
            placement,
        )
        assert (
            target_item.get_attribute("data-js-move-node-tree-placement")
            == placement
        )
        self.test_case.driver.execute_script(
            """
            const target = arguments[0];
            const placement = arguments[1];
            const bounds = target.getBoundingClientRect();
            let clientX = bounds.left + 2;
            let clientY = bounds.top + bounds.height * 0.25;
            if (placement === 'after') {
              clientY = bounds.top + bounds.height * 0.75;
            } else if (placement === 'child') {
              clientX = bounds.left + 40;
              clientY = bounds.top + bounds.height * 0.75;
            }
            target.dispatchEvent(new MouseEvent('click', {
              bubbles: true,
              clientX,
              clientY,
            }));
            """,
            target,
            placement,
        )

    def _ensure_item_visible(self, item_xpath: str) -> None:
        item = self.test_case.driver.find_element(By.XPATH, item_xpath)
        ancestor_child_lists = item.find_elements(
            By.XPATH,
            "ancestor::ul[@data-js-move-node-tree-children]",
        )
        for child_list in reversed(ancestor_child_lists):
            if child_list.get_attribute("hidden") is None:
                continue
            collapse_button = child_list.find_element(
                By.XPATH,
                "parent::li/*/*[@data-js-move-node-tree-collapse]",
            )
            collapse_button.click()

    def assert_document_present(self, document_title: str) -> None:
        self.test_case.assert_element(
            self._document_xpath(document_title),
            by=By.XPATH,
        )

    def assert_document_incompatible(self, document_title: str) -> None:
        self.test_case.assert_element(
            f"{self._document_xpath(document_title)}"
            "[@data-js-move-node-tree-incompatible]",
            by=By.XPATH,
        )

    def assert_success(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="move-node-success-message"]',
            by=By.XPATH,
        )

    def assert_no_change(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="move-node-no-change-message"]',
            by=By.XPATH,
        )
        self.test_case.assert_text(
            "The node is already at the selected location.",
            '//*[@data-testid="move-node-no-change-message"]',
            by=By.XPATH,
        )

    def assert_error(self, expected_message: str) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="move-node-error-message"]',
            by=By.XPATH,
        )
        self.test_case.assert_text(
            expected_message,
            '//*[@data-testid="move-node-error-message"]',
            by=By.XPATH,
        )

    def do_go_to_new_location(self):
        self.test_case.click(
            '//*[@data-testid="move-node-go-to-new-location"]',
            by=By.XPATH,
        )
        self.assert_not_modal()
        from tests.end2end.helpers.screens.document.screen_document import (  # noqa: PLC0415
            Screen_Document,
        )

        return Screen_Document(self.test_case)

    def assert_go_to_new_location_href_contains(self, expected: str) -> None:
        link = self.test_case.find_element(
            '//*[@data-testid="move-node-go-to-new-location"]',
            by=By.XPATH,
        )
        assert expected in link.get_attribute("href")
