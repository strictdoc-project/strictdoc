"""
@relation(SDOC-SRS-157, scope=file)
"""

import os

from selenium.webdriver.common.by import By

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
            self.assert_element(".tree-map-html__node[data-depth='2']")
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

            first_section = ".tree-map-html__section:first-of-type"
            self.assert_element_absent(
                first_section + " .tree-map-html__ancestor"
            )
            self.click(first_section + " .tree-map-html__node[data-depth='1']")
            self.assert_elements(first_section + " .tree-map-html__ancestor", 1)
            back_button = self.find_element(
                first_section + " .tree-map-html__back"
            )
            assert back_button.is_enabled()
            self.click(first_section + " .tree-map-html__back")
            assert not back_button.is_enabled()
            self.assert_element_absent(
                first_section + " .tree-map-html__ancestor"
            )

            # Ancestor navigation adds a visit instead of rewriting history.
            self.click(first_section + " .tree-map-html__node[data-depth='1']")
            self.click(first_section + " .tree-map-html__ancestor")
            self.assert_element_absent(
                first_section + " .tree-map-html__ancestor"
            )
            assert back_button.is_enabled()
            self.click(first_section + " .tree-map-html__back")
            self.assert_elements(first_section + " .tree-map-html__ancestor", 1)
            self.click(first_section + " .tree-map-html__back")
            assert not back_button.is_enabled()
