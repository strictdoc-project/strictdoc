# TEST_CASE integrity checks

## WHAT

Extends the existing non-blocking requirement-integrity analysis pass
(`strictdoc/core/analyzers/requirement_integrity_analyzer.py`, see
`developer/tasks/eurobot/20260827_requirement_integrity_checks/task.md`)
to also convert every `TEST_CASE` node in `eurobot/Eurobot_Tests.sdoc`
whose STATEMENT matches the shape

    ЕСЛИ (<condition>) ТО УСПЕХ [ИНАЧЕ ПРОВАЛ]

into a small Python representation, then runs three checks against it:

1. Undefined interface: the condition names a variable no
   `INTERFACE_PARAMETER` node declares anywhere in the project — the same
   check `REQUIREMENT` nodes already get.
2. Value type mismatch: the condition compares a declared variable to a
   literal of the wrong type for it — the same check `REQUIREMENT` nodes
   already get.
3. Outcome not fully defined: the STATEMENT has a `ТО УСПЕХ` branch
   without an `ИНАЧЕ ПРОВАЛ` branch, or vice versa. This check has no
   `REQUIREMENT` analog.

A `TEST_CASE` whose STATEMENT does not match this shape at all — the free
prose style `TC-1`/`TC-2`/`TC-3` already use ("Ожидаемый результат: ...")
— gets a single "could not convert" warning, the same wording convention
as an unconvertible `REQUIREMENT`, and is excluded from all three checks.
Their STATEMENT text is not rewritten by this task.

All three checks are warnings only, reported through the existing
`ValidationIndex.add_issue`, never build-stopping.

`REQ-7`'s `STATEMENT` is rewritten as part of this task, to check a
physically meaningful condition (has the robot's position moved past the
start zone) instead of the trivial cord-pulled flag it checked before, and
to double as a live example of check #1: it references
`dbg.pose.position.z`, which is not declared as an `INTERFACE_PARAMETER`
(only `.x`, `.y`, and `.orientation.yaw` are), so it now shows exactly one
undefined-interface warning. That variable is left undeclared on purpose.

## WHY

`REQ-7`'s test case already wrote its STATEMENT in the `ЕСЛИ (condition)
ТО УСПЕХ ИНАЧЕ ПРОВАЛ` shape, referencing `input.started_cord`, an
`INTERFACE_PARAMETER` declared in `Eurobot_Requirements.sdoc`. That is
exactly the same kind of integrity problem a `REQUIREMENT` can already
have — a reference to an interface nobody declared, or a value of the
wrong type — just on the test-case side of the same fork's grammar
(`eurobot/eurobot_tests_grammar.sgra`'s `TEST_CASE`, `RELATIONS: ROLE:
VERIFIES` back to a `REQUIREMENT`). A missing outcome definition is its
own, test-case-specific mistake: a test case that says `ТО УСПЕХ` but
never says what a failure looks like is not actually checkable in
practice.

This reuses `requirement_integrity_analyzer.py`'s existing machinery
rather than adding new machinery:

- The analyzer already walks every document via `SDocDocumentIterator`
  and already builds `interfaces: Dict[str, InterfaceDecl]` once per pass.
  A `TEST_CASE`'s condition is checked against that same table — no
  second whole-project walk, no new hook point. Both existing call sites
  (`strictdoc/features/export/export_action.py`,
  `strictdoc/server/routers/main_router.py`) need no changes.
- `_invalid_identifier_reason`, `_tree_sitter_confirms`, and
  `_parse_literal` are reused unchanged.
- `_parse_condition`'s OR/AND-splitting logic is reused via a new optional
  `clause_pattern` parameter (default unchanged), rather than duplicated,
  because `TEST_CASE` condition clauses in `Eurobot_Tests.sdoc` use a bare
  `=` for equality (`input.started_cord=true`) where `REQUIREMENT` always
  uses `==` (`input.started_cord==true`, see `REQ-6`) — a `TEST_CASE`-only
  regex accepts both, normalized to `==` before it reaches the generated
  Python snippet.
- `check_undefined_interfaces`/`check_value_types` are mirrored, not
  generalized, into `check_test_case_undefined_interfaces`/
  `check_test_case_value_types`: a `TEST_CASE` has no action clause (its
  outcome is the fixed УСПЕХ/ПРОВАЛ vocabulary, not an arbitrary
  assignment), so reshaping `RequirementEffect`/the existing check
  functions to share an implementation would touch code paths
  `REQUIREMENT` already relies on, to save a small amount of duplication.

## HOW

Bottom line: add a `TestCaseEffect` dataclass, `TEST_CASE`-only parsing
functions (`_split_test_case_statement`, `_extract_test_case`,
`_build_test_case_snippet`), and three `TEST_CASE`-only check functions,
all inside `requirement_integrity_analyzer.py`; wire them into the same
`RequirementIntegrityAnalyzer.analyze_document_tree` entry point that
already handles `REQUIREMENT`/`INTERFACE_PARAMETER`.

**Extraction, per `TEST_CASE` node.** Read `node.reserved_statement`;
match `ЕСЛИ`/`КОГДА`/`IF` ... `(condition)` ... `ТО`/`ТОГДА`/`THEN` (the
same condition-extraction shape `REQUIREMENT` uses); then scan the text
after the then-keyword for the words `УСПЕХ` and `ПРОВАЛ` (in either
order, either or both present). Parse the condition into `(variable,
operator, value)` clauses with `_parse_condition`, generate a Python
snippet (`<var> = None` stubs plus an `if <condition>: pass` line) and
confirm it with `tree_sitter_python`, the same construction `REQUIREMENT`
uses. A `TEST_CASE` whose text does not match the `ЕСЛИ (condition) ТО
...` shape at all, or matches it but names neither `УСПЕХ` nor `ПРОВАЛ`
anywhere after `ТО`, gets one "could not convert" warning and is excluded
from the checks below — same non-cascading philosophy `REQUIREMENT`
already has.

**Checks, run once per build** against the whole-project
`test_case_effects: List[TestCaseEffect]` table and the shared
`interfaces` table:

- `check_test_case_undefined_interfaces`: a condition names a variable
  absent from `interfaces`.
- `check_test_case_value_types`: a condition compares a declared variable
  to a literal of the wrong type, validated the same way (pydantic's
  strict `TypeAdapter`) as `REQUIREMENT`'s check.
- `check_test_case_outcome_defined`: the STATEMENT is missing a `ТО
  УСПЕХ` branch, an `ИНАЧЕ ПРОВАЛ` branch, or both — up to two separate
  warnings, one per missing branch.

**Content change.** `REQ-7`'s STATEMENT in `eurobot/Eurobot_Tests.sdoc`
now reads:

    1. Установить робота на старт (dbg.pose.position.z=0 И dbg.pose.position.y=0)
    2. Выдернуть стартовый корд (input.started_cord=true)
    ЕСЛИ робот выехал из зоны старта (dbg.pose.position.z > 0.125 И dbg.pose.position.y > 0.125)
    ТО УСПЕХ
    ИНАЧЕ ПРОВАЛ

The compound condition is joined with `И`, the existing `AND_SPLIT_RE`
keyword `REQUIREMENT` conditions already use — no parser change needed.
`dbg.pose.position.z` has no matching `INTERFACE_PARAMETER`, so
`check_test_case_undefined_interfaces` reports it; that is expected, kept
as a working example of the check rather than fixed here.

### Deferred work

- No check relates a `TEST_CASE`'s outcome back to the `REQUIREMENT` it
  `VERIFIES` (`RELATIONS: ROLE: VERIFIES`) — e.g. confirming the test
  case's condition variable is the same one the requirement's condition
  names. Out of scope for this pass.
- `TC-1`/`TC-2`/`TC-3`'s free-prose STATEMENT text is left as-is; making
  them convertible (rewriting them into the `ЕСЛИ (...) ТО УСПЕХ ИНАЧЕ
  ПРОВАЛ` shape) is course content work, not covered here.
