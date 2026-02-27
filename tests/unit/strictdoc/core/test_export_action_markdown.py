import os
import tempfile
from pathlib import Path

from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.parallelizer import NullParallelizer


def _create_project_config_for_markdown_export(
    input_root: str, output_root: str
) -> ProjectConfig:
    project_config = ProjectConfig.default_config()
    project_config.input_paths = [input_root]
    project_config.output_dir = output_root
    project_config.export_output_html_root = os.path.join(output_root, "html")
    project_config.export_formats = ["markdown"]
    return project_config


def test_001_markdown_export_writes_markdown_for_all_supported_inputs():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_root = Path(temp_dir) / "input"
        input_nested = input_root / "nested"
        input_root.mkdir(parents=True)
        input_nested.mkdir(parents=True)

        markdown_a = (
            "# Document A\n"
            "\n"
            "## Requirement A\n"
            "\n"
            "**UID**: REQ-A\n"
            "\n"
            "**Statement**: System shall do A.\n"
        )
        markdown_b = (
            "# Document B\n"
            "\n"
            "## Requirement B\n"
            "\n"
            "**UID**: REQ-B\n"
            "\n"
            "**Statement**: System shall do B.\n"
        )
        sdoc_c = (
            "[DOCUMENT]\n"
            "TITLE: Document C\n"
            "\n"
            "[REQUIREMENT]\n"
            "UID: REQ-C\n"
            "TITLE: Requirement C\n"
            "STATEMENT: System shall do C.\n"
        )

        (input_root / "a.md").write_text(markdown_a, encoding="utf8")
        (input_nested / "b.markdown").write_text(markdown_b, encoding="utf8")
        (input_root / "c.sdoc").write_text(sdoc_c, encoding="utf8")

        output_root = Path(temp_dir) / "output"
        project_config = _create_project_config_for_markdown_export(
            input_root=str(input_root), output_root=str(output_root)
        )

        export_action = ExportAction(project_config, NullParallelizer())
        export_action.export()

        exported_a = output_root / "markdown" / "a.md"
        exported_b = output_root / "markdown" / "nested" / "b.md"
        exported_c = output_root / "markdown" / "c.md"

        assert exported_a.exists()
        assert exported_b.exists()
        assert exported_c.exists()

        assert exported_a.read_text(encoding="utf8") == markdown_a
        assert exported_b.read_text(encoding="utf8") == markdown_b

        exported_c_content = exported_c.read_text(encoding="utf8")
        assert exported_c_content.startswith("# Document C\n")
        assert "## Requirement C" in exported_c_content
        assert "**UID**: REQ-C" in exported_c_content


def test_002_markdown_export_uses_platform_line_endings():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_root = Path(temp_dir) / "input"
        input_root.mkdir(parents=True)

        markdown_crlf = (
            "# Document CRLF\r\n"
            "\r\n"
            "## Requirement CRLF\r\n"
            "\r\n"
            "**UID**: REQ-CRLF\r\n"
            "\r\n"
            "**Statement**: Line 1\r\n"
        )
        with open(
            input_root / "crlf.md",
            "w",
            encoding="utf8",
            newline="",
        ) as input_file:
            input_file.write(markdown_crlf)

        output_root = Path(temp_dir) / "output"
        project_config = _create_project_config_for_markdown_export(
            input_root=str(input_root), output_root=str(output_root)
        )

        export_action = ExportAction(project_config, NullParallelizer())
        export_action.export()

        exported_file = output_root / "markdown" / "crlf.md"
        assert exported_file.exists()

        exported_bytes = exported_file.read_bytes()
        assert exported_bytes.decode("utf8") == (
            "# Document CRLF"
            f"{os.linesep}"
            f"{os.linesep}"
            "## Requirement CRLF"
            f"{os.linesep}"
            f"{os.linesep}"
            "**UID**: REQ-CRLF"
            f"{os.linesep}"
            f"{os.linesep}"
            "**Statement**: Line 1"
            f"{os.linesep}"
        )
