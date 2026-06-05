# Regenerating the cargo-nextest JUnit XML fixtures

Each `NN_*` directory here is a **self-contained Cargo project** (a single
crate, or a workspace) as well as a StrictDoc fixture: its Rust sources are the
source under test, and `reports/tests_unit.nextest.junit.xml` is the JUnit
report that cargo-nextest produces for it. Both the report (for fast test runs)
and the setup that produces it (for reproducibility) are committed on purpose,
so that the fixtures can be trusted *and* regenerated when a new cargo-nextest
version changes the JUnit layout. `04_module_layouts` and `05_workspace` cover
the non-trivial test module layouts (nested modules, integration-test
submodules, same-stem files, and same-named tests across workspace crates).

## How to regenerate

From this directory, with [cargo-nextest](https://nexte.st) installed:

```sh
./regenerate.sh
```

For each crate it runs `cargo nextest run --profile ci` (the `ci` profile in
each crate's `.config/nextest.toml` enables the JUnit reporter), then copies
`target/nextest/ci/junit.xml` into `reports/` and normalizes the run-specific
fields so the committed fixtures are deterministic:

| Field | Normalized to | Why |
|-------|---------------|-----|
| `uuid` | all-zeros | new per run |
| `timestamp` | `2025-03-10T10:30:39+00:00` | wall-clock time |
| `time` | `0.000` | measured duration |
| panic thread-id `(NNNN)` | removed | thread id varies per run |

Everything else — `<testsuite>`/`<testcase>` structure, `<failure>` bodies,
`<system-out>`/`<system-err>` — is verbatim cargo-nextest output. The crate in
`02_failed_test` is expected to fail; the script tolerates the non-zero exit.

## `_generator/`

`_generator/` is not a StrictDoc fixture — it is the documented source for the
inline cargo-nextest XML used by the unit tests in
`tests/unit/.../test_junit_xml_reader_nextest.py`. It is a single `my_crate`
that, in one run, exercises every shape those tests rely on: a passing test, a
failing test, a nested-module test (`tests::nested::nested_module_test`), and
an integration-test binary (`classname` with `::`), and therefore emits
multiple `<testsuite>`s in one report. `regenerate.sh` writes its normalized
output to `_generator/reports/junit.xml`; the unit-test snippets are minimal
single-scenario slices of that file.

These fixtures were last regenerated with cargo-nextest 0.9.137.
