import re

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from seleniumbase import BaseCase


class MediaZoom:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    def assert_open(self) -> None:
        self.test_case.assert_element("//sdoc-media-zoom", by=By.XPATH)

    def assert_not_open(self) -> None:
        self.test_case.assert_element_not_present(
            "//sdoc-media-zoom", by=By.XPATH
        )

    def get_stage_element(self, tag_name: str) -> WebElement:
        return self.test_case.find_element(f"sdoc-media-zoom-stage {tag_name}")

    def get_stage_transform(self) -> str:
        return self.test_case.get_element(
            "sdoc-media-zoom-stage"
        ).value_of_css_property("transform")

    def get_stage_scale(self) -> float:
        """
        Reads the scale factor off the stage's "matrix(a, b, c, d, tx, ty)"
        transform. Only meaningful here because the stage is never
        rotated/skewed, so the leading coefficient "a" is the uniform
        scale.
        """
        transform = self.get_stage_transform()
        match = re.match(r"matrix\(([^,]+),", transform)
        assert match, f"Unexpected transform value: {transform!r}"
        return float(match.group(1))

    def get_stage_translate(self) -> tuple:
        """
        Reads (tx, ty) off the stage's "matrix(a, b, c, d, tx, ty)"
        transform.
        """
        transform = self.get_stage_transform()
        match = re.match(
            r"matrix\(([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,)]+)\)",
            transform,
        )
        assert match, f"Unexpected transform value: {transform!r}"
        return float(match.group(5)), float(match.group(6))

    def do_close_with_escape(self) -> None:
        """Uses Escape key. Includes assert_not_open."""
        self.test_case.get_element("html").send_keys(Keys.ESCAPE)
        self.assert_not_open()

    def do_close_with_backdrop_click(self) -> None:
        """
        Clicks a corner of the overlay, away from the centered stage.
        Includes assert_not_open.
        """
        self.test_case.click_with_offset("sdoc-media-zoom", 10, 10)
        self.assert_not_open()

    def do_toggle_fit_natural_with_double_click(self) -> None:
        self.test_case.double_click_with_offset(
            "sdoc-media-zoom", 0, 0, center=True
        )

    def dispatch_click(self, element: WebElement) -> None:
        """
        Fires a plain, script-dispatched "click" on the element, as
        opposed to WebElement.click()'s real, trusted click. A trusted
        click's own mousedown clears any existing selection as a browser
        default action before the click handler under test ever runs,
        which would erase a selection set up via the Range API in the
        same test right before calling this. A dispatched, untrusted
        click carries no such default action, so a selection set up just
        before this call is still there when the click listener runs.
        """
        self.test_case.execute_script(
            "arguments[0].dispatchEvent("
            "new MouseEvent('click', {bubbles: true, cancelable: true}));",
            element,
        )

    def do_arrow_pan(self, key: str, *, alt: bool = False) -> None:
        if alt:
            ActionChains(self.test_case.driver).key_down(Keys.ALT).send_keys(
                key
            ).key_up(Keys.ALT).perform()
        else:
            self.test_case.get_element("html").send_keys(key)

    def do_wheel_zoom_in(self) -> None:
        self.test_case.execute_script(
            """
            const overlay = document.querySelector('sdoc-media-zoom');
            const rect = overlay.getBoundingClientRect();
            overlay.dispatchEvent(new WheelEvent('wheel', {
                clientX: rect.width / 2,
                clientY: rect.height / 2,
                deltaY: -300,
                bubbles: true,
                cancelable: true,
            }));
            """
        )
