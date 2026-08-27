# Cross-requirement integrity checks

## WHAT

A non-blocking analysis pass, running as part of every `strictdoc export`
and `strictdoc server` build, that converts every `REQUIREMENT` and
`INTERFACE_PARAMETER` node's text into a small Python representation, then
runs a fixed suite of whole-project integrity checks against that
representation:

1. Undefined interface: a `REQUIREMENT`'s condition or action names a
   variable that no `INTERFACE_PARAMETER` node declares anywhere in the
   project.
2. Contradicting requirements: two `REQUIREMENT` nodes place conditions on
   the same variable that can both hold at the same time, but prescribe
   actions on that variable that cannot both be true.

The IF/THEN pseudo-code shape (functional requirements) and the
`prefix_Variable`/`Description`/`Type` shape (interface parameters) exist so
the converter can reliably pull a `(variable, operator, value, action)`
tuple out of a requirement and a `(name, type)` declaration out of an
interface parameter. The shape itself is not what gets checked; matching it
is only a means to that extraction.

Both checks report a warning attached to the offending node, never a
build-stopping error: an undefined interface reference or a suspected
contradiction is a note for the team to look at, not something that stops
anyone's `export` or `server` run.

## WHY

The team does not want a style checker. They want checks that catch actual
integrity problems across the whole requirement set: a requirement that
quietly depends on an interface nobody defined, or two requirements that
silently disagree about what should happen under the same condition. Both
mistakes are easy to make by hand once the requirement set grows past what
one person holds in their head, and neither is visible from reading one
requirement at a time.

The two structured text shapes make this possible without building a
natural-language understanding system. A functional requirement already
commits to naming one `variable`, one comparison `operator`, one `value`,
and one `action` per condition and per action line. An interface parameter
already commits to naming one `prefix_Variable` and one `Type`. That
consistency is what turns free-form prose into a small, comparable Python
object, the same reason StrictDoc's own `ReqIFFormat` and `ExcelFormat`
import against a fixed schema instead of parsing arbitrary documents.

This reuses infrastructure already present in this fork rather than adding
new machinery:

- **A non-blocking, per-node warning mechanism already exists, fully built
  end to end, and nothing calls it.** `strictdoc/core/validation_index.py`:
  `ValidationIndex.add_issue(node, issue, field=None)` stores an issue per
  node/field and prints it to the console. The HTML side already reads it:
  `render_issues()` in
  `strictdoc/export/html/generators/view_objects/document_screen_view_object.py`
  is already called from the STATEMENT field template
  (`strictdoc/export/html/templates/components/node_field/statement/index.jinja`),
  rendering `components/issue/index.jinja` with existing CSS
  (`.field_issue-ribbon` in `strictdoc/export/html/_static/element.css`).
  `add_issue` is called from nowhere in the codebase today. This task can
  be the first feature that actually populates it, with no new HTML or CSS
  work needed.
- **An existing analyzer shape fits a whole-project pass like this.**
  `strictdoc/core/analyzers/document_uid_analyzer.py`'s `DocumentUIDAnalyzer`
  already walks every document and node via `SDocDocumentIterator` to
  compute project-wide stats, structurally the closest existing thing to a
  cross-node analysis pass. It is not currently called from `export`, only
  from server routes and two CLI commands, so this task's analyzer is the
  first to hook into the export/server build path directly.
- **One shared hook point covers both `export` and `server`.**
  `TraceabilityIndexBuilder.create(...)`
  (`strictdoc/core/traceability_index_builder.py`) is called from both
  `ExportAction.build_index()` (`strictdoc/features/export/export_action.py`)
  and the server's `rebuild_index_after_file_change()`
  (`strictdoc/server/routers/main_router.py`). Running the new analyzer
  once, right after each of those two calls, covers every `strictdoc
  export` and every `strictdoc server` rebuild the same way.
- **`tree-sitter-python` is already a runtime dependency and already used
  to parse Python source in this codebase**
  (`strictdoc/backend/sdoc_source_code/reader_python.py`), unlike stdlib
  `ast`, which nothing here uses. Reusing it to re-parse each generated
  snippet into a structured tuple matches the codebase's own convention
  instead of adding a second, unprecedented parsing approach.

## HOW

Bottom line: extract every `REQUIREMENT` and `INTERFACE_PARAMETER` node
into a plain Python object, collect those objects into two whole-project
tables, then run a small, fixed set of check functions over the tables and
report each finding through `ValidationIndex.add_issue`.

**Grammar addition.** This task defines a new `INTERFACE_PARAMETER`
element: `TITLE` holds the `prefix_Variable` name, `STATEMENT` holds the
`Description`/`Type`/type-specific-fields body. This is an addition to the
shared grammar, the same way `20260827_eurobot_rules_import` added `RULE`'s
`STATUS` field; `20260827_requirements_and_test_grammar` is not edited in
this pass.

**Extraction, per node.**

- `REQUIREMENT`: read `node.reserved_statement` (the grammar-resolved
  content field, not a hardcoded `"STATEMENT"` string); line-match `IF`,
  the parenthesized condition, `THEN`, and `system shall`; pull
  `(variable, operator, value)` out of the condition line and
  `(variable, action, value)` out of the action line, using a small,
  explicit action-phrase table (for example "set to" maps to `=`,
  "increase by" maps to `+=`).
- `INTERFACE_PARAMETER`: read `TITLE` as the variable name; read
  `reserved_statement` for `Description:` and `Type:` lines.
- From each extracted tuple, generate a short Python snippet (a stub
  variable declaration plus, for a requirement, an `if variable <op>
  value:` line and its action line) and parse that snippet with
  `tree_sitter_python`, the same construction
  `reader_python.py` already uses, to get back a structured tuple rather
  than trusting the original text match blindly. A node whose text does
  not match its expected shape closely enough to produce a tuple gets one
  warning ("could not convert this node's text into a checkable form") and
  is excluded from the checks below; a shape mismatch is a fact worth
  reporting on its own; it does not by itself imply an integrity problem.

**Whole-project tables**, built once per build from every extracted node:

- `interfaces: dict[str, InterfaceDecl]`, one entry per `INTERFACE_PARAMETER`
  node, keyed by its variable name.
- `requirement_effects: list[RequirementEffect]`, one entry per
  `REQUIREMENT` node, holding its UID, its condition tuple, and its action
  tuple.

**Integrity checks**, run once per build after every node has been
converted:

- `check_undefined_interfaces`: for every `RequirementEffect`, look up its
  condition's and action's variable name in `interfaces`. A name absent
  from `interfaces` is one warning on that requirement's node, naming the
  missing variable.
- `check_contradicting_requirements`: for every pair of
  `RequirementEffect`s that share the same condition variable, decide
  whether their condition ranges can hold at the same time (an exact match
  on `operator` and `value` for `==`; an overlap check for `<`, `<=`, `>`,
  `>=`; mixed-operator pairs start from a small, explicit set the team
  actually uses). When the conditions can hold together, compare the two
  actions on that variable; if they disagree (different `value`, or
  opposite action verbs, such as an "increase" pattern against a
  "decrease" pattern), record one warning on each of the two requirement
  nodes, each naming the other requirement's UID, so a reviewer can open
  both side by side.
- This is a heuristic pass, not a formal proof. Natural-language operators
  and values leave real room for a false positive (a flagged pair a human
  reads and dismisses) or a false negative (a genuine contradiction phrased
  in a way the heuristic misses). That is acceptable for a warning; it
  would not be acceptable for a build-blocking error, which is why this
  entire feature stays warning-only.

**Hook point and warning surface**, unchanged by the checks themselves:
a new `strictdoc/core/analyzers/requirement_integrity_analyzer.py`
module, mirroring `document_uid_analyzer.py`'s shape, run once right after
`TraceabilityIndexBuilder.create(...)` succeeds at both existing call
sites. Every finding calls `validation_index.add_issue(node, message,
field=...)`, which `render_issues()` and the existing `.field_issue-ribbon`
template already render with no new UI code.

### Deferred work

- Overlap detection between differing comparison operators (for example,
  does `speed > 10` overlap with `speed != 12`) starts with a small,
  explicit set of operator pairs the team actually uses; the general case
  is not solved here.
- Only pairwise contradictions are checked. Three or more requirements that
  are fine two at a time but jointly impossible are not detected.
- The document-level issues banner
  (`strictdoc/export/html/templates/components/issue/banner.jinja`) is a
  hardcoded stub today; wiring it to a real per-document warning count is a
  natural follow-up, not covered here.
- `INTERFACE_PARAMETER`'s `Type` field and its type-specific fields (for
  example `Min`/`Max` for a numeric type) are not fully pinned down; this
  task's extraction only needs the variable's name and declared `Type`, not
  a complete field schema, so that schema is left open for now.
