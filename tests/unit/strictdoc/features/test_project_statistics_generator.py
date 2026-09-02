from datetime import datetime
from typing import Tuple

from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.core.analyzers.requirement_integrity_analyzer import (
    RequirementIntegrityAnalyzer,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.project_statistics.generator import (
    ProgressStatisticsGenerator,
)
from tests.unit.helpers.fake_document_meta import create_fake_document_meta

# A trimmed grammar carrying just what RequirementIntegrityAnalyzer and
# ProgressStatisticsGenerator both read, mirroring
# tests/unit/strictdoc/core/analyzers/test_requirement_integrity_analyzer.py.
TEST_GRAMMAR = """
[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
""".strip()

# A well-formed statement RequirementIntegrityAnalyzer can convert.
CONVERTIBLE_STATEMENT = "ЕСЛИ (x > 1) ТО робот должен установить x в 1"
# Ordinary prose: doesn't match the IF/THEN pseudo-code shape, so it fails
# conversion as-is.
UNCONVERTIBLE_STATEMENT = "The robot shall behave reasonably."


def _build_traceability_index(
    *, convertible_count: int, unconvertible_count: int
) -> Tuple[TraceabilityIndex, ProjectConfig]:
    requirement_blocks = []
    index = 0
    for _ in range(convertible_count):
        requirement_blocks.append(
            f"[REQUIREMENT]\nUID: REQ-{index:03d}\n"
            f"STATEMENT: {CONVERTIBLE_STATEMENT}\n"
        )
        index += 1
    for _ in range(unconvertible_count):
        requirement_blocks.append(
            f"[REQUIREMENT]\nUID: REQ-{index:03d}\n"
            f"STATEMENT: {UNCONVERTIBLE_STATEMENT}\n"
        )
        index += 1

    document_text = (
        "[DOCUMENT]\nTITLE: Test Document\n\n"
        + TEST_GRAMMAR
        + "\n\n"
        + "\n".join(requirement_blocks)
        + "\n"
    )
    document = SDReader().read(document_text)
    document.meta = create_fake_document_meta()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    project_config = ProjectConfig.default_config()
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=project_config
    )
    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)
    return traceability_index, project_config


def _render_statistics(
    traceability_index: TraceabilityIndex, project_config: ProjectConfig
) -> str:
    link_renderer = LinkRenderer(root_path="", static_path="_static")
    html_templates = HTMLTemplates.create(
        project_config=project_config,
        enable_caching=False,
        strictdoc_last_update=datetime.today(),
    )
    return str(
        ProgressStatisticsGenerator.export(
            project_config,
            traceability_index,
            link_renderer,
            html_templates=html_templates,
        )
    )


COUNT_TESTID = (
    'data-testid="table-row-value-requirements-failed-conversion-check">'
)


def test_counts_only_the_unconvertible_requirement() -> None:
    traceability_index, project_config = _build_traceability_index(
        convertible_count=1, unconvertible_count=1
    )

    html = _render_statistics(traceability_index, project_config)

    assert f"{COUNT_TESTID}1<" in html


def test_zero_when_every_requirement_converts() -> None:
    traceability_index, project_config = _build_traceability_index(
        convertible_count=2, unconvertible_count=0
    )

    html = _render_statistics(traceability_index, project_config)

    assert f"{COUNT_TESTID}0<" in html
