"""
Unit tests for RequirementIntegrityAnalyzer: converting REQUIREMENT text
into a small Python representation and running the two cross-requirement
integrity checks against it.

See developer/tasks/eurobot/20260827_requirement_integrity_checks/task.md
and strictdoc/core/analyzers/requirement_integrity_analyzer.py.
"""

from typing import List

from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.core.analyzers.requirement_integrity_analyzer import (
    CANNOT_CONVERT_MESSAGE,
    CONTRADICTION_CONVERSION_FAILED_MESSAGE,
    UNDEFINED_INTERFACE_CONVERSION_FAILED_MESSAGE,
    RequirementIntegrityAnalyzer,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from tests.unit.helpers.fake_document_meta import create_fake_document_meta

# A trimmed stand-in for eurobot/eurobot_grammar.sgra's REQUIREMENT and
# INTERFACE_PARAMETER elements, inlined so these tests have no dependency on
# the eurobot/ reference project's own grammar file.
TEST_GRAMMAR = """
[GRAMMAR]
ELEMENTS:
- TAG: INTERFACE_PARAMETER
  FIELDS:
  - TITLE: TITLE
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
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


def _build_traceability_index(document_content: str) -> TraceabilityIndex:
    document_text = (
        "[DOCUMENT]\nTITLE: Test Document\n\n"
        + TEST_GRAMMAR
        + "\n\n"
        + document_content.strip()
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
    return TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=ProjectConfig.default_config()
    )


def _issues(traceability_index: TraceabilityIndex, uid: str) -> List[str]:
    node = traceability_index.get_node_by_uid(uid)
    return (
        traceability_index.validation_index.get_issues(node, field="STATEMENT")
        or []
    )


INTERFACE_MOTOR_SPEED = """
[INTERFACE_PARAMETER]
TITLE: motor_Speed
STATEMENT: >>>
Description: Current motor speed.
Type: int
<<<
"""


def test_well_formed_requirement_with_declared_interface_passes_everything():
    traceability_index = _build_traceability_index(
        INTERFACE_MOTOR_SPEED
        + """
[REQUIREMENT]
UID: REQ-1
STATEMENT: ЕСЛИ (motor_Speed > 10) ТО робот должен уменьшить motor_Speed на 5
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _issues(traceability_index, "REQ-1") == []


def test_undefined_interface_fails_only_that_check():
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-2
STATEMENT: ЕСЛИ (battery_Level < 20) ТО робот должен установить battery_Level в 100
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-2")
    assert len(issues) == 1
    assert "battery_Level" in issues[0]
    assert CANNOT_CONVERT_MESSAGE not in issues[0]


def test_contradicting_requirements_fail_each_other_only():
    traceability_index = _build_traceability_index(
        INTERFACE_MOTOR_SPEED
        + """
[REQUIREMENT]
UID: REQ-INCREASE
STATEMENT: ЕСЛИ (motor_Speed > 10) ТО робот должен увеличить motor_Speed на 5

[REQUIREMENT]
UID: REQ-DECREASE
STATEMENT: ЕСЛИ (motor_Speed > 10) ТО робот должен уменьшить motor_Speed на 5
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    increase_issues = _issues(traceability_index, "REQ-INCREASE")
    decrease_issues = _issues(traceability_index, "REQ-DECREASE")
    assert len(increase_issues) == 1
    assert "REQ-DECREASE" in increase_issues[0]
    assert len(decrease_issues) == 1
    assert "REQ-INCREASE" in decrease_issues[0]


def test_unconvertible_requirement_fails_both_checks_without_affecting_others():
    """
    The REQ-5 case: a prose requirement, alongside an unrelated well-formed
    one, to prove one node's conversion failure doesn't cascade.
    """
    traceability_index = _build_traceability_index(
        INTERFACE_MOTOR_SPEED
        + """
[REQUIREMENT]
UID: REQ-OK
STATEMENT: ЕСЛИ (motor_Speed > 10) ТО робот должен уменьшить motor_Speed на 5

[REQUIREMENT]
UID: REQ-PROSE
STATEMENT: >>>
1) Должен быть в наличии корд.
2) Робот должен считывать, есть ли в нём корд.
<<<
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    prose_issues = _issues(traceability_index, "REQ-PROSE")
    assert len(prose_issues) == 3
    assert CANNOT_CONVERT_MESSAGE in prose_issues
    assert UNDEFINED_INTERFACE_CONVERSION_FAILED_MESSAGE in prose_issues
    assert CONTRADICTION_CONVERSION_FAILED_MESSAGE in prose_issues

    assert _issues(traceability_index, "REQ-OK") == []


def test_compound_or_condition_checks_every_clauses_variable():
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-COMPOUND
STATEMENT: ЕСЛИ (motor_Speed > 5 ИЛИ battery_Level < 2) ТО робот должен установить motor_Speed в 1
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-COMPOUND")
    # Conversion succeeds (the compound shape itself is supported), so the
    # "could not convert" warning must be absent, and every clause's
    # variable is still checked for an interface declaration: motor_Speed
    # (undeclared here) and battery_Level (undeclared here) each get their
    # own warning. The contradiction check is out of scope for a compound
    # condition, so it must not add a warning of its own either way.
    assert CANNOT_CONVERT_MESSAGE not in issues
    assert any("motor_Speed" in issue for issue in issues)
    assert any("battery_Level" in issue for issue in issues)
    assert not any("Contradicting" in issue for issue in issues)


def test_and_combinator_is_also_recognized():
    traceability_index = _build_traceability_index(
        INTERFACE_MOTOR_SPEED
        + """
[REQUIREMENT]
UID: REQ-AND
STATEMENT: КОГДА (motor_Speed > 5 И battery_Level < 2) ТОГДА робот должен уменьшить motor_Speed на 1
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-AND")
    assert CANNOT_CONVERT_MESSAGE not in issues
    assert any("battery_Level" in issue for issue in issues)
