# Test execution dashboard

## WHAT

A custom `Feature` (built on `strictdoc/core/feature.py`) that walks every
`TEST_CASE` node in the project, tallies the `STATUS` field, and renders a
screen showing counts by status (Not Executed, Blocked, Failed, Passed) plus
an overall pass rate. The screen shall be extendable: adding a new number
(for example, a per-`TARGET_REVISION` breakdown once
`20260827_release_versioning` lands) should only require adding to the
feature, not restructuring it.

## WHY

None of the built-in screens answer "how many tests passed" directly.
`ProjectStatistics` reports document and section counts, not test outcomes;
`TraceabilityMatrix` shows links, not aggregate status; `TreeMap` is a
structural visualization. A dedicated dashboard is the one genuine build
task among the Eurobot asks, and `ProjectStatisticsFeature`
(`strictdoc/features/project_statistics/feature.py` and `screen.py`) is a
proven, already-shipped reference for this shape of feature: a server
screen, a nav icon, and an export-side generator, wired through `Feature`
rather than hardcoded into `main_router.py`.

## HOW

Structure: mirror `ProjectStatisticsFeature`'s split between `feature.py`
(the thin `Feature` subclass: `HANDLE`, `supports_export()`,
`supports_server()`, `screen_filename()`, `screen_icon()`) and `screen.py`
(the actual generation logic, called from `render_screen()`).

Data: iterate the traceability index for `TEST_CASE` nodes, read each one's
`STATUS` field, and tally into the four buckets. Reuse
`SDocDocumentIterator` the way `ProgressStatisticsGenerator` already does,
rather than writing a new tree walk.

Registration: add the new `HANDLE` (for example
`"EUROBOT_TEST_DASHBOARD"`) to the Eurobot project's `project_features`,
following the same `List[Union[str, Feature]]` mechanism `ProjectConfig`
already resolves.

Dependencies: needs `20260827_requirements_and_test_grammar`'s `STATUS`
field to exist. A per-revision breakdown (for example, "12 of 40 tests
passed for C1") additionally needs `20260827_release_versioning`'s
`TARGET_REVISION` field; build the plain status tally first and add the
revision breakdown once that field exists.

### Deferred work

Trend over time (pass rate across RCs) is not part of this task. It would
need reading the `STATUS` history out of past git tags (see
`20260827_release_versioning`'s diff-based recovery) rather than the live
tree, and is a separate, larger piece of work.
