"""
Cross-requirement integrity checks.

Converts every REQUIREMENT node's condition/action text into a small Python
representation (parsed and confirmed with tree_sitter_python, the same
construction strictdoc/backend/sdoc_source_code/reader_python.py already
uses), then runs two whole-project checks against that representation:

1. check_undefined_interfaces: a requirement's condition or action names a
   variable no INTERFACE_PARAMETER node declares.
2. check_contradicting_requirements: two requirements place conditions on
   the same variable that can hold at the same time, but prescribe actions
   on that variable that disagree.

Both are warnings, reported through the existing
strictdoc/core/validation_index.py::ValidationIndex.add_issue, never a
build-stopping error.

A REQUIREMENT node whose text does not match the expected pseudo-code shape
closely enough to convert gets a "could not convert" warning, and both
checks above are reported FAILED for it too (each with its own explanatory
issue) rather than silently skipped: a check that cannot verify a
requirement is a failed check, not an inapplicable one. This does not
cascade — another node's conversion failure never fails this node's checks.

Requirements in this fork are written in Russian, so the pseudo-code shape
is matched in Russian as well as English:

    ЕСЛИ (condition) ТО робот должен action
    КОГДА (condition) ТОГДА робот должен action
    IF (condition) THEN system shall action

A condition may combine several clauses with ИЛИ/OR or И/AND.
check_undefined_interfaces checks every clause's variable regardless of
combinator; check_contradicting_requirements only compares single-clause
conditions (a compound condition's pairwise overlap is out of this
heuristic's scope, same as its own admitted operator-overlap gap).

See developer/tasks/eurobot/20260827_requirement_integrity_checks/task.md.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern, Tuple

import tree_sitter_python
from tree_sitter import Language, Parser

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.validation_index import ValidationIndex

Clause = Tuple[str, str, str]  # (variable, operator, value)

CANNOT_CONVERT_MESSAGE = (
    "Could not convert this node's text into a checkable form."
)
UNDEFINED_INTERFACE_CONVERSION_FAILED_MESSAGE = (
    "Undefined-interface check failed: requirement text could not be "
    "converted, so its interface references could not be verified."
)
CONTRADICTION_CONVERSION_FAILED_MESSAGE = (
    "Contradiction check failed: requirement text could not be converted, "
    "so it could not be compared against other requirements."
)

# (condition keyword, then keyword, action-intro keyword), tried in order.
# All real eurobot/ requirements are written in Russian; English is kept as
# a fallback for a requirement that is ever written in English.
KEYWORD_PAIRS: List[Tuple[str, str, str]] = [
    ("ЕСЛИ", "ТО", "робот должен"),
    ("КОГДА", "ТОГДА", "робот должен"),
    ("IF", "THEN", "system shall"),
]

OR_SPLIT_RE = re.compile(r"\s*\b(?:ИЛИ|OR)\b\s*", re.IGNORECASE)
AND_SPLIT_RE = re.compile(r"\s*\b(?:И|AND)\b\s*", re.IGNORECASE)

CONDITION_CLAUSE_RE = re.compile(
    r"^(?P<variable>[^\s()=!<>]+)\s*"
    r"(?P<operator>==|!=|<=|>=|<|>)\s*"
    r"(?P<value>\S+)$"
)

TYPE_LINE_RE = re.compile(r"(?im)^\s*Type\s*:\s*\S")

# action phrase -> python operator. Matched against the action text, which
# reads "<phrase> <variable> ... <value>".
ACTION_PHRASE_TABLE: List[Tuple[Pattern[str], str]] = [
    (
        re.compile(
            r"^set\s+(?P<variable>\w+)\s+to\s+(?P<value>\S+)$", re.IGNORECASE
        ),
        "=",
    ),
    (
        re.compile(
            r"^increase\s+(?P<variable>\w+)\s+by\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "+=",
    ),
    (
        re.compile(
            r"^decrease\s+(?P<variable>\w+)\s+by\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "-=",
    ),
    (
        re.compile(
            r"^установить\s+(?P<variable>\w+)\s+в\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "=",
    ),
    (
        re.compile(
            r"^увеличить\s+(?P<variable>\w+)\s+на\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "+=",
    ),
    (
        re.compile(
            r"^уменьшить\s+(?P<variable>\w+)\s+на\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "-=",
    ),
]

OPPOSING_ACTION_OPERATORS = {"+=": "-=", "-=": "+="}

_PY_LANGUAGE = Language(tree_sitter_python.language())


@dataclass
class InterfaceDecl:
    name: str
    node: SDocNode


@dataclass
class RequirementEffect:
    uid: str
    node: SDocNode
    condition_clauses: List[Clause]
    condition_combinator: Optional[str]  # "and" / "or" / None (single clause)
    action: Clause

    @property
    def is_compound(self) -> bool:
        return self.condition_combinator is not None

    def variables(self) -> List[str]:
        names = [clause[0] for clause in self.condition_clauses]
        names.append(self.action[0])
        return names


def _extract_interface(node: SDocNode) -> Optional[InterfaceDecl]:
    title = node.reserved_title
    statement = node.reserved_statement or ""
    if title is None or not title.strip():
        return None
    if TYPE_LINE_RE.search(statement) is None:
        return None
    return InterfaceDecl(name=title.strip(), node=node)


def _split_statement(statement: str) -> Optional[Tuple[str, str]]:
    for condition_kw, then_kw, action_kw in KEYWORD_PAIRS:
        pattern = re.compile(
            rf"{condition_kw}\s*\((?P<condition>.+?)\)\s*{then_kw}\s+"
            rf"{re.escape(action_kw)}\s+(?P<action>.+)",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(statement)
        if match is not None:
            return (
                match.group("condition").strip(),
                match.group("action").strip(),
            )
    return None


def _parse_condition(
    condition_text: str,
) -> Optional[Tuple[List[Clause], Optional[str]]]:
    or_parts = OR_SPLIT_RE.split(condition_text)
    combinator: Optional[str]
    if len(or_parts) > 1:
        combinator, parts = "or", or_parts
    else:
        and_parts = AND_SPLIT_RE.split(condition_text)
        if len(and_parts) > 1:
            combinator, parts = "and", and_parts
        else:
            combinator, parts = None, [condition_text]

    clauses: List[Clause] = []
    for part in parts:
        match = CONDITION_CLAUSE_RE.match(part.strip())
        if match is None:
            return None
        clauses.append(
            (
                match.group("variable"),
                match.group("operator"),
                match.group("value"),
            )
        )
    return clauses, combinator


def _parse_action(action_text: str) -> Optional[Clause]:
    stripped = action_text.strip().rstrip(".")
    for pattern, operator in ACTION_PHRASE_TABLE:
        match = pattern.match(stripped)
        if match is not None:
            return match.group("variable"), operator, match.group("value")
    return None


def _build_snippet(
    condition_clauses: List[Clause],
    condition_combinator: Optional[str],
    action: Clause,
) -> str:
    variable_names = sorted(
        {clause[0] for clause in condition_clauses} | {action[0]}
    )
    stub_lines = [f"{name} = None" for name in variable_names]

    python_combinator = " or " if condition_combinator == "or" else " and "
    condition_expr = python_combinator.join(
        f"{variable} {operator} {value}"
        for variable, operator, value in condition_clauses
    )

    action_variable, action_operator, action_value = action
    lines = [
        *stub_lines,
        f"if {condition_expr}:",
        f"    {action_variable} {action_operator} {action_value}",
    ]
    return "\n".join(lines) + "\n"


def _tree_sitter_confirms(snippet: str) -> bool:
    parser = Parser(_PY_LANGUAGE)
    tree = parser.parse(snippet.encode("utf-8"))
    return not tree.root_node.has_error


def _extract_requirement(node: SDocNode) -> Optional[RequirementEffect]:
    statement = node.reserved_statement
    uid = node.reserved_uid
    if statement is None or uid is None:
        return None

    split = _split_statement(statement)
    if split is None:
        return None
    condition_text, action_text = split

    parsed_condition = _parse_condition(condition_text)
    if parsed_condition is None:
        return None
    condition_clauses, condition_combinator = parsed_condition

    action = _parse_action(action_text)
    if action is None:
        return None

    snippet = _build_snippet(condition_clauses, condition_combinator, action)
    if not _tree_sitter_confirms(snippet):
        return None

    return RequirementEffect(
        uid=uid,
        node=node,
        condition_clauses=condition_clauses,
        condition_combinator=condition_combinator,
        action=action,
    )


def check_undefined_interfaces(
    effects: List[RequirementEffect],
    interfaces: Dict[str, InterfaceDecl],
    validation_index: ValidationIndex,
) -> None:
    for effect in effects:
        # dict.fromkeys: dedupe while keeping first-seen order, so a
        # variable used in both the condition and the action gets one
        # warning, not two.
        for variable in dict.fromkeys(effect.variables()):
            if variable not in interfaces:
                validation_index.add_issue(
                    effect.node,
                    f"Undefined interface: requirement '{effect.uid}' "
                    f"references undeclared variable '{variable}'.",
                    field="STATEMENT",
                )


def _as_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except ValueError:
        return None


def _bounds_for(operator: str, value: float) -> Tuple[float, bool, float, bool]:
    """(lower, lower_inclusive, upper, upper_inclusive), "!=" excluded."""
    neg_inf, pos_inf = float("-inf"), float("inf")
    if operator == ">":
        return value, False, pos_inf, False
    if operator == ">=":
        return value, True, pos_inf, False
    if operator == "<":
        return neg_inf, False, value, False
    if operator == "<=":
        return neg_inf, False, value, True
    assert operator == "=="
    return value, True, value, True


def _intervals_overlap(
    bounds_a: Tuple[float, bool, float, bool],
    bounds_b: Tuple[float, bool, float, bool],
) -> bool:
    lo_a, lo_a_incl, hi_a, hi_a_incl = bounds_a
    lo_b, lo_b_incl, hi_b, hi_b_incl = bounds_b

    lo, lo_incl = (
        (lo_a, lo_a_incl and lo_b_incl)
        if lo_a == lo_b
        else (lo_a, lo_a_incl)
        if lo_a > lo_b
        else (lo_b, lo_b_incl)
    )
    hi, hi_incl = (
        (hi_a, hi_a_incl and hi_b_incl)
        if hi_a == hi_b
        else (hi_a, hi_a_incl)
        if hi_a < hi_b
        else (hi_b, hi_b_incl)
    )

    if lo < hi:
        return True
    if lo > hi:
        return False
    return lo_incl and hi_incl


def _overlap_with_not_equal(
    operator_a: str, value_a: float, operator_b: str, value_b: float
) -> bool:
    if operator_a == "!=" and operator_b == "!=":
        return True  # each excludes only a single point out of the line
    if operator_b == "!=":
        operator_a, value_a, operator_b, value_b = (
            operator_b,
            value_b,
            operator_a,
            value_a,
        )
    if operator_b == "==":
        return value_a != value_b
    # "!=" against an inequality excludes at most one point from an
    # infinite range, so they overlap.
    return True


def _ranges_can_overlap(clause_a: Clause, clause_b: Clause) -> bool:
    _, operator_a, raw_value_a = clause_a
    _, operator_b, raw_value_b = clause_b

    value_a = _as_float(raw_value_a)
    value_b = _as_float(raw_value_b)
    if value_a is None or value_b is None:
        # Non-numeric values: only an exact "==" match is in the small,
        # explicit set this heuristic covers.
        return (
            operator_a == "=="
            and operator_b == "=="
            and (raw_value_a == raw_value_b)
        )

    if operator_a == "!=" or operator_b == "!=":
        return _overlap_with_not_equal(operator_a, value_a, operator_b, value_b)

    return _intervals_overlap(
        _bounds_for(operator_a, value_a), _bounds_for(operator_b, value_b)
    )


def _actions_disagree(action_a: Clause, action_b: Clause) -> bool:
    _, operator_a, value_a = action_a
    _, operator_b, value_b = action_b
    if operator_a == "=" and operator_b == "=":
        return value_a != value_b
    return OPPOSING_ACTION_OPERATORS.get(operator_a) == operator_b


def check_contradicting_requirements(
    effects: List[RequirementEffect], validation_index: ValidationIndex
) -> None:
    # Only single-clause conditions are compared: a compound (ИЛИ/И)
    # condition's pairwise overlap is out of this heuristic's scope.
    comparable_effects = [
        effect
        for effect in effects
        if not effect.is_compound
        and effect.action[0] == effect.condition_clauses[0][0]
    ]
    for index, effect_a in enumerate(comparable_effects):
        clause_a = effect_a.condition_clauses[0]
        for effect_b in comparable_effects[index + 1 :]:
            clause_b = effect_b.condition_clauses[0]
            if clause_a[0] != clause_b[0]:
                continue
            if not _ranges_can_overlap(clause_a, clause_b):
                continue
            if not _actions_disagree(effect_a.action, effect_b.action):
                continue
            validation_index.add_issue(
                effect_a.node,
                f"Contradicting requirement: '{effect_a.uid}' and "
                f"'{effect_b.uid}' can both apply to '{clause_a[0]}' at the "
                "same time but prescribe different actions.",
                field="STATEMENT",
            )
            validation_index.add_issue(
                effect_b.node,
                f"Contradicting requirement: '{effect_b.uid}' and "
                f"'{effect_a.uid}' can both apply to '{clause_b[0]}' at the "
                "same time but prescribe different actions.",
                field="STATEMENT",
            )


class RequirementIntegrityAnalyzer:
    @staticmethod
    def analyze_document_tree(traceability_index: TraceabilityIndex) -> None:
        validation_index = traceability_index.validation_index
        document_tree = traceability_index.document_tree
        assert document_tree is not None

        interfaces: Dict[str, InterfaceDecl] = {}
        effects: List[RequirementEffect] = []

        for document in document_tree.document_list:
            document_iterator = SDocDocumentIterator(document)
            for node, _ in document_iterator.all_content():
                if not isinstance(node, SDocNode):
                    continue

                if node.node_type == "INTERFACE_PARAMETER":
                    interface = _extract_interface(node)
                    if interface is None:
                        validation_index.add_issue(
                            node, CANNOT_CONVERT_MESSAGE, field="STATEMENT"
                        )
                        continue
                    interfaces[interface.name] = interface

                elif node.node_type == "REQUIREMENT":
                    effect = _extract_requirement(node)
                    if effect is None:
                        validation_index.add_issue(
                            node, CANNOT_CONVERT_MESSAGE, field="STATEMENT"
                        )
                        validation_index.add_issue(
                            node,
                            UNDEFINED_INTERFACE_CONVERSION_FAILED_MESSAGE,
                            field="STATEMENT",
                        )
                        validation_index.add_issue(
                            node,
                            CONTRADICTION_CONVERSION_FAILED_MESSAGE,
                            field="STATEMENT",
                        )
                        continue
                    effects.append(effect)

        check_undefined_interfaces(effects, interfaces, validation_index)
        check_contradicting_requirements(effects, validation_index)
