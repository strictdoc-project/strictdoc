"""
@relation(SDOC-SRS-157, scope=file)
"""

import os

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_tree_map_html_renderer(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port() + "/tree_map_html.html")

            self.assert_element(
                '//body[@data-viewtype="tree-map-html"]',
                by=By.XPATH,
            )
            self.assert_elements(
                ".tree-map-html__section",
                3,
            )
            first_section = ".tree-map-html__section:first-of-type"
            self.assert_element(
                first_section
                + " .tree-map-html__sibling-navigation--project-root"
            )
            assert not self.driver.find_element(
                By.CSS_SELECTOR,
                first_section + " .tree-map-html__previous-sibling",
            ).is_displayed()
            assert not self.driver.find_element(
                By.CSS_SELECTOR,
                first_section + " .tree-map-html__next-sibling",
            ).is_displayed()
            self.assert_element_absent(".tree-map-html__node[data-depth='2']")
            self.click(first_section + " .tree-map-html__preview-control")
            self.assert_element(".tree-map-html__node[data-depth='2']")

            requirement_selector = (
                first_section + " .tree-map-html__node[data-depth='2']"
            )
            requirement_element = self.driver.find_element(
                By.CSS_SELECTOR, requirement_selector
            )
            requirement_actions = requirement_element.find_elements(
                By.CSS_SELECTOR, ".tree-map-html__node-action"
            )
            assert len(requirement_actions) == 2
            assert (
                requirement_element.find_element(
                    By.CSS_SELECTOR,
                    ".tree-map-html__node-action--go-to-document",
                )
                .get_attribute("href")
                .endswith("input.html#REQ-1")
            )

            ActionChains(self.driver).key_down(Keys.SHIFT).move_to_element(
                requirement_element
            ).perform()
            self.assert_element(".tree-map-html__info-panel:not([hidden])")
            self.assert_text("Requirement 1", ".tree-map-html__info-panel")
            self.assert_text("REQ-1", ".tree-map-html__info-panel")
            ActionChains(self.driver).key_up(Keys.SHIFT).perform()

            self.hover(requirement_selector)
            assert self.execute_script("return window.Turbo !== undefined")
            self.click(
                requirement_selector + " .tree-map-html__node-action--preview"
            )
            self.assert_element("#modal [data-js-modal]")
            self.click('#modal [data-testid="form-cancel-action"]')

            self.click('[data-testid="tree-map-html-tips-button"]')
            self.assert_element('[data-testid="tree-map-html-tips-content"]')
            self.assert_element(
                '[data-testid="tree-map-html-tips-content"] '
                ".tree-map-html-tips__key svg"
            )
            self.click('[data-testid="form-cancel-action"]')
            self.assert_element_absent(
                '[data-testid="tree-map-html-tips-content"]'
            )
            self.assert_no_js_errors()

            rectangles_are_valid = self.execute_script(
                """
                const nodes = Array.from(
                  document.querySelectorAll(
                    ".tree-map-html__node[data-depth='2']",
                  ),
                );
                return nodes.length >= 6 && nodes.every((node) => {
                  const rectangle = node.getBoundingClientRect();
                  return rectangle.width > 0 && rectangle.height > 0;
                });
                """
            )
            assert rectangles_are_valid

            rendered_children_respect_minimum_height = self.execute_script(
                """
                const children = Array.from(
                  document.querySelectorAll(
                    ".tree-map-html__node[data-depth]:not([data-depth='0'])",
                  ),
                );
                return children.every((node) =>
                  node.getBoundingClientRect().height >= 31.99
                );
                """
            )
            assert rendered_children_respect_minimum_height

            rendering_limits_are_respected = self.execute_script(
                """
                const sections = Array.from(
                  document.querySelectorAll(".tree-map-html__section"),
                );
                return sections.every((section) => {
                  const nodes = Array.from(
                    section.querySelectorAll(".tree-map-html__node"),
                  );
                  const depths = nodes.map((node) =>
                    Number(node.dataset.depth)
                  );
                  return nodes.length <= 500 && Math.max(...depths) <= 4;
                });
                """
            )
            assert rendering_limits_are_respected

            branches_are_complete_or_collapsed = self.execute_script(
                """
                const branches = Array.from(
                  document.querySelectorAll(
                    ".tree-map-html__node--branch",
                  ),
                );
                return branches.every((branch) => {
                  const childrenContainer = Array.from(branch.children).find(
                    (element) =>
                      element.classList.contains("tree-map-html__children"),
                  );
                  return childrenContainer === undefined ||
                    childrenContainer.children.length ===
                      Number(branch.dataset.childCount);
                });
                """
            )
            assert branches_are_complete_or_collapsed

            current_level_is_marked = self.execute_script(
                """
                const nodes = Array.from(
                  document.querySelectorAll(".tree-map-html__node"),
                );
                return nodes.every((node) =>
                  node.classList.contains(
                    "tree-map-html__node--current-level",
                  ) === (node.dataset.depth === "1")
                );
                """
            )
            assert current_level_is_marked

            focused_roots_are_not_interactive = self.execute_script(
                """
                const roots = Array.from(
                  document.querySelectorAll(
                    ".tree-map-html__canvas > .tree-map-html__node",
                  ),
                );
                return roots.every((root) =>
                  root.classList.contains(
                    "tree-map-html__node--focused-root",
                  ) &&
                  !root.classList.contains("tree-map-html__node--branch") &&
                  !root.hasAttribute("tabindex")
                );
                """
            )
            assert focused_roots_are_not_interactive

            back_icon = self.driver.find_element(
                By.CSS_SELECTOR,
                first_section + " .tree-map-html__back",
            )
            assert not back_icon.is_displayed()
            self.assert_element_absent(
                first_section + " .tree-map-html__ancestor"
            )
            self.click(first_section + " .tree-map-html__node[data-depth='1']")
            self.assert_elements(first_section + " .tree-map-html__ancestor", 1)
            assert back_icon.is_displayed()
            assert back_icon.tag_name == "svg"
            self.click(first_section + " .tree-map-html__back")
            assert not back_icon.is_displayed()
            self.assert_element_absent(
                first_section + " .tree-map-html__ancestor"
            )

            # Ancestor navigation adds a visit instead of rewriting history.
            self.click(first_section + " .tree-map-html__node[data-depth='1']")
            self.click(first_section + " .tree-map-html__ancestor")
            self.assert_element_absent(
                first_section + " .tree-map-html__ancestor"
            )
            assert back_icon.is_displayed()
            self.click(first_section + " .tree-map-html__back")
            self.assert_elements(first_section + " .tree-map-html__ancestor", 1)
            self.click(first_section + " .tree-map-html__back")
            assert not back_icon.is_displayed()

            # Sibling navigation follows the source tree order even when the
            # rectangle layout places nodes according to their weights.
            document_nodes = self.driver.find_elements(
                By.CSS_SELECTOR,
                first_section + " .tree-map-html__node[data-depth='1']",
            )
            first_document = next(
                node
                for node in document_nodes
                if node.text.startswith("Test document")
            )
            first_document.click()
            self.assert_text(
                "Test document",
                first_section + " .tree-map-html__sibling-current",
            )
            current_label = self.driver.find_element(
                By.CSS_SELECTOR,
                first_section
                + " .tree-map-html__sibling-current"
                + " .tree-map-html__label--root",
            )
            assert "Test document" in current_label.get_attribute("title")
            assert current_label.value_of_css_property("text-overflow") == (
                "ellipsis"
            )
            next_label = self.driver.find_element(
                By.CSS_SELECTOR,
                first_section + " .tree-map-html__sibling-label--next",
            )
            assert "tree-map-html__next-sibling" in (
                next_label.find_element(By.XPATH, "..").get_attribute("class")
            )
            assert "Second test document" in next_label.text
            assert "Second test document" in next_label.get_attribute("title")
            self.click(first_section + " .tree-map-html__next-sibling")
            self.assert_text(
                "Second test document",
                first_section + " .tree-map-html__sibling-current",
            )
            self.assert_text(
                "Test document",
                first_section + " .tree-map-html__sibling-label--previous",
            )
            self.click(first_section + " .tree-map-html__back")
            assert not back_icon.is_displayed()
            self.assert_element_absent(
                first_section + " .tree-map-html__ancestor"
            )
