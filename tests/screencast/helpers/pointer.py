from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

Target = Union[str, Locator]

_CSS = (Path(__file__).parent / "pointer.css").read_text(encoding="utf-8")

# Playwright doesn't render a real OS mouse cursor, so clicks are invisible
# in a recorded video unless we fake one. This injects a small dot that
# tracks real `mousemove` events (dispatched by page.mouse.move below), and
# a pulsing outline style (pointer.css) used to highlight a click's target
# just before clicking it. Registered via add_init_script so it re-applies
# on every navigation within this page (file:// scenes, the live server,
# ...). The CSS is spliced in as a JS string via json.dumps() (not an
# f-string, to avoid escaping every brace in the JS below): a JSON string
# is always a valid JS string literal, so pointer.css can contain quotes,
# backslashes, anything, without needing to keep that in sync here.
_INIT_SCRIPT = """
(() => {
  const style = document.createElement('style');
  style.textContent = __CSS__;

  const attach = () => {
    document.head.appendChild(style);
    const cursor = document.createElement('div');
    cursor.id = '__screencast_cursor';
    document.documentElement.appendChild(cursor);
    window.addEventListener('mousemove', (event) => {
      cursor.style.left = event.clientX + 'px';
      cursor.style.top = event.clientY + 'px';
    }, true);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attach);
  } else {
    attach();
  }
})();
""".replace("__CSS__", json.dumps(_CSS))


class Pointer:
    """
    Makes Playwright-driven interactions visible in recorded screencasts:
    a fake cursor travels to the target before every click, and the target
    is briefly highlighted so the viewer's eye doesn't miss it.
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        page.add_init_script(script=_INIT_SCRIPT)

    def _locator(self, target: Target) -> Locator:
        if isinstance(target, str):
            return self.page.locator(target).first
        return target

    def move_to(self, target: Target, *, pause_ms: int = 300) -> None:
        locator = self._locator(target)
        locator.scroll_into_view_if_needed()
        box = locator.bounding_box()
        assert box is not None, f"Not visible: {target}"
        self.page.mouse.move(
            box["x"] + box["width"] / 2,
            box["y"] + box["height"] / 2,
            steps=25,
        )
        self.page.wait_for_timeout(pause_ms)

    def click(self, target: Target, *, pause_ms: int = 400) -> None:
        locator = self._locator(target)
        self.move_to(locator)
        locator.evaluate("(el) => el.classList.add('__screencast_highlight')")
        self.page.wait_for_timeout(pause_ms)
        locator.click()
        try:
            # A click that navigates away (e.g. a tree/document link)
            # leaves nothing left to unhighlight on the new page.
            locator.evaluate(
                "(el) => el.classList.remove('__screencast_highlight')",
                timeout=1000,
            )
        except PlaywrightTimeoutError:
            pass

    def type_into(self, target: Target, text: str, *, delay_ms: int = 35) -> None:
        locator = self._locator(target)
        self.click(locator)
        # Some fields (e.g. UID) come pre-filled with a suggested value;
        # replace it rather than typing alongside it.
        locator.evaluate("(el) => { el.textContent = ''; }")
        locator.press_sequentially(text, delay=delay_ms)
