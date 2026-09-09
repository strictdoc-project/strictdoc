from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.node.node import Node


class Section(Node):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase, node_order: int = 1) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_order, int)
        assert node_order > 0, node_order

        xpath = f"(//sdoc-node[@data-testid='node-section'])[{node_order}]"
        super().__init__(test_case, xpath)
        self.node_order: int = node_order

    def assert_is_section(self) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}",
            by=By.XPATH,
        )

    def assert_section_title(
        self,
        node_title: str,
        node_level: str = "",
    ) -> None:
        title = super().create_node_title_string(node_title, node_level)
        self.test_case.assert_element(
            f"{self.node_xpath}//sdoc-section-title[contains(., '{title}')]",
            by=By.XPATH,
        )

    def assert_section_text(self, text: str) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}//sdoc-section-text[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_anchor_links_number(self, links: int) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}//div[@data-testid='anchor_links_number' and contains(., '{links}')]",
            by=By.XPATH,
        )

    def do_copy_anchor_to_buffer(self) -> None:
        # The button only appears on a real CSS :hover, so the hover target
        # must already be on-screen: ActionChains moves the mouse to the
        # element's current on-page position, it does not scroll for us, and
        # a prior step in the same test may have scrolled it out of view.
        self.test_case.sdoc_do_scroll_to_element_by_xpath(self.node_xpath)
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f'{self.node_xpath}//*[@data-testid="section-anchor-button"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
