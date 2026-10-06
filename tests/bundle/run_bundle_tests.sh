#!/usr/bin/env bash
#
# Verify a frozen (PyInstaller) StrictDoc bundle.
#
# Usage:
#   tests/bundle/run_bundle_tests.sh PATH_TO_STRICTDOC_EXE [smoke|full|lit|all] [pytest args...]
#
#   smoke  fast CI subset (pytest -m smoke): version/help, html export,
#          excel import + content check + re-export, html2pdf (if Chrome),
#          server boot + headless-browser crawl with one form.        ~2-3 min
#   full   every BT-* test in tests/bundle/test_bundle.py (all CLI commands,
#          every export format, reqif/excel round-trips, full server crawl
#          with forms, html2pdf offline/no-chrome cases, bundle checks).
#   lit    upstream integration suite (tests/integration, 550+ tests) with
#          %strictdoc = the bundle, plus the html2pdf lit suite.
#   all    full + lit
#
# Requirements on the test machine (NOT needed by the bundle itself):
#   python3 with: pytest playwright openpyxl pypdf   (+ `playwright install chromium`)
#   lit tier additionally: lit==18.1.8 filecheck   (uv group "check" has all)
#   optional: poppler-utils (pdftotext), Google Chrome (html2pdf), git, unshare
#
# Environment:
#   BUNDLE_TEST_PYTHON        python to run pytest/lit (default: python3/python)
#   BUNDLE_TEST_RESULTS       results dir (default: build/bundle_test_results)
#   BUNDLE_TEST_SKIP_PDF=1    skip html2pdf tests
#   BUNDLE_TEST_MAX_PAGES     full crawl page budget (default 250)
#   STRICTDOC_EXEC            instead of a bundle path, run a baseline command
#                             (e.g. "python -m strictdoc.cli.main") with "-"
#                             as the bundle argument, to classify failures.
set -uo pipefail

if [ $# -lt 1 ]; then sed -n '2,32p' "$0"; exit 2; fi
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
BUNDLE="$1"; shift
TIER="${1:-smoke}"; [ $# -gt 0 ] && shift
PY="${BUNDLE_TEST_PYTHON:-$(command -v python3 || command -v python)}"
RESULTS="${BUNDLE_TEST_RESULTS:-$ROOT/build/bundle_test_results}"
mkdir -p "$RESULTS"
export BUNDLE_TEST_RESULTS="$RESULTS"

if [ "$BUNDLE" != "-" ]; then
  BUNDLE="$(cd "$(dirname "$BUNDLE")" && pwd)/$(basename "$BUNDLE")"
  [ -f "$BUNDLE" ] || { echo "error: no such executable: $BUNDLE" >&2; exit 2; }
  export STRICTDOC_BUNDLE="$BUNDLE"
  unset STRICTDOC_EXEC
  EXEC_FOR_LIT="$BUNDLE"
else
  [ -n "${STRICTDOC_EXEC:-}" ] || { echo "error: '-' needs STRICTDOC_EXEC" >&2; exit 2; }
  EXEC_FOR_LIT="$STRICTDOC_EXEC"
fi

echo "bundle under test: ${STRICTDOC_BUNDLE:-$STRICTDOC_EXEC}"
echo "tier: $TIER    results: $RESULTS"

rc=0
run_pytest() {
  local name="$1"; shift
  (cd "$HERE" && "$PY" -m pytest -c "$HERE/pytest.ini" --rootdir "$HERE" \
     --junitxml "$RESULTS/$name.junit.xml" -rA -v "$@" "$HERE/test_bundle.py") \
     2>&1 | tee "$RESULTS/$name.log"
  local r=${PIPESTATUS[0]}; [ "$r" -ne 0 ] && rc=1
}

run_lit() {
  # PATH without any venv: a stray `html2pdf4doc` console script would hide
  # bundle bugs (that is exactly how upstream CI misses them).
  local tools="$RESULTS/lit-tools"; mkdir -p "$tools"
  for t in python python3; do
    printf '#!/bin/sh\nexec "%s" "$@"\n' "$PY" > "$tools/$t"; chmod +x "$tools/$t"
  done
  local VBIN; VBIN="$("$PY" -c 'import sys,os; print(os.path.dirname(sys.executable))')"
  # Test helper tools (lit, filecheck, reqif, pytest, gcovr, ...) but never
  # html2pdf4doc: the bundle must not depend on it.
  for f in "$VBIN"/*; do
    b="$(basename "$f")"
    case "$b" in html2pdf4doc*|python*|activate*|*.fish|*.csh|*.ps1|*.bat) continue ;; esac
    ln -sf "$f" "$tools/$b"
  done
  local LIT="$tools/lit"
  local tmpd="$RESULTS/lit-tmp"; rm -rf "$tmpd"; mkdir -p "$tmpd"
  (cd "$ROOT" && PATH="$tools:/usr/local/bin:/usr/bin:/bin" "$LIT" \
     --param STRICTDOC_EXEC="$EXEC_FOR_LIT" --param STRICTDOC_TMP_DIR="$tmpd" \
     --param TEST_OUTPUT_DIR="build/bundle_lit" --timeout 180 --order smart \
     --xunit-xml-output "$RESULTS/lit.junit.xml" -v "$ROOT/tests/integration") \
     > "$RESULTS/lit.log" 2>&1 || rc=1
  tail -8 "$RESULTS/lit.log"
  if [ "${BUNDLE_TEST_SKIP_PDF:-0}" != 1 ]; then
    (cd "$ROOT" && PATH="$tools:/usr/local/bin:/usr/bin:/bin" "$LIT" \
       --param STRICTDOC_EXEC="$EXEC_FOR_LIT" --param STRICTDOC_TMP_DIR="$tmpd" \
       --param TEST_OUTPUT_DIR="build/bundle_lit_html2pdf" --param TEST_HTML2PDF=1 \
       --threads 1 --timeout 300 --xunit-xml-output "$RESULTS/lit_html2pdf.junit.xml" -v \
       "$ROOT/tests/integration/features/html2pdf" "$ROOT/tests/integration/features/_integration_") \
       > "$RESULTS/lit_html2pdf.log" 2>&1 || rc=1
    tail -8 "$RESULTS/lit_html2pdf.log"
  fi
}

case "$TIER" in
  smoke) run_pytest smoke -m smoke "$@" ;;
  full)  run_pytest full "$@" ;;
  lit)   run_lit ;;
  all)   run_pytest full "$@"; run_lit ;;
  *) echo "unknown tier: $TIER" >&2; exit 2 ;;
esac
"$PY" "$HERE/summarize_results.py" "$RESULTS" || true
exit $rc
