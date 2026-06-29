# Introduce Feature abstraction

## Status: implemented and verified (2026-07-12)

See "Implementation status: done" note at the end of the HOW section for
what was built and the deviations discovered along the way.

## WHY

[[20260711_1_format_abstraction]] introduced `Format`, the top-level
abstraction for everything that reads/writes document *content*
(sdoc/markdown/reqif/rst/spdx/excel/html/html2pdf/doxygen/json). That task's
WHY section named a second, orthogonal need and explicitly left it out of
scope:

> StrictDoc users need write their own custom generators or features for
> `export`, `import`, or other commands. This second type of feature is
> related to, but mostly orthogonal to, the `Format` feature.

Today, everything that isn't a `Format` — search, MathJax, Mermaid, Nestor,
Doxygen, project statistics, tree map, requirement
traceability/deep-traceability, traceability matrix, diff & changelog,
source file view, source coverage, project index, launcher — lives under
`strictdoc/features/*` but has no shared abstraction. Each is wired ad hoc:

- Enabled/disabled via the flat `ProjectFeature` string enum and
  `project_features=[...]` in the project config, checked through a
  matching `ProjectConfig.is_activated_*()` method
  (`strictdoc/core/project_config.py:781-832`).
- Hooked into `export`/`server` by hand at each call site (e.g.
  `strictdoc/server/routers/main_router.py` hardcodes routes per feature,
  mirroring how `EXPORT_FORMATS` was a hardcoded list before `Format`
  existed).

This means a user cannot add their *own* feature (e.g. a custom project
report, a custom server screen, a custom derived export artifact) without
patching StrictDoc's own source. `Format` solved this for content
conversion; `Feature` should solve it for everything else that plugs into
`export` and `server`.

## WHAT

Introduce a new `Feature` abstraction (Python abstract class), analogous to
`Format`, as a facade for cross-cutting capabilities that are *not*
document-content conversion:

- Bundle the typical actions a feature performs against the `export` and
  `server` commands behind one interface (exact methods: see HOW/open
  questions below).
- Let users register their own `Feature` subclasses via the project config,
  the same way custom `Format` subclasses are registered
  (`formats=[*ProjectConfig.default_formats(), CustomFormat()]`) — see
  "Config wiring" below for the exact shape.
- Use `ProjectStatistics` as the first real `Feature`, migrated off the
  `ProjectFeature.PROJECT_STATISTICS_SCREEN` ad hoc wiring. It is a good
  proof of concept because it already exercises every touchpoint this
  task cares about: a server screen/route
  (`project_statistics.html`, handled inline in
  `strictdoc/server/routers/main_router.py:4688-4699`), a nav-bar icon
  (`icons/ico16_stat.svg`, included in
  `strictdoc/export/html/templates/_shared/nav.jinja.html:15-24`), and an
  export-side generator
  (`strictdoc/features/project_statistics/generator.py`).
  (Note: an earlier draft of this task used Doxygen as the PoC feature;
  superseded by this decision. Doxygen reclassification, if still wanted,
  is left for a later task.)

### Explicitly out of scope for this task

Agreed with the user before drafting this task (see "Decisions already
made" below): this task is abstraction + one real proof-of-concept
(`ProjectStatistics`), not a wholesale migration.

- Migrating the other existing features (search, MathJax, Mermaid, Nestor,
  Doxygen, tree map, trace/deep-trace, traceability matrix,
  diff & changelog, source file view, source coverage, project index,
  launcher) onto the new `Feature` class. Left for follow-up task(s),
  mirroring how the `Format` work was split into
  `20260711_1_format_abstraction` / `20260711_2_connect_import_to_formats`
  / `20260711_3_convert_command_replaces_import`.
- Replacing the `ProjectFeature` enum / `project_features=[...]` /
  `is_activated_*()` toggle mechanism. `Feature` is additive: built-in
  screens keep using the enum exactly as today. `Feature` is for
  export/server contributions, especially custom user-defined ones, that
  have no enum-backed toggle today (a custom `Feature` is simply present or
  absent from the registered list — there is no separate on/off flag to
  design).
- Doxygen reclassification from `Format` to `Feature`. Superseded by using
  `ProjectStatistics` as the PoC instead (see WHAT above); left for a
  later task if still wanted.

## Decisions already made (discussed with the user before drafting HOW)

- **Scope**: abstraction + `ProjectStatistics` as the one real
  proof-of-concept feature. Not a full migration of every
  `strictdoc/features/*` entry.
- **Relationship to `ProjectFeature` enum**: coexist, not replace, but the
  enum *values* become the canonical `Feature` handles (see "Handles"
  below) — so migrating a feature means its existing enum member starts
  being backed by a `Feature` class, without renaming anything a project
  config already references by string.
- **PoC feature**: `ProjectStatistics` moves off the ad hoc
  `ProjectFeature.PROJECT_STATISTICS_SCREEN` wiring in
  `strictdoc/core/project_config.py` /
  `strictdoc/server/routers/main_router.py` /
  `strictdoc/export/html/templates/_shared/nav.jinja.html` onto the new
  `Feature` class.
- **Touchpoints covered by the abstract interface**: both `export` and
  `server` (matching the two commands named by the user), not just one.
- **Handles**: each `Feature` class carries its own handle as a class
  attribute, reusing the existing `ProjectFeature` enum value string
  verbatim — e.g. `ProjectStatisticsFeature.HANDLE = "PROJECT_STATISTICS_SCREEN"`,
  matching `Format.handles()`'s role but as a single string, not a list
  (a `Feature`, unlike a `Format`, doesn't need to answer to multiple
  handles/aliases).
- **`project_features` config type**: widens from `List[str]` to
  `List[Union[str, Feature]]`. A project config can list a feature either
  by its handle string (built-ins, exactly as today —
  `project_features=["PROJECT_STATISTICS_SCREEN", ...]` keeps working
  unchanged) or by passing a `Feature` instance directly (required for
  custom user-defined features, which have no built-in enum member to
  reference by string). `ProjectConfig` resolves the list into
  `Feature` instances internally (built-in string handles look up a
  built-in `Feature` instance; a passed instance is used as-is).
- **Server routes**: each `Feature` contributes routes to the server, but
  the route handlers themselves must live in a separate module that the
  `Feature` class imports and wires up — not written inline on the
  `Feature` class — to keep the `Feature` class itself as a thin facade/
  registration point rather than a dumping ground for route logic. E.g.
  `strictdoc/features/project_statistics/feature.py` (the `Feature`
  class) imports from
  `strictdoc/features/project_statistics/routes.py` (the actual
  `@router.get(...)` handlers, extracted out of the
  `project_statistics.html` branch currently inline in
  `main_router.py:4688-4699`).
- **Icon**: each `Feature` class also owns its left-sidebar nav icon
  (today: raw `{% include "icons/ico16_stat.svg" %}` partials hardcoded
  per feature in `nav.jinja.html:15-24`). Exact representation (icon
  file path vs. inline SVG string vs. Jinja partial name) is an open
  question below, but ownership is decided: the icon is a `Feature`
  attribute/method, not something `nav.jinja.html` hardcodes per feature
  going forward.

## HOW

All open questions from earlier drafts are now resolved (discussed with
the user). This section is the settled design; implementation may still
surface small deviations (as the `Format` task's own "Implementation
status" notes did), to be recorded here when that happens.

### The abstract interface

```py
class FeatureContext:
    project_config: "ProjectConfig"
    traceability_index: "TraceabilityIndex"
    html_templates: "HTMLTemplates"


class Feature(ABC):
    HANDLE: str  # e.g. "PROJECT_STATISTICS_SCREEN" -- reuses the existing
                 # ProjectFeature enum value string verbatim, so string-based
                 # project_features=[...] entries keep resolving unchanged.

    @staticmethod
    @abstractmethod
    def supports_export() -> bool: ...

    def export(self, context: FeatureContext) -> None:
        """Only called if supports_export() is True."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def supports_server() -> bool: ...

    def screen_filename(self) -> str:
        """
        Only called if supports_server() is True. The
        document_relative_path.relative_path value (e.g.
        "project_statistics.html") this Feature's screen owns, used as the
        dispatch key inside main_router.py's generate_document(). See "Server
        touchpoint" below for why this isn't a raw FastAPI route.
        """
        raise NotImplementedError

    def render_screen(self, context: FeatureContext) -> None:
        """
        Only called if supports_server() is True. Must write the screen's
        HTML file to context.project_config.export_output_html_root, the
        same contract every generate_document() branch already follows.
        Implementations delegate the actual generation logic to a sibling
        module (e.g. screen.py) imported here -- generation logic itself
        must not be written inline on the Feature class.
        """
        raise NotImplementedError

    def screen_icon(self) -> str:
        """
        Jinja template path for the nav icon, rendered via
        `{% include feature.screen_icon() %}`, e.g.
        "features/project_statistics/ico16_stat.svg". See "Icon" below.
        """
        raise NotImplementedError
```

- **`FeatureContext`** is a new, separate struct from `Format`'s
  `ExportContext` (`strictdoc/core/format.py`) — deliberately not reused.
  It carries only what `ProjectStatistics` (today's sole real example)
  actually needs: `project_config`, `traceability_index`,
  `html_templates`. It excludes `ExportContext`'s `parallelizer` and
  format-specific `bundle_*` fields (`bundle_traceability_index`,
  `bundle_document`, both HTML2PDF-only) since no Feature touches them
  today; extend `FeatureContext` later if a future Feature needs more,
  rather than pre-adding unused fields now.
- **Handles**: single string per `Feature` (`HANDLE`), not a list like
  `Format.handles()` — a `Feature`, unlike a `Format`, doesn't need to
  answer to multiple aliases.
- **Icon — renamed and settled through several rounds of revision
  (2026-07-12)**: `icon()` renamed to `screen_icon() -> str`, kept as a
  Jinja template path rendered via `{% include feature.screen_icon() %}`
  (not raw markup — an earlier revision tried a raw-markup/`| safe`
  approach to solve the custom-Feature question below, but was reverted:
  it's unnecessary churn for the one built-in case this task actually
  needs, and a real solution for genuinely external custom Features is
  deferred, see below).

  The path is resolved against the existing static `HTML_TEMPLATE_DIRS`
  list (`strictdoc/core/environment.py`) — the same mechanism every
  built-in feature's own `.jinja` templates already rely on (each feature
  gets a `"<feature>/templates"` entry there;
  `strictdoc/features/project_statistics/templates` was already
  registered before this task). `ProjectStatisticsFeature.screen_icon()`
  returns `"features/project_statistics/ico16_stat.svg"`, and the icon
  file itself was moved to live right next to that feature's own
  templates:
  `strictdoc/features/project_statistics/templates/features/project_statistics/ico16_stat.svg`
  (alongside its existing `main.jinja`/`index.jinja`, matching that
  directory's established `templates/features/<feature>/` nesting
  convention) — moved there from the old shared
  `strictdoc/export/html/templates/icons/` directory, feature-local per
  `AGENTS.md`'s "prefer feature-local templates" guidance. No change to
  `HTML_TEMPLATE_DIRS` or `HTMLTemplates`/Jinja loader setup was needed —
  two earlier attempts at solving this more generically (an `assets/`
  directory added as a new `HTML_TEMPLATE_DIRS` entry; a dynamic
  per-Feature search-path mechanism built into
  `strictdoc/export/html/html_templates.py`) were both reverted as
  unnecessary once it was clear the already-existing `templates` entry
  covered this feature's needs exactly.

  **Left open**: how a genuinely custom Feature (defined outside
  strictdoc's own package, e.g. in a user's project config, with no entry
  in `HTML_TEMPLATE_DIRS`) would supply its own icon. `{% include %}`
  only resolves paths through the search roots in that static list, so a
  custom Feature has no way to extend it today. The user's plan (stated
  during this task) is a **second API method** returning raw markup
  directly (inline `<svg>`, or an `<img src="data:...">` data URI for a
  raster image) for exactly this case — deferred to a later task, not
  implemented here.
- `nav.jinja.html` is updated at least for the `ProjectStatistics` entry,
  replacing its hardcoded `{% include "icons/ico16_stat.svg" %}` with
  `{% include project_statistics_feature.screen_icon() %}`; the other
  still-unmigrated features' blocks stay as they are (still gated by
  `is_activated_*()`, still hardcoded icon includes) until their own
  future migration.

### Config wiring

- `ProjectConfig.project_features` widens from `List[str]` to
  `List[Union[str, Feature]]`. Built-in string handles (exactly as today,
  e.g. `"PROJECT_STATISTICS_SCREEN"`) resolve to a built-in `Feature`
  instance; a `Feature` instance passed directly is used as-is. This is
  the only way to register a custom Feature, since custom features have
  no `ProjectFeature` enum member to reference by string.
- `ProjectConfig` resolves `project_features` into a list of `Feature`
  instances internally (mirroring `ProjectConfig.formats` /
  `default_formats()`), exposed as e.g.
  `ProjectConfig.get_features() -> List[Feature]`.
- No new CLI flag. Activation stays purely project-config-driven via
  `project_features=[...]`, unlike `Format`'s `--formats`, which needed
  the two-pass-parse trick because it's a CLI argument in the first
  place — `project_features` never has been.

### Export orchestration

`ExportAction.export()` (`strictdoc/features/export/export_action.py`)
runs its existing `Format` loop, then also iterates
`project_config.get_features()` and calls `.export()` on each
`Feature` where `supports_export()` is `True`, building a
`FeatureContext` from the same `TraceabilityIndex`/`HTMLTemplates`
already in hand at that point. No separate `FeatureAction` orchestrator.

### Server touchpoint: screen-filename dispatch, not raw route registration

**Revised during implementation (2026-07-12), before any code was
written**: `project_statistics.html` is not its own FastAPI route. All
HTML screens (index, traceability_matrix, tree_map, source_coverage,
project_statistics, regular documents) are served by one generic route,
`get_document()` (`main_router.py:4572`), which owns file-mtime caching,
ETag/304 handling, and read/write locking shared by every screen. The
per-screen `if/elif` chain inside its nested `generate_document()`
(`main_router.py:4633+`) only decides which generator populates the file
before that shared machinery serves it. A `register_routes(router, ...)`
hook that adds a standalone new FastAPI route — the original plan — would
silently drop `project_statistics.html` out of that shared cache/lock
wrapper: a real behavior regression, not a neutral refactor. Confirmed
with the user; the design below replaces `register_routes()`.

The correct seam mirrors how the `Format` task fixed `DocumentFinder`:
replace the hardcoded `if/elif` with a lookup driven by registered
`Feature`s, without touching the shared caching/locking wrapper around it.

- `Feature` interface changes: `register_routes()` is replaced by
  `screen_filename() -> str` (e.g. `"project_statistics.html"`, the
  `document_relative_path.relative_path` value this feature owns) and
  `render_screen(self, context: FeatureContext) -> None` (equivalent to
  today's `html_generator.export_project_statistics(...)` call — it must
  write the HTML file to `project_config.export_output_html_root`, same
  contract every branch in `generate_document()` already follows, so the
  surrounding must-generate/cache/lock logic keeps working unmodified).
- `strictdoc/features/project_statistics/screen.py` (new): the actual
  screen-generation logic, extracted out of the
  `elif document_relative_path.relative_path == "project_statistics.html"`
  branch currently inline in `main_router.py:4688-4699`. This is the
  "separate file the feature imports" the user asked for — accurately
  named for what it does (screen generation), since there is no literal
  route handler to extract.
- `strictdoc/features/project_statistics/feature.py` (new):
  `ProjectStatisticsFeature(Feature)`, `HANDLE =
  "PROJECT_STATISTICS_SCREEN"`, `supports_export() == True`,
  `supports_server() == True`, `screen_filename()` returns
  `"project_statistics.html"`, `screen_icon()` returns
  `"features/project_statistics/ico16_stat.svg"` (a Jinja template path,
  resolved via the feature's own already-registered `HTML_TEMPLATE_DIRS`
  entry). `render_screen()` imports and calls into `screen.py`.
- `main_router.py`'s `generate_document()` builds a
  `{screen_filename(): feature_}` dict from
  `project_config.get_features()` (features where `supports_server()` is
  `True`) once per request (or hoisted outside if cheap enough), and the
  `if/elif` chain gains one generic branch: if
  `document_relative_path.relative_path` is a key in that dict, call
  `feature_.render_screen(context)`. The existing
  `project_statistics.html` `elif` branch (including its
  `is_activated_project_statistics()` precondition check) is deleted,
  since the new mechanism now serves that URL — the precondition check
  moves into the dict-building step (only activated features populate
  the dict, so an unactivated `project_statistics.html` request falls
  through to the generic "not a real document" handling that already
  exists for arbitrary unknown paths).
- `ProjectConfig.is_activated_project_statistics()` stays (per "coexist,
  not replace" decision) but is reimplemented in terms of
  `get_features()` membership rather than the raw `ProjectFeature` enum
  check, so it keeps working for any code (templates, other checks) that
  still calls it.
- `nav.jinja.html` is updated per "Icon" above, at least for the
  `ProjectStatistics` entry.

### Scope confirmation

This validates the full interface (export + server + icon + config
resolution) against one real, currently-working feature, end to end —
same rigor as how the `Format` task proved its abstraction by fully
extracting `HTMLGenerator`/`ReqIFExport`/etc. rather than just defining
`Format` on paper. All other `strictdoc/features/*` entries remain
unmigrated (see "Explicitly out of scope") until follow-up tasks.

#### Implementation status: done

Built as designed above, with one deviation and one minor, deliberate
behavior widening, both discovered during implementation:

- **Export trigger condition**: initially implemented as `html_templates
  is not None` (matching `ExportAction`'s existing `needs_html_templates`
  condition, true for either `"html"` or `"html2pdf"`), which widened
  behavior slightly versus pre-migration (project statistics was
  previously only ever generated from inside `HTMLGenerator.export()`,
  i.e. only for `"html"` specifically, never an `html2pdf`-only export).
  Caught after initial verification and corrected per the user's request
  to preserve exact prior behavior: the condition is now `"html" in
  requested_handles` specifically (with `assert html_templates is not
  None` immediately under it, since that's implied whenever `"html"` is
  requested). No behavior change from pre-migration.
- **`HTMLGenerator.export_project_statistics()` removed**, not kept as a
  delegating wrapper. It had no callers left once both the `ExportAction`
  and `main_router.py` call sites were migrated to the `Feature`
  mechanism, and it wasn't part of the public `strictdoc.api.*` surface or
  referenced by any test — confirmed via repo-wide grep before deletion.

Files added: `strictdoc/core/feature.py` (`Feature`, `FeatureContext`),
`strictdoc/features/project_statistics/screen.py`
(`render_project_statistics_screen()`, the extracted generation logic),
`strictdoc/features/project_statistics/feature.py`
(`ProjectStatisticsFeature`).

Files changed: `strictdoc/core/project_config.py` (`project_features`
widened to `List[Union[str, Feature]]`, `get_features()`/`get_feature()`/
`_builtin_features_by_handle()` added, `is_activated_project_statistics()`
reimplemented), `strictdoc/features/export/export_action.py` (Feature
export loop), `strictdoc/server/routers/main_router.py`
(`server_features_by_screen_filename` dict + generic dispatch branch,
replacing the hardcoded `project_statistics.html` `elif`),
`strictdoc/export/html/html_generator.py` (nested project-statistics call
and now-dead `export_project_statistics()` method removed),
`strictdoc/export/html/templates/_shared/nav.jinja.html` (icon rendered
via `{% include project_config.get_feature("PROJECT_STATISTICS_SCREEN").screen_icon() %}`
instead of a hardcoded literal include path). Icon asset moved:
`strictdoc/export/html/templates/icons/ico16_stat.svg` →
`strictdoc/features/project_statistics/templates/features/project_statistics/ico16_stat.svg`
(feature-local, alongside that feature's existing `main.jinja`/
`index.jinja`, resolved via the already-registered
`"project_statistics/templates"` `HTML_TEMPLATE_DIRS` entry — no new
entry or loader changes needed).

Verified: full unit suite (634 passed), `ruff`/`ruff format`/`mypy --strict`
all clean, `project_statistics` integration tests (6 passed), `commands/export`
smoke tests against StrictDoc's own docs (which activate
`PROJECT_STATISTICS_SCREEN` in `strictdoc_config.py`), `html2pdf`
integration suite (14 passed, 1 pre-existing unsupported), and end-to-end
browser tests for `project_statistics` plus adjacent nav/project-tree
screens (4 passed) — all green.
