"""
@relation(SDOC-SRS-36, scope=file)
"""

import io
import pickle
from pathlib import Path
from typing import Any, Set, Tuple

from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.export.html.html_templates import NormalHTMLTemplates
from strictdoc.features.export.export_action import ExportAction
from strictdoc.features.source_file_view.view_data import (
    SourceFileViewDataCollector,
)
from strictdoc.features.source_file_view.view_object import (
    SourceFileViewObject,
)
from strictdoc.helpers.parallelizer import NullParallelizer

INPUT_SDOC = """\
[DOCUMENT]
TITLE: Requirements

[REQUIREMENT]
UID: REQ-1
TITLE: Parent requirement
STATEMENT: >>>
The parent links to [LINK: REQ-2].

[ANCHOR: ANCHOR-1]
<<<
RATIONALE: The parent has a rationale.
COMMENT: The parent has a comment.

[REQUIREMENT]
UID: REQ-2
TITLE: Child requirement
STATEMENT: The child links to [LINK: ANCHOR-1].
RELATIONS:
- TYPE: Parent
  VALUE: REQ-1

[REQUIREMENT]
UID: REQ-3
TITLE: Requirement without statement and rationale
"""

INPUT_SOURCE = """\
# @relation(REQ-1, scope=range_start)
CONTENT 1
# @relation(REQ-1, scope=range_end)
# @relation(REQ-2, scope=line)
CONTENT 2
# @relation(REQ-3, scope=line)
CONTENT 3
"""

# A view object must not hold document nodes or the traceability index.
# Otherwise, pickling it for a worker process would copy large parts of the
# project.
FORBIDDEN_CLASSES = {
    ("strictdoc.backend.sdoc.models.node", "SDocNode"),
    ("strictdoc.backend.sdoc.models.node", "SDocNodeField"),
    ("strictdoc.backend.sdoc.models.document", "SDocDocument"),
    ("strictdoc.core.traceability_index", "TraceabilityIndex"),
}


class ClassRecordingUnpickler(pickle.Unpickler):
    def __init__(self, data: bytes) -> None:
        super().__init__(io.BytesIO(data))
        self.classes: Set[Tuple[str, str]] = set()

    def find_class(self, module: str, name: str) -> Any:
        self.classes.add((module, name))
        return super().find_class(module, name)


def create_view_object(
    tmp_path: Path,
) -> Tuple[SourceFileViewObject, NormalHTMLTemplates]:
    input_root = tmp_path / "input"
    input_root.mkdir()
    (input_root / "input.sdoc").write_text(INPUT_SDOC, encoding="utf8")
    (input_root / "file.py").write_text(INPUT_SOURCE, encoding="utf8")

    output_root = tmp_path / "output"
    project_config = ProjectConfig.default_config()
    project_config.project_features.append(
        ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
    )
    project_config.input_paths = [str(input_root)]
    project_config.source_root_path = str(input_root)
    project_config.output_dir = str(output_root)
    project_config.export_output_html_root = str(output_root / "html")

    traceability_index = ExportAction(
        project_config, NullParallelizer()
    ).traceability_index
    source_files = [
        source_file_
        for source_file_ in traceability_index.document_tree.source_tree.source_files
        if source_file_.is_referenced
    ]
    assert len(source_files) == 1
    source_file: SourceFile = source_files[0]

    html_templates = NormalHTMLTemplates()
    data_collector = SourceFileViewDataCollector(
        traceability_index=traceability_index,
        project_config=project_config,
        html_templates=html_templates,
    )
    view_object = SourceFileViewObject.create(
        source_file=source_file, data_collector=data_collector
    )
    return view_object, html_templates


def test_01_view_object_holds_no_nodes_and_no_traceability_index(
    tmp_path: Path,
) -> None:
    view_object, _ = create_view_object(tmp_path)

    unpickler = ClassRecordingUnpickler(pickle.dumps(view_object))
    unpickler.load()

    assert unpickler.classes & FORBIDDEN_CLASSES == set()
    assert sorted(view_object.nodes.keys()) == ["REQ-1", "REQ-2", "REQ-3"]


def test_04_node_without_statement_and_rationale(tmp_path: Path) -> None:
    """
    The templates read the statement and the rationale of a node only if the
    node has them. SDocNode raises an exception for a missing field, so the
    view object must not read these fields of a node that lacks them.
    """
    view_object, html_templates = create_view_object(tmp_path)

    node_with_fields = view_object.nodes["REQ-1"]
    assert node_with_fields.has_reserved_statement()
    assert node_with_fields.content_field is not None
    assert node_with_fields.rationale_field is not None
    assert len(node_with_fields.get_comment_fields()) == 1

    node_without_fields = view_object.nodes["REQ-3"]
    assert not node_without_fields.has_reserved_statement()
    assert node_without_fields.content_field is None
    assert node_without_fields.rationale_field is None

    html = view_object.render_screen(html_templates.jinja_environment())
    assert "Requirement without statement and rationale" in html
    assert "The parent has a rationale." in html


def test_02_pickled_view_object_renders_the_same_html(
    tmp_path: Path,
) -> None:
    view_object, html_templates = create_view_object(tmp_path)
    jinja_environment = html_templates.jinja_environment()

    html = view_object.render_screen(jinja_environment)
    unpickled_view_object = pickle.loads(pickle.dumps(view_object))
    unpickled_html = unpickled_view_object.render_screen(jinja_environment)

    assert unpickled_html == html
    # The page shows the nodes, the relation, and the incoming link to the
    # anchor, which come from the data of the view object.
    assert 'data-reqid="REQ-1"' in html
    assert 'class="requirement__link-parent"' in html
    assert "Incoming link" in html


def test_03_render_screen_resets_the_render_state(tmp_path: Path) -> None:
    view_object, html_templates = create_view_object(tmp_path)

    view_object.render_screen(html_templates.jinja_environment())

    assert view_object.source_lines == []
    assert view_object.range_begin_lines == []
    # Rendering twice gives the same HTML.
    assert view_object.render_screen(
        html_templates.jinja_environment()
    ) == view_object.render_screen(html_templates.jinja_environment())
