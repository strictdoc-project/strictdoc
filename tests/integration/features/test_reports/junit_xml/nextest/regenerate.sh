#!/usr/bin/env bash
#
# Regenerate the committed cargo-nextest JUnit XML fixtures from real
# cargo-nextest runs. See README.md for the rationale and the list of
# normalized (run-specific) fields.
#
set -euo pipefail
cd "$(dirname "$0")"

# Normalize the run-specific fields so the committed output is deterministic;
# everything else is verbatim cargo-nextest output.
normalize() {
    sed -E \
        -e 's/uuid="[^"]*"/uuid="00000000-0000-0000-0000-000000000000"/g' \
        -e 's/timestamp="[^"]*"/timestamp="2025-03-10T10:30:39+00:00"/g' \
        -e 's/ time="[^"]*"/ time="0.000"/g' \
        -e 's/(&apos;) \([0-9]+\) panicked/\1 panicked/g'
}

# Each crate gets a clean, crate-local target dir: the crates share package
# names (the committed `classname` depends on them), so a global
# CARGO_TARGET_DIR would let cargo reuse one crate's cached test binary for
# another. Some crates are meant to fail, so tolerate a non-zero exit.
regen() {
    dir=$1 out=$2
    echo "==> $dir"
    rm -rf "$dir/target"
    (cd "$dir" && CARGO_TARGET_DIR=target cargo nextest run --profile ci) || true
    normalize <"$dir/target/nextest/ci/junit.xml" >"$out"
    echo "    wrote $out"
}

# The strictdoc fixtures: each NN_* dir is both a Cargo crate and a fixture.
for dir in [0-9][0-9]_*/; do
    dir=${dir%/}
    regen "$dir" "$dir/reports/tests_unit.nextest.junit.xml"
done

# The _generator crate is the documented source for the inline XML used by the
# unit tests in test_junit_xml_reader_nextest.py (it covers the passing,
# failing, nested-module, integration-binary, and multi-suite shapes in one
# run). It is not a strictdoc fixture, so its output keeps the raw name.
regen "_generator" "_generator/reports/junit.xml"
