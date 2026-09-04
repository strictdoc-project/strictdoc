"""
Cross-requirement integrity checks.

Converts every REQUIREMENT node's condition/action text into a small Python
representation (parsed and confirmed with tree_sitter_python, the same
construction strictdoc/backend/sdoc_source_code/reader_python.py already
uses), then runs three whole-project checks against that representation:

1. check_undefined_interfaces: a requirement's condition or action names a
   variable no INTERFACE_PARAMETER node declares.
2. check_value_types: a requirement's condition or action compares/assigns
   a declared variable to a literal of the wrong type for it — e.g.
   started_cord==5 against an INTERFACE_PARAMETER declaring "Тип: bool".
   Validated with pydantic's strict TypeAdapter (see _parse_literal and
   check_value_types below for exactly what counts as a match).
3. check_contradicting_requirements: two requirements place conditions on
   the same variable that can hold at the same time, but prescribe actions
   on that variable that disagree.

All three are warnings, reported through the existing
strictdoc/core/validation_index.py::ValidationIndex.add_issue, never a
build-stopping error.

A REQUIREMENT or INTERFACE_PARAMETER node whose text does not match the
expected pseudo-code shape closely enough to convert gets a single "could
not convert" warning that names the specific reason (missing TITLE, no
matching ЕСЛИ/КОГДА/IF template, an unparsable condition or action, ...) so
a student can fix the text without guessing. It does not also report the
whole-project checks as separately "failed" for that node — those checks
never had anything to run against for an unconverted node, so another
warning saying so again would be redundant with the first. This does not
cascade — another node's conversion failure never fails this node's checks.

Requirements in this fork are written in Russian, so the pseudo-code shape
is matched in Russian as well as English, and every message this module
produces is in Russian: the students reading them are not assumed to read
English.

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

import ast
import keyword
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern, Tuple, Union

import tree_sitter_python
from pydantic import TypeAdapter, ValidationError
from tree_sitter import Language, Parser

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.validation_index import ValidationIndex

Clause = Tuple[str, str, str]  # (variable, operator, value)

# A header, not a full sentence: _cannot_convert_message() appends the
# specific reason (in Russian) an actual node's text failed to convert, so
# the message a student sees always says what to fix, not just that
# something is wrong.
CANNOT_CONVERT_MESSAGE = (
    "Не удалось привести текст этого узла к проверяемому виду:"
)


def _cannot_convert_message(reason: str) -> str:
    return f"{CANNOT_CONVERT_MESSAGE} {reason}."


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

# Shared with the action-side patterns below, so "robot.velocity.x" is a
# valid variable name on both sides of a requirement, not just in a
# condition: anything but whitespace, parens, and the operator characters
# themselves (a dotted attribute path is a plain, syntactically valid
# Python assignment/comparison target, so tree_sitter accepts it same as a
# flat identifier — see _tree_sitter_confirms()). "+"/"-" are excluded too,
# not just "=": without that, a no-space "x+=5" would greedily swallow the
# "+" into the variable, leaving "=" to look like a plain "=" assignment
# instead of "+=" — ACTION_ASSIGNMENT_RE below needs the boundary clean.
VARIABLE_RE = r"[^\s()=!<>+-]+"

CONDITION_CLAUSE_RE = re.compile(
    rf"^(?P<variable>{VARIABLE_RE})\s*"
    r"(?P<operator>==|!=|<=|>=|<|>)\s*"
    r"(?P<value>\S+)$"
)

TYPE_LINE_RE = re.compile(r"(?im)^\s*(?:Type|Тип)\s*:\s*(?P<type_name>\S+)")

# The interface's declared type, named in English same as a requirement's
# variable/value tokens are (see VARIABLE_RE above and AGENTS.md's
# "Technical writing" section) — only the "Тип:"/"Type:" label itself is
# bilingual, not the type keyword after it.
TYPE_NAME_TO_PYTHON_TYPE: Dict[str, type] = {
    "bool": bool,
    "int": int,
    "float": float,
    "str": str,
}

# action phrase -> python operator. Matched against the action text, which
# reads "<phrase> <variable> ... <value>".
ACTION_PHRASE_TABLE: List[Tuple[Pattern[str], str]] = [
    (
        re.compile(
            rf"^set\s+(?P<variable>{VARIABLE_RE})\s+to\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "=",
    ),
    (
        re.compile(
            rf"^increase\s+(?P<variable>{VARIABLE_RE})\s+by\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "+=",
    ),
    (
        re.compile(
            rf"^decrease\s+(?P<variable>{VARIABLE_RE})\s+by\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "-=",
    ),
    (
        re.compile(
            rf"^установить\s+(?P<variable>{VARIABLE_RE})\s+в\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "=",
    ),
    (
        re.compile(
            rf"^увеличить\s+(?P<variable>{VARIABLE_RE})\s+на\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "+=",
    ),
    (
        re.compile(
            rf"^уменьшить\s+(?P<variable>{VARIABLE_RE})\s+на\s+(?P<value>\S+)$",
            re.IGNORECASE,
        ),
        "-=",
    ),
]

# Fallback for an action written as a bare Python-style assignment instead
# of one of the verb phrases above, e.g. "robot.velocity.x = 70" or
# "motor_Speed += 5" — same VARIABLE_RE, so a dotted path works here too.
ACTION_ASSIGNMENT_RE = re.compile(
    rf"^(?P<variable>{VARIABLE_RE})\s*(?P<operator>\+=|-=|=)\s*(?P<value>\S+)$"
)

OPPOSING_ACTION_OPERATORS = {"+=": "-=", "-=": "+="}

_PY_LANGUAGE = Language(tree_sitter_python.language())


@dataclass
class InterfaceDecl:
    name: str
    node: SDocNode
    # As written after "Тип:"/"Type:" (e.g. "bool") and the Python type it
    # maps to — both kept, so check_value_types() below can validate against
    # value_type while still naming type_name (the student's own spelling)
    # in the message it reports.
    type_name: str
    value_type: type


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


def _extract_interface(node: SDocNode) -> Union[InterfaceDecl, str]:
    """Returns the parsed interface, or a Russian reason it could not be."""
    title = node.reserved_title
    statement = node.reserved_statement or ""
    if title is None or not title.strip():
        return (
            "у узла должно быть заполнено поле TITLE — это имя переменной "
            "интерфейса"
        )
    type_match = TYPE_LINE_RE.search(statement)
    if type_match is None:
        return (
            "в тексте STATEMENT должна быть строка вида «Тип: <тип>» "
            "(английское «Type:» тоже подходит), например «Тип: bool»"
        )
    type_name = type_match.group("type_name").rstrip(".,;:")
    value_type = TYPE_NAME_TO_PYTHON_TYPE.get(type_name.lower())
    if value_type is None:
        return (
            f"в STATEMENT указан неизвестный тип «{type_name}» — допустимые "
            f"типы: {', '.join(sorted(TYPE_NAME_TO_PYTHON_TYPE))}"
        )
    return InterfaceDecl(
        name=title.strip(),
        node=node,
        type_name=type_name,
        value_type=value_type,
    )


NO_CONDITION_REASON = (
    "не найдено условие вида «ЕСЛИ (условие) ТО ...», «КОГДА (условие) "
    "ТОГДА ...» или «IF (condition) THEN ...» — условие должно стоять в "
    "круглых скобках сразу после ключевого слова (перед скобками можно "
    "добавить пояснение словами), например «ЕСЛИ (motor_Speed > 10) ТО ...»"
)


def _split_statement(statement: str) -> Union[Tuple[str, str], str]:
    """
    Returns (condition_text, action_text) on success, or a Russian reason
    naming specifically which half — condition or action — is missing or
    malformed, so a student knows which one to fix.
    """
    # [^(]*? before each "(" lets a human-readable clause sit between the
    # keyword and the parenthesized, checkable expression, e.g. "ЕСЛИ
    # стартовый корд выдернут (started_cord == true) ТО робот должен
    # начать движение (установить robot_moving в true)" — the prose is
    # documentation for the reader; only what's in parens is parsed.
    found_condition = False
    for condition_kw, then_kw, action_kw in KEYWORD_PAIRS:
        condition_match = re.search(
            rf"{condition_kw}[^(]*?\((?P<condition>.+?)\)\s*{then_kw}",
            statement,
            re.IGNORECASE | re.DOTALL,
        )
        if condition_match is None:
            continue
        found_condition = True

        # The action's parens are optional (unlike the condition's):
        # action_in_parens is tried first, action_plain falls back to the
        # older, unparenthesized "робот должен <action>" shape.
        action_match = re.search(
            rf"{re.escape(action_kw)}\s*"
            rf"(?:[^(]*?\((?P<action_in_parens>.+?)\)|(?P<action_plain>.+))",
            statement[condition_match.end() :],
            re.IGNORECASE | re.DOTALL,
        )
        if action_match is None:
            continue

        action = action_match.group("action_in_parens")
        if action is None:
            action = action_match.group("action_plain")
        action = action.strip()
        # A whitespace-only tail (e.g. statement ends right after "робот
        # должен ") is the same "no action" situation as no match at all.
        if action:
            return condition_match.group("condition").strip(), action

    if found_condition:
        return (
            "условие распознано, но не найдено действие после «робот "
            "должен» (или «system shall») — например «...ТО робот должен "
            "уменьшить motor_Speed на 5»"
        )
    return NO_CONDITION_REASON


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
    # Fallback: a bare Python-style assignment ("robot.velocity.x = 70",
    # "motor_Speed += 5") instead of a verb phrase.
    assignment_match = ACTION_ASSIGNMENT_RE.match(stripped)
    if assignment_match is not None:
        return (
            assignment_match.group("variable"),
            assignment_match.group("operator"),
            assignment_match.group("value"),
        )
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


def _invalid_identifier_reason(name: str) -> Optional[str]:
    """
    None if `name` is usable as a Python name or dotted attribute path
    (e.g. "cmd.velocity.x"); otherwise a Russian reason pinpointing which
    dot-separated part is the problem. Checked before _build_snippet() so
    a bad variable name gets its own specific message instead of surfacing
    as the generic "syntax check failed" once it's buried inside a
    multi-line generated snippet.
    """
    for part in name.split("."):
        # Not issoftkeyword() too: "match"/"case"/"type"/"_" are only
        # special in their own statement context — used as a plain name
        # (which is all a dotted attribute path segment ever is here),
        # they're valid Python and tree_sitter agrees.
        if keyword.iskeyword(part):
            return (
                f"«{part}» в имени «{name}» — зарезервированное слово "
                "Python (как «if», «in», «class», «for», …) и не может "
                "быть именем переменной; выберите другое имя"
            )
        if not part.isidentifier():
            return (
                f"«{part}» в имени «{name}» не является допустимым именем "
                "переменной в Python — разрешены буквы, цифры и «_», имя "
                "не может начинаться с цифры"
            )
    return None


def _extract_requirement(node: SDocNode) -> Union[RequirementEffect, str]:
    """Returns the parsed requirement, or a Russian reason it could not be."""
    statement = node.reserved_statement
    uid = node.reserved_uid
    if statement is None or uid is None:
        return "у узла должны быть заполнены поля UID и STATEMENT"

    split = _split_statement(statement)
    if isinstance(split, str):
        return split
    condition_text, action_text = split

    parsed_condition = _parse_condition(condition_text)
    if parsed_condition is None:
        return (
            f"условие «{condition_text}» не удалось разобрать — каждая "
            "часть должна иметь вид «переменная оператор значение» "
            "(например, motor_Speed > 10), а части соединяются словами "
            "И/ИЛИ"
        )
    condition_clauses, condition_combinator = parsed_condition

    action = _parse_action(action_text)
    if action is None:
        return (
            f"действие «{action_text}» не удалось разобрать — ожидались "
            "фразы вроде «установить <переменная> в <значение>», "
            "«увеличить <переменная> на <значение>», «уменьшить "
            "<переменная> на <значение>» либо прямое присваивание вида "
            "«<переменная> = <значение>» (также «+=»/«-=»)"
        )

    for variable, _, _ in condition_clauses:
        reason = _invalid_identifier_reason(variable)
        if reason is not None:
            return reason
    action_reason = _invalid_identifier_reason(action[0])
    if action_reason is not None:
        return action_reason

    snippet = _build_snippet(condition_clauses, condition_combinator, action)
    if not _tree_sitter_confirms(snippet):
        return (
            "получившееся выражение не прошло синтаксическую проверку — "
            "проверьте имена переменных и значения в условии и действии"
        )

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
                    f"Неопределённый интерфейс: требование «{effect.uid}» "
                    f"ссылается на необъявленную переменную «{variable}».",
                    field="STATEMENT",
                )


def _parse_literal(value: str) -> Optional[object]:
    """
    Interprets a condition/action value token (already confirmed to be
    *some* syntactically valid Python expression by _tree_sitter_confirms)
    as a concrete Python value, for check_value_types() to compare against
    an interface's declared type.

    Returns None when the token isn't a literal at all — e.g. it names
    another variable ("robot.velocity.x"), which has no fixed type of its
    own to compare here; that's out of this check's scope.

    "true"/"false" are handled before ast.literal_eval because the DSL
    accepts them lowercase (see e.g. eurobot/Eurobot_Requirements.sdoc's
    "started_cord==true"), which ast.literal_eval rejects — it only knows
    Python's capitalized True/False.
    """
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    try:
        return ast.literal_eval(stripped)
    except (ValueError, SyntaxError):
        return None


def check_value_types(
    effects: List[RequirementEffect],
    interfaces: Dict[str, InterfaceDecl],
    validation_index: ValidationIndex,
) -> None:
    """
    A requirement's condition/action may compare or assign an interface
    variable to a value of the wrong type for it — e.g. "Тип: bool" but the
    requirement writes started_cord==5 or started_cord=="да". Validated with
    pydantic's strict TypeAdapter, so e.g. an int literal is still accepted
    for a "Тип: float" variable (70 is a perfectly good float), but not for
    "Тип: bool" (bool must be exactly True/False, not 0/1) or "Тип: str"
    (str must be quoted text, not a bare number).
    """
    for effect in effects:
        for variable, _, value in [*effect.condition_clauses, effect.action]:
            interface = interfaces.get(variable)
            if interface is None:
                continue  # check_undefined_interfaces already covers this
            literal = _parse_literal(value)
            if literal is None:
                continue  # not a literal (e.g. compared to another variable)
            try:
                TypeAdapter(interface.value_type).validate_python(
                    literal, strict=True
                )
            except ValidationError:
                validation_index.add_issue(
                    effect.node,
                    f"Несовпадение типа: в требовании «{effect.uid}» "
                    f"значение «{value}» переменной «{variable}» не "
                    f"подходит под тип «{interface.type_name}», объявленный "
                    "у интерфейса.",
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
                f"Противоречащие требования: «{effect_a.uid}» и "
                f"«{effect_b.uid}» могут одновременно применяться к "
                f"«{clause_a[0]}», но предписывают разные действия.",
                field="STATEMENT",
            )
            validation_index.add_issue(
                effect_b.node,
                f"Противоречащие требования: «{effect_b.uid}» и "
                f"«{effect_a.uid}» могут одновременно применяться к "
                f"«{clause_b[0]}», но предписывают разные действия.",
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
                    if isinstance(interface, str):
                        validation_index.add_issue(
                            node,
                            _cannot_convert_message(interface),
                            field="STATEMENT",
                        )
                        continue
                    interfaces[interface.name] = interface

                elif node.node_type == "REQUIREMENT":
                    effect = _extract_requirement(node)
                    if isinstance(effect, str):
                        validation_index.add_issue(
                            node,
                            _cannot_convert_message(effect),
                            field="STATEMENT",
                        )
                        continue
                    effects.append(effect)

        check_undefined_interfaces(effects, interfaces, validation_index)
        check_value_types(effects, interfaces, validation_index)
        check_contradicting_requirements(effects, validation_index)
