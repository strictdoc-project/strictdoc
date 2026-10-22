# Test plan: StrictDoc PyInstaller bundle

Owner: The Tester (QA). Build owner: The Dev (`feat/pyinstaller-bundle`).
Status: v1, 2026-10-05.

## 1. Purpose and scope

StrictDoc ships as a self-contained PyInstaller **onedir** bundle (`strictdoc[.exe]`
plus `_internal/`), so requirements engineers can use it without Python, a venv or pip.
This plan tests **the frozen executable only**. The pip package is used only as a
*baseline*, to decide whether a failure comes from the bundle or from upstream StrictDoc.

In scope:
- Every CLI command and subcommand in `strictdoc --help`: `about`, `convert`
  (Excel/ReqIF import), `export` (all formats), `format`, `manage assets|auto-uid|new`,
  `new`, `server`, `version`, `launcher`. Note: upstream 0.30.x has **no** `import`,
  `passthrough` or `diff` commands. Import is `convert`, and diff/changelog is
  `export --generate-diff-dirs/--generate-diff-git`.
- Every export format in `strictdoc/commands/export.py:EXPORT_FORMATS`: html, html2pdf,
  markdown, rst, json, excel, reqif-sdoc, reqifz-sdoc, sdoc, doxygen, spdx.
- Web server: page rendering, every static asset (JS/CSS/fonts/icons/images), Turbo-stream
  actions (edit/create forms), search, traceability screens, source-file views, server-side
  html2pdf and ReqIF export.
- Bundle-specific risks: missing data files (Jinja templates, `_static`, fonts, MathJax,
  Mermaid, PlantUML, html2pdf4doc JS, spdx/reqif/textX package data), hidden imports
  (uvicorn loads `strictdoc.server.app` by name, `strictdoc.api` used by user configs),
  `sys._MEIPASS` path handling, subprocess re-exec of `sys.executable` (html2pdf helper,
  multiprocessing workers, launcher), `multiprocessing.freeze_support`, writes into the bundle
  directory, dependence on a `PATH` venv (`html2pdf4doc` console script), relocation
  (copy to a path with spaces), stray `PYTHONHOME`/`PYTHONPATH`.

Out of scope: StrictDoc functional correctness beyond what its own test suite asserts,
macOS notarisation/code signing, Windows SmartScreen, performance benchmarking.

## 2. Test items and environment

| Item | Value |
|---|---|
| Bundle under test | path passed to the runner (default: `scripts/build_bundle.sh` output `dist/strictdoc-<ver>-<platform>/strictdoc`) |
| Test-side deps (not needed by the bundle) | Python 3.10+ with `pytest playwright openpyxl pypdf`, `playwright install chromium`; lit tier: uv group `check` (`lit==18.1.8`, `filecheck`, `reqif`, `gcovr`, `pytest`) |
| Optional | Google Chrome (html2pdf), poppler-utils (`pdftotext`, `pdfinfo`), git, `unshare` (offline tests, Linux) |
| Fixtures | StrictDoc's own: `docs/`, the repo root with `strictdoc_config.py`, `tests/integration/features/**` |
| Isolation | every bundle call runs with a cleaned environment: venv dirs, any PATH entry containing `html2pdf4doc`, and `PYTHON*`/`VIRTUAL_ENV` variables are removed |

## 3. Tiers

| Tier | Command | Runtime (Linux, 8 cores) | Purpose |
|---|---|---|---|
| smoke | `tests/bundle/run_bundle_tests.sh <exe> smoke` | ~40 s | CI gate on every bundle build (ubuntu/windows/macos) |
| full | `tests/bundle/run_bundle_tests.sh <exe> full` | ~10 min | Release candidate |
| lit | `tests/bundle/run_bundle_tests.sh <exe> lit` | ~6 min + 3 min html2pdf | Upstream integration suite (554 tests) with `%strictdoc` = the bundle |
| baseline | `STRICTDOC_EXEC="python -m strictdoc.cli.main" tests/bundle/run_bundle_tests.sh - full` | | Sorts failures into bundle bugs and upstream bugs |

## 4. Test cases

Pass criteria for every case: exit code 0 unless stated otherwise, no `Traceback`
in the output, expected files present and non-empty, and the bundle directory
unchanged (BT-BND-01).

### 4.1 CLI basics (BT-CLI)
| ID | Smoke | Test | Pass criteria |
|---|---|---|---|
| BT-CLI-01 | ✔ | `version`, `--version`, `-v` | prints `X.Y.Z` |
| BT-CLI-02a | ✔ | `--help` | lists export, server, convert, manage, version |
| BT-CLI-02b | | `<cmd> --help` for every top-level command and every `manage` subcommand | `usage:`, rc 0 |
| BT-CLI-03 | | `about` | mentions StrictDoc |
| BT-CLI-04 | | `new <dir>`, then `export` of that project | .sdoc created; index.html exported |
| BT-CLI-05 | | `export --formats nope` | rc ≠ 0, argparse error, no traceback |

### 4.2 Export (BT-EXP)
| ID | Smoke | Test | Pass criteria |
|---|---|---|---|
| BT-EXP-01 | ✔ | html export of a 3-document nested fixture | index and document pages exist; every local `href/src` asset (css/js/svg/ico/png/fonts) referenced by those pages exists on disk; requirement text present |
| BT-EXP-01b | | html export of `docs/` with `--no-parallelization` | user guide page and its assets exist |
| BT-EXP-02[fmt] | | markdown, rst, json, excel, reqif-sdoc, reqifz-sdoc, sdoc, doxygen, spdx | output files of the expected type exist and parse (JSON, XML, zip, xlsx with ≥1 data row; text formats contain requirement text) |
| BT-EXP-03 | | StrictDoc's own repo (strictdoc_config.py → `strictdoc.api`, user statistics generator `docs.sdoc_project_statistics`, source traceability) | index, project_statistics, tree_map, traceability_matrix, source_coverage pages exist |
| BT-EXP-04 | | `--generate-diff-dirs lhs rhs` | changelog.html shows "1 (1 added)" |
| BT-EXP-05 | | `--generate-diff-git HEAD^..HEAD` on a temp git repo | changelog shows the added requirement |

### 4.3 Import / convert (BT-CONV). Excel is critical.
| ID | Smoke | Test | Pass criteria |
|---|---|---|---|
| BT-CONV-01[fixture,ext] | | `convert input.{xlsx,xls} --input-format=excel` for 3 upstream fixtures | output .sdoc is byte-identical (ignoring CRLF) to upstream's expected .sdoc |
| BT-CONV-02 | ✔ | `.xlsx` → `.sdoc` content check | identical to expected; requirement count = non-empty data rows; UID set = UID column; `[GRAMMAR]` generated |
| BT-CONV-02b | ✔ | Excel import, then `export` html of the result | export rc 0; every UID appears in the HTML |
| BT-CONV-02c | | Excel import of a sheet with a Parent column, then export | **xfail (upstream bug U1)**: strict, so the test flags it once upstream fixes the bug |
| BT-CONV-03 | | Round trip: `export --formats excel` → `convert` back → export html | same number of requirements, same UIDs, all titles present |
| BT-CONV-04 | | `convert sample.reqif` → export html | .sdoc produced; html exported |
| BT-CONV-05 | | Round trip: `export --formats reqif-sdoc` → `convert` back | requirement titles survive |

### 4.4 Manage / format (BT-MAN, BT-FMT)
| ID | Test | Pass criteria |
|---|---|---|
| BT-MAN-01 | `manage auto-uid` on 2 requirements without UIDs | 2 distinct UIDs written |
| BT-MAN-02 | `manage assets` | rc 0 |
| BT-MAN-03 | `manage new` on a single-document project | one more requirement |
| BT-FMT-01 | `format` | rc 0, content preserved |

### 4.5 html2pdf (BT-H2P). Critical.
| ID | Smoke | Test | Pass criteria |
|---|---|---|---|
| BT-H2P-01 | ✔ (if Chrome) | `export --formats html2pdf` on a 3-document fixture | 3 PDFs with `%PDF` magic, page count ≥ 1 (pypdf), text extraction (`pdftotext`, or pypdf as fallback) contains the document title and the requirement titles; driver discovery log saved |
| BT-H2P-02 | | `--chrome-binary /nonexistent` | rc ≠ 0, message mentions Chrome, no traceback |
| BT-H2P-03 | | No network (`unshare -rn`) and an empty driver cache | rc ≠ 0 within 5 min, no traceback |
| BT-H2P-04 | | No network with the driver already cached | rc 0, PDF produced |
| lit | | upstream `tests/integration/features/html2pdf` + `_integration_` (21 tests) | all pass (06_system_chromedriver needs `--param CHROMEDRIVER=`) |

### 4.6 Server (BT-SRV)
Crawler: `tests/bundle/server_crawl.py` (Playwright, headless Chromium). It fails on
any HTTP response ≥ 400 (document, script, stylesheet, font, image, fetch/XHR,
Turbo stream), any failed request, any browser console `error`, and any uncaught
page exception. It records results per page in `crawl_*.json`.

| ID | Smoke | Test | Pass criteria |
|---|---|---|---|
| BT-SRV-01 | ✔ | Boot `server <fixture> --port <free>` with all screens enabled; crawl index, one document plus the TABLE/TRACE/DEEP-TRACE views it links to, index, statistics, matrix; free-text search; open the "edit project title" and "edit requirement" forms | 0 crawl failures; no traceback in the server log |
| BT-SRV-02 | | Scratch copy of StrictDoc's repo (17 documents, 690+ source files): BFS crawl of ≤250 pages (every document and its TABLE/TRACE/DEEP-TRACE/PDF views, project index, statistics, tree map, traceability matrix, source coverage, 25 source-file pages, diff/changelog, the search queries linked from the UI), 2 free-text searches, and 8 forms opened (edit project title, new document, edit document config, edit requirement, new requirement, new section, new text node, move node) | 0 crawl failures, every form opens, no traceback |
| BT-SRV-03 | | Server's `/export_html2pdf/<mid>` (the PDF button) | response body is a PDF |
| BT-SRV-04 | | `/reqif/export_tree` | ReqIF XML (or zip) returned |
| BT-SRV-05 | | `server --watch`, then edit a .sdoc on disk | edited text is served; no traceback |

### 4.7 Bundle-specific (BT-BND)
| ID | Test | Pass criteria |
|---|---|---|
| BT-BND-01 | Session guard: hash of name, size and mtime for every file in the bundle dir, taken before and after the whole run | unchanged (no cache, log or temp files written into the bundle) |
| BT-BND-02 | Run with bogus `PYTHONHOME`/`PYTHONPATH` | export still works |
| BT-BND-03 | Copy the bundle to `.../dir with spaces/strictdoc bundle/` and run from another CWD | export works |
| BT-BND-04 | `launcher` (Tk) with a DISPLAY | process alive after 10 s, no traceback |
| lit | Upstream lit suite with `%strictdoc` = the bundle, PATH stripped of `html2pdf4doc` | all tests pass except documented environment-only failures |

## 5. Failure triage
1. Re-run the failing case with the baseline (`STRICTDOC_EXEC=...`).
2. It fails only on the bundle: **bundle bug**. Report the command, platform, error, and
   missing file or module, with a suspected PyInstaller cause (datas, hiddenimports,
   runtime hook, `sys.executable` re-exec).
3. It fails on both: **upstream bug**. Mark it `xfail(strict=True)` with the reason,
   and report it upstream.
4. Environment-only failures (missing g++, clone dir not named `strictdoc`) are listed in
   the results and not counted.

## 6. Deliverables
- `tests/bundle/run_bundle_tests.sh`: runner (bundle path as argument; tiers smoke/full/lit/all)
- `tests/bundle/test_bundle.py`, `tests/bundle/conftest.py`, `tests/bundle/pytest.ini`
- `tests/bundle/server_crawl.py`: Playwright crawler (also usable on its own)
- `tests/bundle/summarize_results.py`: writes `results.md` (pass/fail matrix) from the JUnit XML
- Results: `build/bundle_test_results/` (JUnit XML, logs, `crawl_*.json`, `results.md`)
