from __future__ import annotations

import time

from playwright.sync_api import Locator


def type_text(locator: Locator, text: str, delay_ms: int = 45) -> None:
    """
    Fake typing effect for standalone HTML scenes (terminal/IDE look).

    Appends characters to the element's text content directly. This is a
    visual effect only: it does not simulate keyboard input and does not
    type into a real input, textarea, or code editor.
    """

    for char in text:
        locator.evaluate(
            "(el, char) => { el.textContent += char; }", char
        )
        time.sleep(delay_ms / 1000)
