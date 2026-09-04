"""
@relation(SDOC-SRS-157, scope=file)
"""

import os

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from tests.end2end.e2e_case import E2ECase
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_tree_map_renderer(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            screen_url = test_server.get_host_and_port() + "/tree_map.html"
            self.open(screen_url)
            self.assert_element_absent(
                '[data-testid="tree-map-selector-option-renderer-debug"]'
            )

            self.open(screen_url + "?debug=1")

            self.assert_element(
                '//body[@data-viewtype="tree-map"]',
                by=By.XPATH,
            )
            self.assert_elements('[data-testid="tree-map-section"]', 1)
            node_selector = '[data-testid="tree-map-node"]'
            depth_two_node_selector = node_selector + '[data-depth="2"]'
            preview_control = '[data-testid="tree-map-preview-folder-contents"]'
            previous_sibling = '[data-testid="tree-map-previous-sibling"]'
            next_sibling = '[data-testid="tree-map-next-sibling"]'
            back_action = '[data-testid="tree-map-back"]'
            ancestor = '[data-testid="tree-map-ancestor"]'

            assert (
                self.driver.find_element(
                    By.CSS_SELECTOR, previous_sibling
                ).get_attribute("disabled")
                is not None
            )
            assert (
                self.driver.find_element(
                    By.CSS_SELECTOR, next_sibling
                ).get_attribute("disabled")
                is not None
            )
            self.assert_element_absent(depth_two_node_selector)
            self.click(
                '[data-testid="tree-map-preview-folder-contents-control"]'
            )
            self.assert_element(depth_two_node_selector)
            assert self.driver.find_element(
                By.CSS_SELECTOR, preview_control
            ).is_selected()

            # Each map restores its own display and navigation state.
            self.click('[data-testid="tree-map-selector-handler"]')
            self.click(
                '[data-testid="tree-map-selector-option-renderer-debug"]'
            )
            assert not self.driver.find_element(
                By.CSS_SELECTOR, preview_control
            ).is_selected()
            self.click(
                node_selector + '[data-node-kind="branch"][data-depth="1"]'
            )
            alternate_focused_label = self.get_text(
                '[data-testid="tree-map-focused-node"]'
            )

            self.click('[data-testid="tree-map-selector-handler"]')
            self.click('[data-testid="tree-map-selector-option-document-tree"]')
            assert self.driver.find_element(
                By.CSS_SELECTOR, preview_control
            ).is_selected()

            self.click('[data-testid="tree-map-selector-handler"]')
            self.click(
                '[data-testid="tree-map-selector-option-renderer-debug"]'
            )
            self.assert_text(
                alternate_focused_label,
                '[data-testid="tree-map-focused-node"]',
            )
            self.click('[data-testid="tree-map-selector-handler"]')
            self.click('[data-testid="tree-map-selector-option-document-tree"]')

            document_element = self.driver.find_element(
                By.CSS_SELECTOR,
                node_selector + '[data-node-title="Test document"]',
            )
            original_window = self.driver.current_window_handle
            window_handles = set(self.driver.window_handles)
            ActionChains(self.driver).move_to_element(
                document_element
            ).perform()
            document_action = document_element.find_element(
                By.CSS_SELECTOR,
                '[data-testid="tree-map-node-action"][data-action="document"]',
            )
            document_action.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 5).until(
                lambda driver: (
                    len(driver.window_handles) == len(window_handles) + 1
                )
            )
            document_window = (
                set(self.driver.window_handles) - window_handles
            ).pop()
            self.driver.switch_to.window(document_window)
            self.driver.close()
            self.driver.switch_to.window(original_window)

            requirement_element = self.driver.find_element(
                By.CSS_SELECTOR, depth_two_node_selector
            )
            requirement_actions = requirement_element.find_elements(
                By.CSS_SELECTOR,
                '[data-testid="tree-map-node-action"][data-action="preview"]',
            )
            assert len(requirement_actions) == 1

            ActionChains(self.driver).key_down(Keys.SHIFT).move_to_element(
                requirement_element
            ).perform()
            info_panel = '[data-testid="tree-map-info-panel"]'
            self.assert_element(info_panel + ":not([hidden])")
            self.assert_text("Requirement 1", info_panel)
            self.assert_text("REQ-1", info_panel)
            ActionChains(self.driver).key_up(Keys.SHIFT).perform()

            ActionChains(self.driver).key_down(Keys.SHIFT).click(
                requirement_element
            ).key_up(Keys.SHIFT).perform()
            self.assert_element("#modal [data-js-modal]")
            cancel_action = self.driver.find_element(
                By.CSS_SELECTOR, '[data-testid="form-cancel-action"]'
            )
            ActionChains(self.driver).key_down(Keys.SHIFT).click(
                cancel_action
            ).key_up(Keys.SHIFT).perform()
            self.assert_element("#modal [data-js-modal]")
            ActionChains(self.driver).key_down(Keys.SHIFT).key_down(
                Keys.ALT
            ).click(cancel_action).key_up(Keys.ALT).key_up(Keys.SHIFT).perform()
            self.assert_element("#modal [data-js-modal]")
            self.click('#modal [data-testid="form-cancel-action"]')

            self.click('[data-testid="tree-map-tips-button"]')
            self.assert_element('[data-testid="tree-map-tips-content"]')
            self.click('[data-testid="form-cancel-action"]')
            self.assert_element_absent('[data-testid="tree-map-tips-content"]')
            self.assert_no_js_errors()

            rendered_nodes_have_valid_rectangles = self.execute_script(
                """
                const nodes = Array.from(
                  document.querySelectorAll('[data-testid="tree-map-node"]'),
                );
                return nodes.length > 1 && nodes.every((node) => {
                  const rectangle = node.getBoundingClientRect();
                  return rectangle.width > 0 && rectangle.height > 0;
                });
                """
            )
            assert rendered_nodes_have_valid_rectangles

            back_element = self.driver.find_element(
                By.CSS_SELECTOR, back_action
            )
            assert not back_element.is_displayed()
            self.assert_element_absent(ancestor)
            self.click(
                node_selector + '[data-node-kind="branch"][data-depth="1"]'
            )
            self.assert_elements(ancestor, 1)
            assert back_element.is_displayed()
            self.click(back_action)
            assert not back_element.is_displayed()
            self.assert_element_absent(ancestor)

            # Ancestor navigation adds a visit instead of rewriting history.
            self.click(
                node_selector + '[data-node-kind="branch"][data-depth="1"]'
            )
            self.click(ancestor)
            self.assert_element_absent(ancestor)
            assert back_element.is_displayed()
            self.click(back_action)
            self.assert_elements(ancestor, 1)
            self.click(back_action)
            assert not back_element.is_displayed()

            # Sibling navigation follows the source tree order.
            self.click(node_selector + '[data-node-title="Test document"]')
            self.assert_text(
                "Test document",
                '[data-testid="tree-map-focused-node"]',
            )
            self.click(next_sibling)
            self.assert_text(
                "Second test document",
                '[data-testid="tree-map-focused-node"]',
            )
            self.click(back_action)
            assert not back_element.is_displayed()
            self.assert_element_absent(ancestor)
