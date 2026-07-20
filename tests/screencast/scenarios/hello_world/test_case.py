"""
Screencast scenario: creating a project from scratch with `strictdoc new`,
adding a Rationale to an existing Requirement through the web UI, then
revealing the real resulting .sdoc source in an editor-style scene.

If this test fails, the "hello-world" screencast video is stale and must
be re-recorded (see tests/screencast/README.md).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from tests.end2end.server import SDocTestServer
from tests.screencast.fixture import RECORD_SERVER_PORT
from tests.screencast.helpers import editor_scene
from tests.screencast.helpers.node import Requirement
from tests.screencast.helpers.pacing import pause
from tests.screencast.helpers.pointer import Pointer
from tests.screencast.helpers.project_tree import ProjectTree
from tests.screencast.helpers.screen import Screen
from tests.screencast.scenarios.typing import type_text

TERMINAL_HTML = os.path.abspath(os.path.join(__file__, "../../../terminal.html"))
EDITOR_HTML = os.path.abspath(os.path.join(__file__, "../../../editor.html"))

RATIONALE_TEXT = (
    "A printed message is the simplest way to verify the application "
    "satisfies the parent requirement."
)


def run_strictdoc_new(project_dir: Path) -> str:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.getcwd()

    # Passed as a relative path, run from its own parent directory, so
    # the command's own printed output ("Location: ...", "cd ...") reads
    # short and relative — the same as a real user typing `strictdoc new
    # hello-world` — instead of leaking pytest's absolute tmp_path.
    # subprocess's cwd must already exist (unlike `strictdoc new` itself,
    # which happily creates its target); callers like manual_scenarios.py
    # may not have created it yet.
    project_dir.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, "-m", "strictdoc.cli.main", "new", project_dir.name],
        capture_output=True,
        text=True,
        env=env,
        check=True,
        cwd=project_dir.parent,
    )
    return result.stdout


def wait_for_stable_scroll_height(
    locator: Locator, *, poll_ms: int = 100, max_polls: int = 20
) -> None:
    """
    Waits until `locator.scrollHeight` stops changing between polls.
    Content that just appeared (e.g. a form that was just opened) can
    keep growing for a bit as it settles, so reading scrollHeight too
    early undershoots a "scroll to the bottom".
    """
    previous_height = None
    for _ in range(max_polls):
        current_height = locator.evaluate("(el) => el.scrollHeight")
        if current_height == previous_height:
            return
        previous_height = current_height
        locator.page.wait_for_timeout(poll_ms)


class Test:
    def test(self, page: Page, tmp_path: Path) -> None:
        pointer = Pointer(page)

        # Scene 1: the real `strictdoc new` output, in a terminal look.
        # Navigate here first, before actually running the command below:
        # video recording starts as soon as the browser context exists
        # (see scenarios/conftest.py), so running the (real, non-trivial)
        # subprocess before the first goto() would show a blank white
        # about:blank page at the very start of the video.
        page.goto(f"file://{TERMINAL_HTML}")
        demo_text = page.locator("#demoText")
        expect(demo_text).to_be_visible()

        type_text(demo_text, "$ strictdoc new hello-world\n")

        project_dir = tmp_path / "hello-world"
        cli_output = run_strictdoc_new(project_dir)

        # The output appears in full, scrolled to the top — read the
        # banner first...
        demo_text.evaluate(
            "(el, text) => { el.textContent += text; }", cli_output
        )
        pause(page, 1)

        # ...then a smooth (CSS scroll-behavior) scroll down to the end,
        # if it doesn't already fit, so the "Next steps" instructions are
        # readable too instead of being cut off below the fold.
        demo_text.evaluate("(el) => { el.scrollTop = el.scrollHeight; }")
        pause(page, 1)

        llr_path = project_dir / "docs" / "low_level_requirements.sdoc"
        original_sdoc_text = llr_path.read_text(encoding="utf-8")

        with SDocTestServer(
            input_path=str(project_dir),
            port=RECORD_SERVER_PORT,
        ) as server:
            base_url = server.get_host_and_port()

            # Scene 2: the web UI, browsing to the existing document.
            page.goto(f"{base_url}/")
            screen = Screen(page)
            screen.assert_on_screen("document-tree")

            project_tree = ProjectTree(pointer)
            project_tree.assert_contains_document("Low-Level Requirements")
            pause(page)

            project_tree.do_click_on_the_document_with_title(
                "Low-Level Requirements"
            )
            screen.assert_on_screen("document")
            pause(page)

            # Scene 3: follow the traceability link up to the parent
            # requirement (a real cross-document navigation to
            # High-Level Requirements), then back down via its child
            # relation — showing the link between the two documents is
            # real and works both ways.
            llr_1 = Requirement.with_node(pointer)
            llr_1.do_click_parent_relation()
            screen.assert_on_screen("document")
            pause(page)

            hlr_1 = Requirement.with_node(pointer)
            hlr_1.do_click_child_relation()
            screen.assert_on_screen("document")
            pause(page)

            # Scene 4: adding a Rationale to the existing Requirement.
            llr_1 = Requirement.with_node(pointer)
            form_edit_requirement = llr_1.do_open_form_edit_requirement()

            # Scroll the content area to the bottom before typing starts,
            # so the (last) Rationale field is settled in view — purely
            # cosmetic, .main already has scroll-behavior: smooth. The
            # form's height keeps growing for a bit right after it opens
            # (its fields animate/settle in), so scrollHeight must be
            # given time to stabilize first, or the scroll undershoots
            # against the still-growing content.
            wait_for_stable_scroll_height(page.locator(".main"))
            page.locator(".main").evaluate(
                "(el) => { el.scrollTop = el.scrollHeight; }"
            )
            pause(page)

            form_edit_requirement.do_fill_in_field_rationale(RATIONALE_TEXT)
            pause(page)
            form_edit_requirement.do_form_submit()

            expect(
                page.locator('[data-field-label="rationale"]').filter(
                    has_text=RATIONALE_TEXT
                )
            ).to_be_visible()
            pause(page, 1)

        final_sdoc_text = llr_path.read_text(encoding="utf-8")
        assert RATIONALE_TEXT not in original_sdoc_text
        assert RATIONALE_TEXT in final_sdoc_text

        # Scene 5: the real resulting .sdoc source, editor-style, with the
        # Rationale revealed exactly where it landed in the file.
        page.goto(f"file://{EDITOR_HTML}")
        editor_scene.render_original(
            page, "docs/low_level_requirements.sdoc", original_sdoc_text
        )
        pause(page)
        editor_scene.reveal_change(page, original_sdoc_text, final_sdoc_text)
        pause(page, 2)
