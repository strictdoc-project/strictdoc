#!/usr/bin/env bash
#
# Smoke-test a StrictDoc bundle built by scripts/build_bundle.sh.
#
# Usage:
#   scripts/smoke_bundle.sh PATH_TO_STRICTDOC_EXECUTABLE
#
# The tests run the bundled executable only, from a scratch directory outside
# the repository, with fixtures copied from tests/integration:
#
#   1. version
#   2. export --formats html, then check the HTML pages and assets exist
#   3. server: fetch the index, every document page and their CSS/JS assets
#   4. export --formats html2pdf, then check the PDFs (needs Google Chrome)
#   5. convert --input-format=excel for .xls and .xlsx, diff the result, and
#      export the imported document to HTML
#   6. server on an Excel-converted project (custom grammar, large enough for
#      the server to precompile its Jinja templates): fetch the index, every
#      document view and their assets; then damage the compiled template
#      cache, restart, and fetch them again
#   7. (SMOKE_FULL=1) export StrictDoc's own documentation, which also covers
#      the project config, a custom statistics generator, tree map, and
#      source file traceability
#
# Environment variables:
#   SMOKE_WORKDIR    Scratch directory (default: a new temp directory).
#   SMOKE_PORT       Server port (default: 8099).
#   SMOKE_SKIP_PDF   "1" skips the html2pdf test (e.g. without Chrome).
#   SMOKE_FULL       "1" also runs test 7.
#
# Works on Linux, macOS and Windows (Git Bash).

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 PATH_TO_STRICTDOC_EXECUTABLE" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
PORT="${SMOKE_PORT:-8099}"
WORK="${SMOKE_WORKDIR:-$(mktemp -d "${TMPDIR:-/tmp}/strictdoc-smoke.XXXXXX")}"
mkdir -p "$WORK"
cd "$WORK"

FIXTURES="$ROOT/tests/integration/features"
PASSED=()

log() { printf '\n==> %s\n' "$*"; }
fail() { echo "SMOKE FAIL: $*" >&2; exit 1; }
pass() { echo "ok: $*"; PASSED+=("$*"); }
need_file() { [ -s "$1" ] || fail "missing or empty: $1"; }

log "Bundle: $EXE"
log "Workdir: $WORK"

# A clean copy of a small project: three documents in nested folders and a
# strictdoc_config.py that imports StrictDoc's own API (which must therefore
# be importable from the bundle).
rm -rf project
cp -R "$FIXTURES/html2pdf/02_three_top_level_requirements" project

#
# 1. Version.
#
log "1. version"
"$EXE" version
pass "version"

#
# 2. HTML export.
#
log "2. export --formats html"
rm -rf out-html
"$EXE" export project --formats html --output-dir out-html
need_file out-html/html/index.html
need_file out-html/html/project/input.html
need_file out-html/html/project/nested/input2.html
need_file out-html/html/project/nested/subnested/input3.html
for asset in base.css layout.css app_core.js favicon.ico \
  html2pdf4doc.min.js mermaid/mermaid.min.js; do
  need_file "out-html/html/_static/$asset"
done
# Every _static asset referenced by the exported index page must exist.
grep -o '_static/[^"?#]*' out-html/html/index.html | sort -u | while read -r ref; do
  need_file "out-html/html/$ref"
done
pass "export html"

#
# 3. Server.
#
log "3. server"
SERVER_LOG="$WORK/server.log"
SERVER_PID=
BASE="http://127.0.0.1:$PORT"

start_server() {
  # start_server PROJECT_DIR: start the server from the current directory
  # (its output and cache go to ./output/server) and wait until it answers.
  "$EXE" server "$1" --port "$PORT" >"$SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  trap stop_server EXIT
  local up=0
  for _ in $(seq 1 120); do
    if curl -fsS -o /dev/null "$BASE/_static/base.css" 2>/dev/null; then up=1; break; fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then break; fi
    sleep 1
  done
  if [ "$up" != 1 ]; then
    cat "$SERVER_LOG" >&2
    fail "server did not start"
  fi
}
stop_server() {
  if [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
    SERVER_PID=
  fi
  trap - EXIT
}

fetch() {
  # fetch PATH OUTFILE: GET $BASE/PATH and require HTTP 200.
  local code
  code="$(curl -sS -o "$2" -w '%{http_code}' "$BASE/$1")" || code="curl-error"
  [ "$code" = 200 ] || { cat "$SERVER_LOG" >&2; fail "GET /$1 -> $code"; }
  echo "200 /$1"
}

check_server_log() {
  # Template and import errors may not turn into an HTTP error.
  if grep -E "Traceback|ModuleNotFoundError|TemplateNotFound" "$SERVER_LOG" >/dev/null; then
    cat "$SERVER_LOG" >&2
    fail "server log has errors ($1)"
  fi
}

start_server project

fetch "" index.html
grep -q "project/input.html" index.html || fail "index lists no documents"
pages=(project/input.html project/nested/input2.html project/nested/subnested/input3.html)
for page in "${pages[@]}"; do
  fetch "$page" page.html
  grep -q "_static/" page.html || fail "$page has no static asset links"
  grep -o '_static/[^"?#]*' page.html >>assets.txt
done
grep -o '_static/[^"?#]*' index.html >>assets.txt
n_assets=0
for asset in $(sort -u assets.txt); do
  fetch "$asset" asset.bin
  n_assets=$((n_assets + 1))
done
[ "$n_assets" -ge 10 ] || fail "expected at least 10 assets, got $n_assets"
# Binary assets: an icon and a font.
fetch "_static/favicon.ico" asset.bin
fetch "_static/fonts/NotoSans-VariableFont_wdth,wght.ttf" asset.bin
check_server_log "server"
stop_server
pass "server (3 pages, $n_assets assets)"

#
# 4. HTML2PDF.
#
if [ "${SMOKE_SKIP_PDF:-0}" = 1 ]; then
  log "4. export --formats html2pdf: SKIPPED (SMOKE_SKIP_PDF=1)"
else
  log "4. export --formats html2pdf"
  rm -rf out-pdf
  "$EXE" export project --formats html2pdf --output-dir out-pdf
  for pdf in input.pdf nested/input2.pdf nested/subnested/input3.pdf; do
    f="out-pdf/html2pdf/pdf/$pdf"
    need_file "$f"
    [ "$(head -c 4 "$f")" = "%PDF" ] || fail "$f is not a PDF"
  done
  pass "export html2pdf"
fi

#
# 5. Excel import.
#
log "5. convert --input-format=excel"
EXCEL="$FIXTURES/excel/import/01_import_basic_e2e"
rm -rf out-xls out-xlsx
"$EXE" convert "$EXCEL/input.xls" out-xls/ --input-format=excel
diff --strip-trailing-cr out-xls/input.sdoc "$EXCEL/expected/expected.sdoc"
"$EXE" convert "$EXCEL/input.xlsx" out-xlsx/ --input-format=excel
diff --strip-trailing-cr out-xlsx/input.sdoc "$EXCEL/expected_xslx/expected.sdoc"
# The imported document (with a Parent relation from the PARENT column) must
# export, which is the point of importing it.
rm -rf out-xlsx-html
"$EXE" export out-xlsx --formats html --output-dir out-xlsx-html
grep -q "A-1" out-xlsx-html/html/out-xlsx/input.html \
  || fail "imported Excel document did not export"
pass "excel import (.xls, .xlsx) + export of the imported doc"


#
# 6. Server on an Excel-converted project.
#
# Two imported spreadsheets: one with a PARENT_UID column (so its grammar
# has a Parent relation) and a 50-row questionnaire with its own columns.
# Each becomes a document with a custom grammar. With more than 5 nodes in a
# document, StrictDoc counts the project as large and the server precompiles
# its Jinja templates into output/server/_cache/<version>/jinja/<hash>/ and
# imports them from there. The second half damages that cache the way an
# interrupted first run does (v0.30.1 then failed every page with
# ModuleNotFoundError: No module named '_jinja2_module_templates_...' and
# TemplateNotFound).
#
log "6. server on an Excel-converted project"
rm -rf srv-excel
mkdir srv-excel
(
  cd srv-excel
  "$EXE" convert "$EXCEL/input.xlsx" excel-project/ --input-format=excel
  "$EXE" convert \
    "$ROOT/tests/integration/examples/python_api/export_excel_questionnaire/expected/tsrm_questionnaires.xlsx" \
    excel-project/ --input-format=excel
  for sdoc in input tsrm_questionnaires; do
    need_file "excel-project/$sdoc.sdoc"
    grep -q "^\[GRAMMAR\]" "excel-project/$sdoc.sdoc" \
      || fail "excel-project/$sdoc.sdoc has no custom grammar"
  done
)

excel_server_pass() {
  # excel_server_pass LABEL: fetch the index, every document view and
  # their assets from the running server.
  rm -f assets.txt
  fetch "" index.html
  local docs
  docs="$(grep -o 'href="excel-project/[^"#?]*\.html"' index.html \
    | sed 's/^href="//; s/"$//' | sort -u)"
  [ "$(echo "$docs" | wc -l)" -eq 2 ] || fail "index does not list both documents ($1)"
  local n_pages=0 doc base view
  for doc in $docs; do
    fetch "$doc" page.html
    grep -q -E "A-2|CM-020" page.html || fail "$doc shows no requirement ($1)"
    grep -o '_static/[^"?#]*' page.html >>assets.txt
    n_pages=$((n_pages + 1))
    base="${doc%.html}"
    # Other views of the document that the page links to (-TABLE, -TRACE,
    # -DEEP-TRACE, ...): fetch each one that is enabled.
    for view in $(grep -o "$(basename "$base")-[A-Z-]*\.html" page.html | sort -u); do
      fetch "$(dirname "$doc")/$view" view.html
      grep -o '_static/[^"?#]*' view.html >>assets.txt
      n_pages=$((n_pages + 1))
    done
  done
  for asset in $(sort -u assets.txt); do
    fetch "$asset" asset.bin
  done
  check_server_log "$1"
  echo "ok: $n_pages document views ($1)"
}

cd srv-excel
start_server excel-project
grep -q "Compile Jinja templates" "$SERVER_LOG" \
  || fail "the server did not precompile its templates; the test needs a larger project"
excel_server_pass "fresh template cache"
stop_server

# Damage the compiled template cache: delete every other compiled template.
compiled="$(find output/server/_cache -path '*/jinja/*' -name 'tmpl_*.py' | sort)"
[ -n "$compiled" ] || fail "no compiled templates under output/server/_cache"
echo "$compiled" | awk 'NR % 2 == 0' | while read -r f; do rm -f "$f"; done
start_server excel-project
excel_server_pass "damaged template cache"
stop_server
cd "$WORK"
pass "server on an Excel-converted project (fresh and damaged template cache)"

#
# 7. StrictDoc's own documentation.
#
if [ "${SMOKE_FULL:-0}" = 1 ]; then
  log "7. export StrictDoc's own documentation"
  rm -rf out-docs
  (cd "$ROOT" && "$EXE" export . --formats html --output-dir "$WORK/out-docs")
  need_file out-docs/html/index.html
  need_file out-docs/html/project_statistics.html
  need_file out-docs/html/tree_map.html
  pass "export StrictDoc docs"
fi

log "All smoke tests passed"
printf '  %s\n' "${PASSED[@]}"
