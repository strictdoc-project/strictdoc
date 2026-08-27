# Test execution dashboard

## WHAT

A custom `Feature` (built on `strictdoc/core/feature.py`) that counts and
lists four coverage gaps, rather than only tallying test status:

1. `RULE` nodes (from `20260827_eurobot_rules_import`) that no `REQUIREMENT`
   covers.
2. `REQUIREMENT` nodes that cover no `RULE`.
3. `REQUIREMENT` nodes that no `TEST_CASE` covers.
4. `TEST_CASE` nodes whose `STATUS` is not `Passed`.

Each gap shows both a count, for the at-a-glance dashboard number, and a
list (UID, title, a link to the node), so a mentor can act on it directly
instead of hunting for the affected nodes afterward.

A revision control lets a mentor scope all four gaps to one revision's own
requirements, or cumulatively to everything planned up to and including a
chosen revision (`TARGET_REVISION` from `20260827_release_versioning`).

## WHY

A plain status tally does not answer what a mentor actually needs before a
test session: which rules are still unaddressed, which requirements exist
without covering a rule, which requirements have no test yet, and which
tests still need to pass, all scoped to what should already be done by a
given revision. These four questions are what the team asked the dashboard
to answer.

They are also already answerable with primitives this fork's own code
already has, not new machinery:

- A `Parent` relation writes both directions of the graph edge at
  index-build time (`strictdoc/core/traceability_index_builder.py`, lines
  670-681): when a `REQUIREMENT` declares `Parent` pointing at a `RULE`, the
  builder records the forward edge on the `REQUIREMENT` and the reverse
  edge on the `RULE` in the same step. A `RULE` node's list of covering
  requirements is therefore already available with no extra wiring.
- `get_parent_requirements()` and `get_children_requirements()`
  (`strictdoc/core/traceability_index.py`) check only that a node is an
  `SDocNode` with a UID, not that it is tagged `REQUIREMENT`. They already
  work on `RULE` and `TEST_CASE` nodes the same way they work on
  `REQUIREMENT` nodes.
- This exact shape of check already exists for the built-in case:
  `strictdoc/features/project_statistics/generator.py` (lines 68-88)
  computes "requirements no one traces to" via
  `len(get_children_requirements(requirement)) == 0` and "requirements that
  trace to nothing" via `len(get_parent_requirements(requirement)) == 0`.
  Gaps 1 through 3 are the same two checks, applied to `RULE`,
  `REQUIREMENT`, and `TEST_CASE` at different points in the Rule to
  Requirement to Test chain, not a new kind of check.

The Query Engine cannot do this task by itself, which is why it needs a
dedicated `Feature` rather than a saved search: its grammar
(`strictdoc/core/query_engine/grammar.py`) has no ordering or range operator
(only equality, inequality, and list membership), so "cumulative up to
revision C2" cannot be written as one query string, and its type predicates
(`is_requirement()`, `is_section()`, and so on) are hardcoded to specific
built-in tags, with no equivalent for a custom tag like `RULE` or
`TEST_CASE`.

## HOW

Structure: mirror `ProjectStatisticsFeature`'s split between `feature.py`
(the thin `Feature` subclass: `HANDLE`, `supports_export()`,
`supports_server()`, `screen_filename()`, `screen_icon()`) and `screen.py`
(the actual generation logic, called from `render_screen()`).

Iteration: walk every node the same way `ProgressStatisticsGenerator.export()`
already does: loop `traceability_index.document_tree.document_list`, wrap
each document in `SDocDocumentIterator(document).all_content(...)`, and
filter by `node.node_type == "RULE"` (or `"REQUIREMENT"`, or `"TEST_CASE"`).

Gap computation, reusing the traceability index's own methods directly
rather than the Query Engine:

- Gap 1: for each `RULE` node, `len(get_children_requirements(rule_node))
  == 0`.
- Gap 2: for each `REQUIREMENT` node, `len(get_parent_requirements(req_node))
  == 0`.
- Gap 3: for each `REQUIREMENT` node, `len(get_children_requirements(req_node))
  == 0`.
- Gap 4: for each `TEST_CASE` node, its `STATUS` field value is not
  `"Passed"`.

Revision filter, done in the feature's own Python code, since the Query
Engine has no ordering operator to express it:

- Gaps 2 and 3 filter directly on the `REQUIREMENT`'s own `TARGET_REVISION`
  field.
- Gaps 1 and 4 are transitive, since neither `RULE` nor `TEST_CASE` carries
  `TARGET_REVISION` itself: a `RULE` only counts a covering `REQUIREMENT`
  toward coverage if that requirement's `TARGET_REVISION` falls within the
  selected range, so a rule whose only covering requirement is planned for
  a later revision still shows as uncovered at the earlier one. A
  `TEST_CASE` is in range only if the `REQUIREMENT`(s) it traces to
  (`get_parent_requirements(test_case_node)`) are.
- "Cumulative up to revision X" needs a defined chronological order for
  revision identifiers, not string comparison: major-letter codenames are
  not guaranteed to be assigned in strict alphabetical sequence, so whether
  `C1` comes before or after `D2` cannot be decided by comparing the
  letters. This depends on `20260827_release_versioning` keeping its
  `TARGET_REVISION` choices as an explicit, ordered list, so "cumulative"
  resolves as a list-position lookup rather than a string comparison. Not
  solved here; flagged as a dependency on that task.

Rendering: each gap renders its own list (UID, title, a link to the node)
directly in the dashboard's own template, rather than linking out to the
generic Query Engine search screen the way `ProjectStatistics` does for its
own orphan-requirement metric, since the search screen has no way to select
a custom tag like `RULE` or `TEST_CASE` in the first place.

Registration: add the new `HANDLE` (for example
`"EUROBOT_TEST_DASHBOARD"`) to the Eurobot project's `project_features`,
following the same `List[Union[str, Feature]]` mechanism `ProjectConfig`
already resolves.

Dependencies: needs `20260827_requirements_and_test_grammar`'s `RULE`,
`REQUIREMENT`, `TEST_CASE` elements and `STATUS` field, and
`20260827_release_versioning`'s `TARGET_REVISION` field. Both are
prerequisites, not later additions; this task cannot be built before them.

### Deferred work

- The ordered-revision-list requirement above is a dependency on
  `20260827_release_versioning`, not addressed by editing that task in this
  pass.
- Trend over time (pass rate or gap counts across RCs) is not part of this
  task. It would need reading past states out of git tags (see
  `20260827_release_versioning`'s diff-based recovery) rather than the live
  tree, and is a separate, larger piece of work.
