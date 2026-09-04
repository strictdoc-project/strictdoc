"""
Unit tests for RequirementIntegrityAnalyzer: converting REQUIREMENT text
into a small Python representation and running the cross-requirement
integrity checks against it.

See developer/tasks/eurobot/20260827_requirement_integrity_checks/task.md
and strictdoc/core/analyzers/requirement_integrity_analyzer.py.
"""

from typing import List

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.core.analyzers.requirement_integrity_analyzer import (
    CANNOT_CONVERT_MESSAGE,
    RequirementIntegrityAnalyzer,
)
from strictdoc.core.document_iterator import SDocDocumentIterator
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


def _interface_issues(
    traceability_index: TraceabilityIndex, title: str
) -> List[str]:
    """
    INTERFACE_PARAMETER nodes have no UID in this grammar, so unlike
    _issues() above this looks the node up by TITLE, walking the tree the
    same way RequirementIntegrityAnalyzer itself does.
    """
    for document in traceability_index.document_tree.document_list:
        for node, _ in SDocDocumentIterator(document).all_content():
            if (
                isinstance(node, SDocNode)
                and node.node_type == "INTERFACE_PARAMETER"
                and node.reserved_title == title
            ):
                return (
                    traceability_index.validation_index.get_issues(
                        node, field="STATEMENT"
                    )
                    or []
                )
    raise AssertionError(f"No INTERFACE_PARAMETER with TITLE {title!r} found.")


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


INTERFACE_STARTED_CORD_BOOL = """
[INTERFACE_PARAMETER]
TITLE: started_cord
STATEMENT: Тип: bool
"""


def test_bool_interface_rejects_a_numeric_value():
    traceability_index = _build_traceability_index(
        INTERFACE_STARTED_CORD_BOOL
        + """
[REQUIREMENT]
UID: REQ-BOOL-NUM
STATEMENT: ЕСЛИ (started_cord==1) ТО робот должен установить started_cord в true
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-BOOL-NUM")
    assert len(issues) == 1
    assert "Несовпадение типа" in issues[0]
    assert "bool" in issues[0]


def test_bool_interface_rejects_a_quoted_string_value():
    traceability_index = _build_traceability_index(
        INTERFACE_STARTED_CORD_BOOL
        + """
[REQUIREMENT]
UID: REQ-BOOL-STR
STATEMENT: ЕСЛИ (started_cord=='yes') ТО робот должен установить started_cord в true
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-BOOL-STR")
    assert len(issues) == 1
    assert "Несовпадение типа" in issues[0]


def test_bool_interface_accepts_true_false_literals():
    traceability_index = _build_traceability_index(
        INTERFACE_STARTED_CORD_BOOL
        + """
[REQUIREMENT]
UID: REQ-BOOL-OK
STATEMENT: ЕСЛИ (started_cord==true) ТО робот должен установить started_cord в false
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _issues(traceability_index, "REQ-BOOL-OK") == []


def test_float_interface_accepts_an_int_literal():
    # 70 is a perfectly good float value — check_value_types must not flag
    # an int literal against a "Тип: float" interface the way it flags one
    # against "Тип: bool" or "Тип: str".
    traceability_index = _build_traceability_index(
        """
[INTERFACE_PARAMETER]
TITLE: robot_speed
STATEMENT: Тип: float

[REQUIREMENT]
UID: REQ-FLOAT-OK
STATEMENT: ЕСЛИ (robot_speed > 0) ТО робот должен установить robot_speed в 70
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _issues(traceability_index, "REQ-FLOAT-OK") == []


def test_value_type_check_is_skipped_for_a_value_that_is_not_a_literal():
    # motor_Speed compared to another variable name, not to a literal value
    # — there's no fixed type on the right-hand side for this check to
    # compare motor_Speed's declared type against.
    traceability_index = _build_traceability_index(
        INTERFACE_MOTOR_SPEED
        + """
[REQUIREMENT]
UID: REQ-VAR-VS-VAR
STATEMENT: ЕСЛИ (motor_Speed > target_Speed) ТО робот должен уменьшить motor_Speed на 5
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _issues(traceability_index, "REQ-VAR-VS-VAR") == []


def test_unknown_declared_type_names_the_type_in_the_message():
    traceability_index = _build_traceability_index(
        """
[INTERFACE_PARAMETER]
TITLE: motor_Speed
STATEMENT: Тип: velocity
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _interface_issues(traceability_index, "motor_Speed")
    assert len(issues) == 1
    assert "velocity" in issues[0]


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


def test_unconvertible_requirement_gets_single_actionable_issue():
    """
    The REQ-5/REQ-6 case: a prose requirement, alongside an unrelated
    well-formed one, to prove one node's conversion failure doesn't cascade
    into extra issues on itself or affect the other node.
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
    # A single issue, not one per whole-project check that also couldn't
    # run — and it names the expected shape so the text can be fixed.
    assert len(prose_issues) == 1
    assert prose_issues[0].startswith(CANNOT_CONVERT_MESSAGE)
    assert "ЕСЛИ" in prose_issues[0]

    assert _issues(traceability_index, "REQ-OK") == []


def test_unparsable_condition_names_the_condition_in_the_message():
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-BAD-CONDITION
STATEMENT: ЕСЛИ (motor_Speed ~~ 10) ТО робот должен уменьшить motor_Speed на 5
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-BAD-CONDITION")
    assert len(issues) == 1
    assert "условие" in issues[0]


def test_unparsable_action_names_the_action_in_the_message():
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-BAD-ACTION
STATEMENT: ЕСЛИ (motor_Speed > 10) ТО робот должен сделать что-то с motor_Speed
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-BAD-ACTION")
    assert len(issues) == 1
    assert "действие" in issues[0]


def test_interface_without_type_line_names_type_in_the_message():
    traceability_index = _build_traceability_index(
        """
[INTERFACE_PARAMETER]
TITLE: motor_Speed
STATEMENT: Current motor speed, no Type line.
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _interface_issues(traceability_index, "motor_Speed")
    assert len(issues) == 1
    assert "Type" in issues[0]


def test_russian_type_line_is_accepted_same_as_english():
    # Students write STATEMENT in Russian (see eurobot/Eurobot_Requirements.sdoc),
    # so "Тип: bool" must be recognized exactly like "Type: bool" is.
    traceability_index = _build_traceability_index(
        """
[INTERFACE_PARAMETER]
TITLE: started_cord
STATEMENT: >>>
Тип: bool
<<<
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _interface_issues(traceability_index, "started_cord") == []


def test_reset_prevents_duplicate_issues_on_a_second_pass():
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-PROSE
STATEMENT: >>>
1) Должен быть в наличии корд.
<<<
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)
    assert len(_issues(traceability_index, "REQ-PROSE")) == 1

    # Re-running without a reset() in between (the bug a naive "just call
    # the analyzer again after every save" fix would have) duplicates the
    # issue, because add_issue() only ever appends.
    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)
    assert len(_issues(traceability_index, "REQ-PROSE")) == 2

    # reset() before re-running (what write_document_to_file() actually
    # does) keeps it at one.
    traceability_index.validation_index.reset()
    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)
    assert len(_issues(traceability_index, "REQ-PROSE")) == 1


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
    assert not any("Противореч" in issue for issue in issues)


def test_prose_before_parens_is_allowed_for_both_condition_and_action():
    """
    A human-readable clause may sit between the keyword and the
    parenthesized, checkable expression — "ЕСЛИ <текст> (<условие>)" and
    "робот должен <текст> (<действие>)" — only what's in parens is parsed,
    the rest is documentation for the reader.
    """
    traceability_index = _build_traceability_index(
        INTERFACE_MOTOR_SPEED
        + """
[REQUIREMENT]
UID: REQ-PROSE-WRAPPED
STATEMENT: >>>
ЕСЛИ
скорость мотора превышает предел (
motor_Speed > 10)
ТО
робот должен снизить скорость (
уменьшить motor_Speed на 5)
<<<
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _issues(traceability_index, "REQ-PROSE-WRAPPED") == []


def test_dotted_attribute_path_is_a_valid_action_variable_via_raw_assignment():
    """
    The follow-up example from the bug report: a Python-style raw
    assignment ("variable = value") with a dotted attribute path as the
    variable name, instead of a verb phrase with a flat identifier.
    """
    traceability_index = _build_traceability_index(
        """
[INTERFACE_PARAMETER]
TITLE: started_cord
STATEMENT: >>>
Description: Whether the starting cord has been pulled.
Type: bool
<<<

[INTERFACE_PARAMETER]
TITLE: robot.velocity.x
STATEMENT: >>>
Description: Robot's forward velocity.
Type: float
<<<

[REQUIREMENT]
UID: REQ-DOTTED-ACTION
STATEMENT: >>>
ЕСЛИ
стартовый корд выдернут (
started_cord==true)
ТО
робот должен начать движение (
robot.velocity.x = 70)
<<<
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _issues(traceability_index, "REQ-DOTTED-ACTION") == []


def test_action_assignment_operator_variants_are_recognized():
    """
    "+=" / "-=" work as raw assignments too (not just "="), including with
    no spaces around the operator — VARIABLE_RE excludes "+"/"-" so the
    variable capture doesn't swallow the operator's first character.
    """
    # Different (non-overlapping) conditions, so this stays a pure parsing
    # check — same-condition opposing "+="/"-=" is exactly what
    # test_contradicting_requirements_fail_each_other_only already covers.
    traceability_index = _build_traceability_index(
        INTERFACE_MOTOR_SPEED
        + """
[REQUIREMENT]
UID: REQ-PLUS-EQUALS
STATEMENT: ЕСЛИ (motor_Speed < 5) ТО робот должен скорректировать скорость (motor_Speed += 3)

[REQUIREMENT]
UID: REQ-NO-SPACE
STATEMENT: ЕСЛИ (motor_Speed > 100) ТО робот должен скорректировать скорость (motor_Speed-=3)
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    assert _issues(traceability_index, "REQ-PLUS-EQUALS") == []
    assert _issues(traceability_index, "REQ-NO-SPACE") == []


def test_reserved_python_keyword_in_condition_variable_names_it_specifically():
    """
    "in.started_cord" builds valid-looking Python ("in.started_cord = None")
    that tree_sitter would reject with no clue why: "in" is a reserved
    keyword, not usable as a name, not even as the first segment of a
    dotted path. _invalid_identifier_reason() catches this before the
    generic syntax-check message would otherwise have to guess.
    """
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-KEYWORD-CONDITION
STATEMENT: ЕСЛИ (in.started_cord == true) ТО робот должен установить cmd.moving в true
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-KEYWORD-CONDITION")
    assert len(issues) == 1
    assert "«in»" in issues[0]
    assert "in.started_cord" in issues[0]


def test_reserved_python_keyword_in_action_variable_names_it_specifically():
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-KEYWORD-ACTION
STATEMENT: ЕСЛИ (started_cord == true) ТО робот должен установить class.moving в true
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-KEYWORD-ACTION")
    assert len(issues) == 1
    assert "«class»" in issues[0]


def test_soft_keyword_segment_is_not_flagged_as_invalid():
    """
    "match"/"case"/"type"/"_" are reserved only in their own statement's
    syntax; used as a plain name (all a dotted-path segment ever is here),
    they're valid Python, and tree_sitter agrees — _invalid_identifier_reason()
    must not report a false positive for these.
    """
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-SOFT-KEYWORD
STATEMENT: ЕСЛИ (started_cord == true) ТО робот должен установить cmd.type в true
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    issues = _issues(traceability_index, "REQ-SOFT-KEYWORD")
    assert not any(CANNOT_CONVERT_MESSAGE in issue for issue in issues)


def test_split_reports_missing_condition_separately_from_missing_action():
    traceability_index = _build_traceability_index(
        """
[REQUIREMENT]
UID: REQ-NO-CONDITION
STATEMENT: Должен быть в наличии корд (механика, платформа)

[REQUIREMENT]
UID: REQ-NO-ACTION
STATEMENT: ЕСЛИ (motor_Speed > 10) ТО что-то произойдёт
"""
    )

    RequirementIntegrityAnalyzer.analyze_document_tree(traceability_index)

    no_condition_issues = _issues(traceability_index, "REQ-NO-CONDITION")
    no_action_issues = _issues(traceability_index, "REQ-NO-ACTION")

    assert len(no_condition_issues) == 1
    assert "условие" in no_condition_issues[0]
    assert "действие" not in no_condition_issues[0]

    assert len(no_action_issues) == 1
    assert "действие" in no_action_issues[0]
    # REQ-NO-ACTION does have a recognizable condition — the message must
    # say so, not repeat the "condition not found" wording.
    assert "не найдено условие" not in no_action_issues[0]


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
