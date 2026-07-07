"""
Screencast scenario: creating a project from scratch with `strictdoc new`,
adding a new Requirement to an existing document through the web UI, then
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

REQUIREMENT_UID = "HLR-2"
REQUIREMENT_TITLE = "Hello world requirement"
REQUIREMENT_STATEMENT = "StrictDoc shall greet the world."


def run_strictdoc_new(project_dir: Path) -> str:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.getcwd()

    result = subprocess.run(
        [sys.executable, "-m", "strictdoc.cli.main", "new", str(project_dir)],
        capture_output=True,
        text=True,
        env=env,
        check=True,
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
        demo_text.evaluate(
            "(el, text) => { el.textContent += text; }", cli_output
        )
        pause(page, 2)

        hlr_path = project_dir / "docs" / "high_level_requirements.sdoc"
        original_sdoc_text = hlr_path.read_text(encoding="utf-8")

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
            project_tree.assert_contains_document("High-Level Requirements")
            pause(page)

            project_tree.do_click_on_the_document_with_title(
                "High-Level Requirements"
            )
            screen.assert_on_screen("document")
            pause(page)

            # Scene 3: adding a new Requirement below the existing one.
            hlr_1 = Requirement.with_node(pointer)
            node_menu = hlr_1.do_open_node_menu()
            form_edit_requirement = node_menu.do_node_add_requirement_below()

            form_edit_requirement.do_fill_in_field_uid(REQUIREMENT_UID)
            form_edit_requirement.do_fill_in_field_title(REQUIREMENT_TITLE)
            form_edit_requirement.do_fill_in_field_statement(
                REQUIREMENT_STATEMENT
            )
            pause(page)
            form_edit_requirement.do_form_submit()

            expect(
                page.locator("sdoc-node-title", has_text=REQUIREMENT_TITLE)
            ).to_be_visible()
            expect(
                page.locator('[data-field-label="statement"]').filter(
                    has_text=REQUIREMENT_STATEMENT
                )
            ).to_be_visible()
            pause(page, 2)

        final_sdoc_text = hlr_path.read_text(encoding="utf-8")
        assert final_sdoc_text.startswith(original_sdoc_text), (
            "Expected the new requirement to be appended after the "
            "document's existing content."
        )
        added_sdoc_text = final_sdoc_text[len(original_sdoc_text) :]
        assert REQUIREMENT_UID in added_sdoc_text

        # Scene 4: the real resulting .sdoc source, editor-style.
        page.goto(f"file://{EDITOR_HTML}")
        editor_scene.render_original(
            page, "docs/high_level_requirements.sdoc", original_sdoc_text
        )
        pause(page)
        editor_scene.reveal_added_lines(page, added_sdoc_text)
        pause(page, 2)
