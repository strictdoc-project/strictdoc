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

from playwright.sync_api import Page, expect

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


class Test:
    def test(self, page: Page, tmp_path: Path) -> None:
        pointer = Pointer(page)

        project_dir = tmp_path / "hello-world"
        cli_output = run_strictdoc_new(project_dir)

        # Scene 1: the real `strictdoc new` output, in a terminal look.
        page.goto(f"file://{TERMINAL_HTML}")
        demo_text = page.locator("#demoText")
        expect(demo_text).to_be_visible()

        type_text(demo_text, "$ strictdoc new hello-world\n")

        # The output appears in full, scrolled to the top — read the
        # banner first...
        demo_text.evaluate(
            "(el, text) => { el.textContent += text; }", cli_output
        )
        pause(page, 2)

        # ...then a smooth (CSS scroll-behavior) scroll down to the end,
        # if it doesn't already fit, so the "Next steps" instructions are
        # readable too instead of being cut off below the fold.
        demo_text.evaluate("(el) => { el.scrollTop = el.scrollHeight; }")
        pause(page, 2)

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

            # Scene 3: adding a Rationale to the existing Requirement.
            llr_1 = Requirement.with_node(pointer)
            form_edit_requirement = llr_1.do_open_form_edit_requirement()

            form_edit_requirement.do_fill_in_field_rationale(RATIONALE_TEXT)
            pause(page)
            form_edit_requirement.do_form_submit()

            expect(
                page.locator('[data-field-label="rationale"]').filter(
                    has_text=RATIONALE_TEXT
                )
            ).to_be_visible()
            pause(page, 2)

        final_sdoc_text = llr_path.read_text(encoding="utf-8")
        assert RATIONALE_TEXT not in original_sdoc_text
        assert RATIONALE_TEXT in final_sdoc_text

        # Scene 4: the real resulting .sdoc source, editor-style, with the
        # Rationale revealed exactly where it landed in the file.
        page.goto(f"file://{EDITOR_HTML}")
        editor_scene.render_original(
            page, "docs/low_level_requirements.sdoc", original_sdoc_text
        )
        pause(page)
        editor_scene.reveal_change(page, original_sdoc_text, final_sdoc_text)
        pause(page, 2)
