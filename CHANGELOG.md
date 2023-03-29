# Changelog

## [Unreleased](https://github.com/strictdoc-project/strictdoc/tree/HEAD)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.37...HEAD)

**Closed issues:**

- tasks: improve the virtual environments infrastructure  [\#1057](https://github.com/strictdoc-project/strictdoc/issues/1057)

## [0.0.37](https://github.com/strictdoc-project/strictdoc/tree/0.0.37) (2023-03-29)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.36...0.0.37)

**Fixed bugs:**

- Several errors with strictdoc server, possibly connected to deployment via PyInstaller [\#1068](https://github.com/strictdoc-project/strictdoc/issues/1068)

**Closed issues:**

- Empty statement error [\#1083](https://github.com/strictdoc-project/strictdoc/issues/1083)
- Cannot execute strictdoc command  [\#1070](https://github.com/strictdoc-project/strictdoc/issues/1070)
- CI: set up the end-2-end tests on Windows [\#1065](https://github.com/strictdoc-project/strictdoc/issues/1065)
- tasks.py: invoke/venv solution has to be improved  [\#1064](https://github.com/strictdoc-project/strictdoc/issues/1064)
- Implement the initial SDoc markup highlighting plugin for Visual Studio Code [\#1059](https://github.com/strictdoc-project/strictdoc/issues/1059)
- Known issue: test server process leaks semaphore objects when killed by the test script [\#993](https://github.com/strictdoc-project/strictdoc/issues/993)
- SDoc grammar: single vs multiline fields: make a decision [\#823](https://github.com/strictdoc-project/strictdoc/issues/823)

**Merged pull requests:**

- Bump version to 0.0.37 [\#1089](https://github.com/strictdoc-project/strictdoc/pull/1089) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc: disallow empty multiline fields completely. [\#1088](https://github.com/strictdoc-project/strictdoc/pull/1088) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc: disallow empty single fields completely. [\#1087](https://github.com/strictdoc-project/strictdoc/pull/1087) ([stanislaw](https://github.com/stanislaw))
- CI: tests/end2end: try with Tox [\#1086](https://github.com/strictdoc-project/strictdoc/pull/1086) ([stanislaw](https://github.com/stanislaw))
- tasks: switch all tasks to Tox [\#1085](https://github.com/strictdoc-project/strictdoc/pull/1085) ([stanislaw](https://github.com/stanislaw))
- docs: user guide: update with Sublime Text syntax [\#1084](https://github.com/strictdoc-project/strictdoc/pull/1084) ([stanislaw](https://github.com/stanislaw))
- docs: document the IDE support using TextMate grammars [\#1082](https://github.com/strictdoc-project/strictdoc/pull/1082) ([stanislaw](https://github.com/stanislaw))
- docs: document the lack of non-string types support in the UI [\#1080](https://github.com/strictdoc-project/strictdoc/pull/1080) ([stanislaw](https://github.com/stanislaw))
- server: resolve paths to assets correctly for PyInstaller [\#1078](https://github.com/strictdoc-project/strictdoc/pull/1078) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: try reducing the warmup interval from 3 to 0 [\#1075](https://github.com/strictdoc-project/strictdoc/pull/1075) ([stanislaw](https://github.com/stanislaw))
- CI: try end-to-end tests against Windows [\#1073](https://github.com/strictdoc-project/strictdoc/pull/1073) ([stanislaw](https://github.com/stanislaw))

## [0.0.36](https://github.com/strictdoc-project/strictdoc/tree/0.0.36) (2023-03-23)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.35...0.0.36)

**Closed issues:**

- CI: set up an integration test job for proving the quality of the latest released Pip package [\#1067](https://github.com/strictdoc-project/strictdoc/issues/1067)
- Missing Requirements [\#1060](https://github.com/strictdoc-project/strictdoc/issues/1060)

**Merged pull requests:**

- Bump version to 0.0.36 [\#1072](https://github.com/strictdoc-project/strictdoc/pull/1072) ([stanislaw](https://github.com/stanislaw))
- CI: group together periodic integration tests jobs [\#1071](https://github.com/strictdoc-project/strictdoc/pull/1071) ([stanislaw](https://github.com/stanislaw))
- CI: group together end-to-end tests jobs [\#1069](https://github.com/strictdoc-project/strictdoc/pull/1069) ([stanislaw](https://github.com/stanislaw))

## [0.0.35](https://github.com/strictdoc-project/strictdoc/tree/0.0.35) (2023-03-23)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.34...0.0.35)

**Fixed bugs:**

- strictdoc server temp file permission denied on Windows 10 [\#1061](https://github.com/strictdoc-project/strictdoc/issues/1061)

**Closed issues:**

- Web UI Backend [\#563](https://github.com/strictdoc-project/strictdoc/issues/563)

**Merged pull requests:**

- Bump version to 0.0.35 [\#1066](https://github.com/strictdoc-project/strictdoc/pull/1066) ([stanislaw](https://github.com/stanislaw))
-  pyproject.toml: restore the bs4 dependency  [\#1063](https://github.com/strictdoc-project/strictdoc/pull/1063) ([stanislaw](https://github.com/stanislaw))
- server: Do not re-open NamedTemporaryFile on Windows [\#1062](https://github.com/strictdoc-project/strictdoc/pull/1062) ([richardbarlow](https://github.com/richardbarlow))
- .readthedocs.yaml: specify Python 3.11 using new conventions [\#1056](https://github.com/strictdoc-project/strictdoc/pull/1056) ([stanislaw](https://github.com/stanislaw))
- docs: update Read the Docs configuration file [\#1055](https://github.com/strictdoc-project/strictdoc/pull/1055) ([stanislaw](https://github.com/stanislaw))

## [0.0.34](https://github.com/strictdoc-project/strictdoc/tree/0.0.34) (2023-03-21)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.33...0.0.34)

**Fixed bugs:**

- Dragging the DEEP TRACE board is very slow [\#1016](https://github.com/strictdoc-project/strictdoc/issues/1016)
- File Traceability: Highlight issues when tagging ranges outside of one of the referenced files [\#990](https://github.com/strictdoc-project/strictdoc/issues/990)
- Saving multiple fields at once in grammar does not work. [\#954](https://github.com/strictdoc-project/strictdoc/issues/954)
- UI: bug: After saving the document configuration, the page type menu in the header does not work [\#939](https://github.com/strictdoc-project/strictdoc/issues/939)
- Double-check empty comment validation when editing requirement [\#895](https://github.com/strictdoc-project/strictdoc/issues/895)
- Javascript issue: TypeError: undefined is not an object \(evaluating 'this.ranges\[rangeAlliace\]\[reqId\]'\) [\#826](https://github.com/strictdoc-project/strictdoc/issues/826)

**Closed issues:**

- Switch to collapsed TOC by default [\#1051](https://github.com/strictdoc-project/strictdoc/issues/1051)
-  Introduce end-to-end tests for DTR screen [\#1033](https://github.com/strictdoc-project/strictdoc/issues/1033)
- Requirement style Table does not always work correctly \(regresses to Simple style\) [\#1027](https://github.com/strictdoc-project/strictdoc/issues/1027)
- UI: Switch to monospace font for all editable fields [\#1015](https://github.com/strictdoc-project/strictdoc/issues/1015)
- Uvicorn shall not watch for changes in files in the integration test folder [\#1011](https://github.com/strictdoc-project/strictdoc/issues/1011)
- UI: document view header: include title in turbo-frame [\#1008](https://github.com/strictdoc-project/strictdoc/issues/1008)
- Deep-traceability: make a short view for requirement + open the full view in a modal [\#1005](https://github.com/strictdoc-project/strictdoc/issues/1005)
- Static HTML export: remove node reactions on hovering [\#998](https://github.com/strictdoc-project/strictdoc/issues/998)
- Create placeholder for empty views \(trace and deep-trace\) [\#995](https://github.com/strictdoc-project/strictdoc/issues/995)
- Error when cancelling editing of a specific section [\#991](https://github.com/strictdoc-project/strictdoc/issues/991)
- TBL: table's top border is missing [\#980](https://github.com/strictdoc-project/strictdoc/issues/980)
- Escape/unescape in requirement field [\#977](https://github.com/strictdoc-project/strictdoc/issues/977)
- Bug in contenteditable [\#975](https://github.com/strictdoc-project/strictdoc/issues/975)
- Local development issue: resolving import paths when called outside strictdoc/ folder [\#968](https://github.com/strictdoc-project/strictdoc/issues/968)
- CI: Flaky tests caused by pytest not starting the server on time [\#966](https://github.com/strictdoc-project/strictdoc/issues/966)
- Display validation messages as a list if there is more than one message [\#952](https://github.com/strictdoc-project/strictdoc/issues/952)
- Add confirmations for dangerous actions [\#945](https://github.com/strictdoc-project/strictdoc/issues/945)
- Wrong behavior of UI items in the menu [\#931](https://github.com/strictdoc-project/strictdoc/issues/931)
- Document tree: remove DOC/TBL/TR/DTR badges [\#927](https://github.com/strictdoc-project/strictdoc/issues/927)
- End-to-end tests: create screen-based test helpers to encapsulate all lower-level XPath implementation [\#926](https://github.com/strictdoc-project/strictdoc/issues/926)
- Solve the problem with a SDoc server not being terminated fast enough before the next test starts [\#925](https://github.com/strictdoc-project/strictdoc/issues/925)
- Solve the problem with conflicting /tmp folders where server and end2end tests generate output [\#924](https://github.com/strictdoc-project/strictdoc/issues/924)
- docs: document the existing capability of UI v0 [\#917](https://github.com/strictdoc-project/strictdoc/issues/917)
- UI: finish CSS layout of all editable fields [\#915](https://github.com/strictdoc-project/strictdoc/issues/915)
- DTR: Collapsible cards, so that only the requirement titles are browsable. [\#914](https://github.com/strictdoc-project/strictdoc/issues/914)
- Add StrictDoc label on the generated/server HTML pages [\#909](https://github.com/strictdoc-project/strictdoc/issues/909)
-  RST tables: align padding of normal text and padding of bullet list. [\#907](https://github.com/strictdoc-project/strictdoc/issues/907)
- Requirement to source file links: handle validation edge case: missing closing pragmas [\#902](https://github.com/strictdoc-project/strictdoc/issues/902)
- RST to HTML rendering by docutils: improve the styles of tables [\#888](https://github.com/strictdoc-project/strictdoc/issues/888)
- Requirement-to-File links edge case: Pygments ignore the first empty line in a file [\#877](https://github.com/strictdoc-project/strictdoc/issues/877)
- Finish handling of the grammar fields: moving up/down and deleting a new grammar field [\#872](https://github.com/strictdoc-project/strictdoc/issues/872)
- Problems with pyinstaller version \(OS X\) [\#837](https://github.com/strictdoc-project/strictdoc/issues/837)
- UI: Remaining work before first release [\#764](https://github.com/strictdoc-project/strictdoc/issues/764)
-  Feature: HTML/DOC: Make a difference between requirement items and free text more visible [\#711](https://github.com/strictdoc-project/strictdoc/issues/711)

**Merged pull requests:**

-  Bump version to 0.0.34  [\#1054](https://github.com/strictdoc-project/strictdoc/pull/1054) ([stanislaw](https://github.com/stanislaw))
- export/html, UI: Switch to collapsed TOC by default [\#1052](https://github.com/strictdoc-project/strictdoc/pull/1052) ([stanislaw](https://github.com/stanislaw))
- export/html: improved JS for doing pan over the DTR screen [\#1049](https://github.com/strictdoc-project/strictdoc/pull/1049) ([stanislaw](https://github.com/stanislaw))
- export/html: Update the backport to a container-type using @media [\#1048](https://github.com/strictdoc-project/strictdoc/pull/1048) ([mettta](https://github.com/mettta))
- docs: document the existing capability of UI v0 [\#1047](https://github.com/strictdoc-project/strictdoc/pull/1047) ([stanislaw](https://github.com/stanislaw))
- Code climate: rename /project\_index and /screens; remove wrongly committed sdoc file [\#1046](https://github.com/strictdoc-project/strictdoc/pull/1046) ([mettta](https://github.com/mettta))
- tests/end2end: update Screens \(TR, DTR, TBL\) tests [\#1044](https://github.com/strictdoc-project/strictdoc/pull/1044) ([mettta](https://github.com/mettta))
- Add end-to-end tests for DTR screen [\#1043](https://github.com/strictdoc-project/strictdoc/pull/1043) ([mettta](https://github.com/mettta))
- tests/end2end: Updating the node finding method using testid [\#1041](https://github.com/strictdoc-project/strictdoc/pull/1041) ([mettta](https://github.com/mettta))
- tests/integration: source files traceability: ensure a test with "docs/ + src/" structure [\#1040](https://github.com/strictdoc-project/strictdoc/pull/1040) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: update helpers, add init tests for all screen types [\#1039](https://github.com/strictdoc-project/strictdoc/pull/1039) ([mettta](https://github.com/mettta))
- Bump version to 0.0.34-alpha.1 [\#1038](https://github.com/strictdoc-project/strictdoc/pull/1038) ([stanislaw](https://github.com/stanislaw))
- strictdoc.toml: features= parameter for centralized activiation/deactivation of features [\#1036](https://github.com/strictdoc-project/strictdoc/pull/1036) ([stanislaw](https://github.com/stanislaw))
- export/html, traceability: fix several JS issues in the source file screen [\#1035](https://github.com/strictdoc-project/strictdoc/pull/1035) ([stanislaw](https://github.com/stanislaw))
- export/html: add Jinja extension for assertions in Jinja templates [\#1034](https://github.com/strictdoc-project/strictdoc/pull/1034) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: print current test number and how many tests are there [\#1030](https://github.com/strictdoc-project/strictdoc/pull/1030) ([stanislaw](https://github.com/stanislaw))
- UI/components: DTR: make a short view for requirement + open the full view in a modal [\#1029](https://github.com/strictdoc-project/strictdoc/pull/1029) ([mettta](https://github.com/mettta))
- server: do not reload when anything in tests/ is touched [\#1028](https://github.com/strictdoc-project/strictdoc/pull/1028) ([stanislaw](https://github.com/stanislaw))
- traceability: minor cleanups and prepare an integration test [\#1025](https://github.com/strictdoc-project/strictdoc/pull/1025) ([stanislaw](https://github.com/stanislaw))
-  docs: regenerate Read the Docs  [\#1024](https://github.com/strictdoc-project/strictdoc/pull/1024) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: print a test number when a test starts [\#1023](https://github.com/strictdoc-project/strictdoc/pull/1023) ([stanislaw](https://github.com/stanislaw))
- server, UI: fix the escaping of RST strings in multiline fields [\#1018](https://github.com/strictdoc-project/strictdoc/pull/1018) ([stanislaw](https://github.com/stanislaw))
- docs: update Development Plan [\#1017](https://github.com/strictdoc-project/strictdoc/pull/1017) ([stanislaw](https://github.com/stanislaw))
- docs: update Requirements and Design [\#1014](https://github.com/strictdoc-project/strictdoc/pull/1014) ([stanislaw](https://github.com/stanislaw))
- UI: document view header: include document title in turbo-frame [\#1010](https://github.com/strictdoc-project/strictdoc/pull/1010) ([mettta](https://github.com/mettta))
- UI: add placeholder for empty views [\#1009](https://github.com/strictdoc-project/strictdoc/pull/1009) ([mettta](https://github.com/mettta))
- server: handle one case of when editing section is cancelled [\#1006](https://github.com/strictdoc-project/strictdoc/pull/1006) ([stanislaw](https://github.com/stanislaw))
- Static HTML export: remove node reactions on hovering [\#1004](https://github.com/strictdoc-project/strictdoc/pull/1004) ([mettta](https://github.com/mettta))
- tasks.py: stop generating StrictDoc documentation alongside Sphinx HTML export [\#1003](https://github.com/strictdoc-project/strictdoc/pull/1003) ([stanislaw](https://github.com/stanislaw))
- UI: Use Confirm when deleting sections and requirements [\#1002](https://github.com/strictdoc-project/strictdoc/pull/1002) ([mettta](https://github.com/mettta))
- export/html: do not render unique identifiers when static export [\#1000](https://github.com/strictdoc-project/strictdoc/pull/1000) ([stanislaw](https://github.com/stanislaw))
- tasks: copy StrictDoc documentation to GitHub pages repo as well [\#999](https://github.com/strictdoc-project/strictdoc/pull/999) ([stanislaw](https://github.com/stanislaw))
- strictdoc.toml: introduce the html\_assets\_strictdoc\_dir parameter [\#996](https://github.com/strictdoc-project/strictdoc/pull/996) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: when exception happens, print out and err output to the console [\#994](https://github.com/strictdoc-project/strictdoc/pull/994) ([stanislaw](https://github.com/stanislaw))
- parallelizer: catch the semaphores-related macOS edge case, document the edge case [\#992](https://github.com/strictdoc-project/strictdoc/pull/992) ([mettta](https://github.com/mettta))
- UI: Display multiple validation messages as a list [\#989](https://github.com/strictdoc-project/strictdoc/pull/989) ([mettta](https://github.com/mettta))
- UI: Fix field overflow if text has extra long words [\#988](https://github.com/strictdoc-project/strictdoc/pull/988) ([mettta](https://github.com/mettta))
- tests: end2end updates [\#987](https://github.com/strictdoc-project/strictdoc/pull/987) ([mettta](https://github.com/mettta))
- tests: update UC55/56, Screen\_DocumentTree, add Form\_ImportReqIF\(Form\) [\#986](https://github.com/strictdoc-project/strictdoc/pull/986) ([mettta](https://github.com/mettta))
- export/html: remove unused static\_path variable from HTML templates [\#985](https://github.com/strictdoc-project/strictdoc/pull/985) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: updates [\#984](https://github.com/strictdoc-project/strictdoc/pull/984) ([mettta](https://github.com/mettta))
- tests: end2end: add Form class and subclasses for context forms [\#983](https://github.com/strictdoc-project/strictdoc/pull/983) ([mettta](https://github.com/mettta))
- UI: TBL view: fix top border [\#982](https://github.com/strictdoc-project/strictdoc/pull/982) ([mettta](https://github.com/mettta))
- export/html: rename all \_\*.\* files to \*.\* [\#981](https://github.com/strictdoc-project/strictdoc/pull/981) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: more explicit configuration of all timeouts [\#979](https://github.com/strictdoc-project/strictdoc/pull/979) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: update UC11/12/20 [\#978](https://github.com/strictdoc-project/strictdoc/pull/978) ([mettta](https://github.com/mettta))
- tests/end2end: update UC07 [\#976](https://github.com/strictdoc-project/strictdoc/pull/976) ([mettta](https://github.com/mettta))
- pyproject.toml: remove MarkupSafe workaround version pin [\#974](https://github.com/strictdoc-project/strictdoc/pull/974) ([stanislaw](https://github.com/stanislaw))
- pyproject.toml: remove beautifulsoup4 as obsolete [\#973](https://github.com/strictdoc-project/strictdoc/pull/973) ([stanislaw](https://github.com/stanislaw))
- NOTICE file [\#972](https://github.com/strictdoc-project/strictdoc/pull/972) ([stanislaw](https://github.com/stanislaw))
- LICENSE: provide an explicit copyright line [\#971](https://github.com/strictdoc-project/strictdoc/pull/971) ([stanislaw](https://github.com/stanislaw))
- UI: forms: Update the form layout, the output of the fields and the field action buttons. [\#970](https://github.com/strictdoc-project/strictdoc/pull/970) ([mettta](https://github.com/mettta))
- reqif/p11\_polarion: accommodate for a yet another spec object type [\#969](https://github.com/strictdoc-project/strictdoc/pull/969) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: introduce screen-based test helpers: UC07\_T01 [\#967](https://github.com/strictdoc-project/strictdoc/pull/967) ([mettta](https://github.com/mettta))
- UI: Add requirement 'table/zebra' display modes [\#965](https://github.com/strictdoc-project/strictdoc/pull/965) ([mettta](https://github.com/mettta))
- server, UI: finish the implementation of saving multiple grammar fields [\#963](https://github.com/strictdoc-project/strictdoc/pull/963) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC55 and other [\#961](https://github.com/strictdoc-project/strictdoc/pull/961) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC11 and UC12 [\#960](https://github.com/strictdoc-project/strictdoc/pull/960) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC10 [\#959](https://github.com/strictdoc-project/strictdoc/pull/959) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC09 [\#958](https://github.com/strictdoc-project/strictdoc/pull/958) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC08 [\#957](https://github.com/strictdoc-project/strictdoc/pull/957) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC07 [\#956](https://github.com/strictdoc-project/strictdoc/pull/956) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC07\_G\[1-2\] [\#953](https://github.com/strictdoc-project/strictdoc/pull/953) ([stanislaw](https://github.com/stanislaw))
- tests/end2: bring UC08-UC10 to latest naming conventions [\#951](https://github.com/strictdoc-project/strictdoc/pull/951) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC06 [\#950](https://github.com/strictdoc-project/strictdoc/pull/950) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to latest naming conventions: UC00, UC01 [\#949](https://github.com/strictdoc-project/strictdoc/pull/949) ([stanislaw](https://github.com/stanislaw))
- tests/end2end: migrate tests to safe server code: UC03: T01-T07 tests [\#946](https://github.com/strictdoc-project/strictdoc/pull/946) ([stanislaw](https://github.com/stanislaw))
- UI: add turbo-template for the document title… [\#944](https://github.com/strictdoc-project/strictdoc/pull/944) ([mettta](https://github.com/mettta))
- tests/end2end: ensure the server is stopped when any exception occurs [\#943](https://github.com/strictdoc-project/strictdoc/pull/943) ([stanislaw](https://github.com/stanislaw))
- UI: remove unused code [\#942](https://github.com/strictdoc-project/strictdoc/pull/942) ([mettta](https://github.com/mettta))
- UI: display document title on the table view [\#941](https://github.com/strictdoc-project/strictdoc/pull/941) ([mettta](https://github.com/mettta))
- UI: Add StrictDoc label on the generated/server HTML pages [\#938](https://github.com/strictdoc-project/strictdoc/pull/938) ([mettta](https://github.com/mettta))
- tests/end2end: reuse the browser session to speed up the tests [\#937](https://github.com/strictdoc-project/strictdoc/pull/937) ([stanislaw](https://github.com/stanislaw))
- server: create the output in the temporary directory unless specified [\#936](https://github.com/strictdoc-project/strictdoc/pull/936) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate Read the Docs documentation [\#935](https://github.com/strictdoc-project/strictdoc/pull/935) ([stanislaw](https://github.com/stanislaw))
- docs: updates to FAQ, add Credits [\#934](https://github.com/strictdoc-project/strictdoc/pull/934) ([stanislaw](https://github.com/stanislaw))
- UI: Document tree: remove DOC/TBL/TR/DTR badges [\#933](https://github.com/strictdoc-project/strictdoc/pull/933) ([mettta](https://github.com/mettta))
- UI: Fix wrong behavior of UI items in the menu [\#932](https://github.com/strictdoc-project/strictdoc/pull/932) ([mettta](https://github.com/mettta))
- backend/reqif: handle the edge case with \<xhtml:object\> tag [\#930](https://github.com/strictdoc-project/strictdoc/pull/930) ([stanislaw](https://github.com/stanislaw))
- RST tables: align padding of normal text and padding of bullet list. [\#929](https://github.com/strictdoc-project/strictdoc/pull/929) ([mettta](https://github.com/mettta))
- UI: Fix table border in Safari [\#928](https://github.com/strictdoc-project/strictdoc/pull/928) ([mettta](https://github.com/mettta))
- UI: forms: components/form/field [\#922](https://github.com/strictdoc-project/strictdoc/pull/922) ([mettta](https://github.com/mettta))
- UI: forms: Requirement parent link [\#921](https://github.com/strictdoc-project/strictdoc/pull/921) ([mettta](https://github.com/mettta))
- docs: regenerate Read the Docs documentation [\#920](https://github.com/strictdoc-project/strictdoc/pull/920) ([stanislaw](https://github.com/stanislaw))
- docs: FAQ: document basic web server recommendations [\#919](https://github.com/strictdoc-project/strictdoc/pull/919) ([stanislaw](https://github.com/stanislaw))
- docs: update Backlog [\#918](https://github.com/strictdoc-project/strictdoc/pull/918) ([stanislaw](https://github.com/stanislaw))
- UI: forms: update grammar fields [\#916](https://github.com/strictdoc-project/strictdoc/pull/916) ([mettta](https://github.com/mettta))
- UI: forms: add a default field\_name value for newly added fields  [\#906](https://github.com/strictdoc-project/strictdoc/pull/906) ([mettta](https://github.com/mettta))
- UI:forms:  edit grammar  [\#905](https://github.com/strictdoc-project/strictdoc/pull/905) ([mettta](https://github.com/mettta))
- Code climate: ruff: activate ERA [\#904](https://github.com/strictdoc-project/strictdoc/pull/904) ([stanislaw](https://github.com/stanislaw))
- Code climate: ruff: activate most of UP group [\#903](https://github.com/strictdoc-project/strictdoc/pull/903) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix all T201 errors [\#901](https://github.com/strictdoc-project/strictdoc/pull/901) ([stanislaw](https://github.com/stanislaw))
- export/html: support linking requirements with Jinja files [\#900](https://github.com/strictdoc-project/strictdoc/pull/900) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc\_source\_code: introduce the @sdoc keyword [\#899](https://github.com/strictdoc-project/strictdoc/pull/899) ([stanislaw](https://github.com/stanislaw))
- Code climate: upgrade link\_health.py [\#898](https://github.com/strictdoc-project/strictdoc/pull/898) ([stanislaw](https://github.com/stanislaw))
- UI: forms: comment fields [\#897](https://github.com/strictdoc-project/strictdoc/pull/897) ([mettta](https://github.com/mettta))
- UI: update 'edit section/requirement' forms templates [\#896](https://github.com/strictdoc-project/strictdoc/pull/896) ([mettta](https://github.com/mettta))
- server: update requirement: only regenerate the document's own SDoc file [\#894](https://github.com/strictdoc-project/strictdoc/pull/894) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate Read the Docs documentation [\#892](https://github.com/strictdoc-project/strictdoc/pull/892) ([stanislaw](https://github.com/stanislaw))
- export/rst: fix edge case when rendering RST section titles [\#890](https://github.com/strictdoc-project/strictdoc/pull/890) ([stanislaw](https://github.com/stanislaw))
- UI: update form/modal markup and CSS [\#889](https://github.com/strictdoc-project/strictdoc/pull/889) ([mettta](https://github.com/mettta))
- requirements coverage: hide under the traceability flag for now [\#887](https://github.com/strictdoc-project/strictdoc/pull/887) ([stanislaw](https://github.com/stanislaw))
- docs: User Guide: add a link to strictdoc-examples repository [\#886](https://github.com/strictdoc-project/strictdoc/pull/886) ([stanislaw](https://github.com/stanislaw))
- server, UI: Document tree: modal forms, test updates [\#883](https://github.com/strictdoc-project/strictdoc/pull/883) ([mettta](https://github.com/mettta))
- docs: requirements: remove composite requirements [\#881](https://github.com/strictdoc-project/strictdoc/pull/881) ([stanislaw](https://github.com/stanislaw))
- Source file traceability: fix edge case: Pygments ignore the first empty line in a file [\#878](https://github.com/strictdoc-project/strictdoc/pull/878) ([stanislaw](https://github.com/stanislaw))
- UI: fix line on the top of the source code page [\#876](https://github.com/strictdoc-project/strictdoc/pull/876) ([mettta](https://github.com/mettta))
- examples: move in tests/integration/examples, strip from itest files [\#875](https://github.com/strictdoc-project/strictdoc/pull/875) ([mettta](https://github.com/mettta))
- docs: FAQ: some numbers [\#874](https://github.com/strictdoc-project/strictdoc/pull/874) ([stanislaw](https://github.com/stanislaw))
- Finish handling of the grammar fields: moving up/down and deleting a new grammar field [\#873](https://github.com/strictdoc-project/strictdoc/pull/873) ([stanislaw](https://github.com/stanislaw))
- server, UI: move editing of the free text into a document config section [\#869](https://github.com/strictdoc-project/strictdoc/pull/869) ([stanislaw](https://github.com/stanislaw))
- server: switch to port 5111 as less popular port [\#868](https://github.com/strictdoc-project/strictdoc/pull/868) ([stanislaw](https://github.com/stanislaw))
- tests/integration/examples: add basic examples [\#867](https://github.com/strictdoc-project/strictdoc/pull/867) ([stanislaw](https://github.com/stanislaw))
- tests/integration: reqif/profiles/p11\_polarion/02\_escaping\_symbols [\#866](https://github.com/strictdoc-project/strictdoc/pull/866) ([stanislaw](https://github.com/stanislaw))
- reqif: p11\_polarion: strip XHTML tags from \<xhtml:...\> namespace prefixes [\#865](https://github.com/strictdoc-project/strictdoc/pull/865) ([stanislaw](https://github.com/stanislaw))
- reqif: introduce p11\_polarion profile, parse the user-provided Polarion example [\#864](https://github.com/strictdoc-project/strictdoc/pull/864) ([stanislaw](https://github.com/stanislaw))
- CI: bring back the PyInstaller task on macOS [\#863](https://github.com/strictdoc-project/strictdoc/pull/863) ([stanislaw](https://github.com/stanislaw))
- reqif: improved handling of multi-value enum attributes. [\#862](https://github.com/strictdoc-project/strictdoc/pull/862) ([stanislaw](https://github.com/stanislaw))
- Ensure that multiprocessing.freeze\_support\(\) is called in a frozen application [\#861](https://github.com/strictdoc-project/strictdoc/pull/861) ([RobertoBagnara](https://github.com/RobertoBagnara))
- reqif: reqif-to-sdoc: remove the factory class to simplify further work [\#860](https://github.com/strictdoc-project/strictdoc/pull/860) ([stanislaw](https://github.com/stanislaw))
- reqif: import: skip DATE spec object attributes [\#859](https://github.com/strictdoc-project/strictdoc/pull/859) ([stanislaw](https://github.com/stanislaw))
- pyproject.toml: bump ReqIF version, change to \>= [\#858](https://github.com/strictdoc-project/strictdoc/pull/858) ([stanislaw](https://github.com/stanislaw))
- Code climate: ruff: activate I group [\#857](https://github.com/strictdoc-project/strictdoc/pull/857) ([stanislaw](https://github.com/stanislaw))
- Code climate: tasks: add ruff linter [\#856](https://github.com/strictdoc-project/strictdoc/pull/856) ([stanislaw](https://github.com/stanislaw))
- server, UI: egse case when editing requirement \(no UID\) [\#855](https://github.com/strictdoc-project/strictdoc/pull/855) ([stanislaw](https://github.com/stanislaw))
- server, UI: adding/deleting requirement's parent links [\#854](https://github.com/strictdoc-project/strictdoc/pull/854) ([stanislaw](https://github.com/stanislaw))
- traceability\_index: method to assign/unassign a requirement parent link [\#853](https://github.com/strictdoc-project/strictdoc/pull/853) ([stanislaw](https://github.com/stanislaw))
- traceability\_index: refactoring work towards Web-editable parent links [\#852](https://github.com/strictdoc-project/strictdoc/pull/852) ([stanislaw](https://github.com/stanislaw))
- server, UI: editing table-based requirements [\#851](https://github.com/strictdoc-project/strictdoc/pull/851) ([stanislaw](https://github.com/stanislaw))
- server: validation: do not allow creating documents without .sdoc extension [\#850](https://github.com/strictdoc-project/strictdoc/pull/850) ([stanislaw](https://github.com/stanislaw))
- Code climate: tests/end2end: adjust document tree tests to latest naming conventions [\#849](https://github.com/strictdoc-project/strictdoc/pull/849) ([stanislaw](https://github.com/stanislaw))
- Code climate: tests/end2end: remove debug screenshot lines [\#848](https://github.com/strictdoc-project/strictdoc/pull/848) ([stanislaw](https://github.com/stanislaw))
- server, tests/end2end: run dev server and test servers on different ports [\#847](https://github.com/strictdoc-project/strictdoc/pull/847) ([stanislaw](https://github.com/stanislaw))
- UI: update 'Empty Doc placeholder' template and related tests [\#846](https://github.com/strictdoc-project/strictdoc/pull/846) ([mettta](https://github.com/mettta))
- Tests/end2end: delete comments [\#845](https://github.com/strictdoc-project/strictdoc/pull/845) ([mettta](https://github.com/mettta))
- Remove Nuitka from the development dependancies [\#844](https://github.com/strictdoc-project/strictdoc/pull/844) ([mettta](https://github.com/mettta))
- UI: add Empty Document placeholder and the corresponding test [\#843](https://github.com/strictdoc-project/strictdoc/pull/843) ([mettta](https://github.com/mettta))
- tasks: Environment class to encapsulate all compile-time information [\#841](https://github.com/strictdoc-project/strictdoc/pull/841) ([stanislaw](https://github.com/stanislaw))
- UI: Add dropdown menu on nodes [\#840](https://github.com/strictdoc-project/strictdoc/pull/840) ([mettta](https://github.com/mettta))
- tests/integration: run strictdoc without any args to attest the PyInstaller bug [\#839](https://github.com/strictdoc-project/strictdoc/pull/839) ([stanislaw](https://github.com/stanislaw))
- tasks: adapt PyInstaller to support "strictdoc server" command [\#838](https://github.com/strictdoc-project/strictdoc/pull/838) ([stanislaw](https://github.com/stanislaw))
- tasks, packaging: allow generating a Windows release under Linux via … [\#836](https://github.com/strictdoc-project/strictdoc/pull/836) ([RobertoBagnara](https://github.com/RobertoBagnara))
- docs: FAQ: SDoc markup and StrictDoc tutorial [\#834](https://github.com/strictdoc-project/strictdoc/pull/834) ([stanislaw](https://github.com/stanislaw))
- server: fix editing of the grammar fields [\#833](https://github.com/strictdoc-project/strictdoc/pull/833) ([stanislaw](https://github.com/stanislaw))
- UI: refactor CSS [\#832](https://github.com/strictdoc-project/strictdoc/pull/832) ([mettta](https://github.com/mettta))
- export/html: remove JQuery [\#829](https://github.com/strictdoc-project/strictdoc/pull/829) ([stanislaw](https://github.com/stanislaw))
- export/html: group JS controllers in a dedicated folder [\#828](https://github.com/strictdoc-project/strictdoc/pull/828) ([stanislaw](https://github.com/stanislaw))
- export/html: switch to Python helper for rendering static URLs [\#827](https://github.com/strictdoc-project/strictdoc/pull/827) ([stanislaw](https://github.com/stanislaw))
- server, UI: editing document grammar [\#825](https://github.com/strictdoc-project/strictdoc/pull/825) ([stanislaw](https://github.com/stanislaw))
- models: requirement: remove \#tags setter [\#824](https://github.com/strictdoc-project/strictdoc/pull/824) ([stanislaw](https://github.com/stanislaw))
- sdoc/models: requirement: remove @uid, @status, @level setters [\#822](https://github.com/strictdoc-project/strictdoc/pull/822) ([stanislaw](https://github.com/stanislaw))
- sdoc/models: requirement: title -\> reserved\_title [\#821](https://github.com/strictdoc-project/strictdoc/pull/821) ([stanislaw](https://github.com/stanislaw))
- sdoc/models: requirement: remove title, statement, and rationale setters [\#820](https://github.com/strictdoc-project/strictdoc/pull/820) ([stanislaw](https://github.com/stanislaw))
- grammar, models: remove RequirementComment [\#819](https://github.com/strictdoc-project/strictdoc/pull/819) ([stanislaw](https://github.com/stanislaw))
- server, UI: editing document config: TITLE and VERSION [\#817](https://github.com/strictdoc-project/strictdoc/pull/817) ([stanislaw](https://github.com/stanislaw))
- UI: Dedicated controller for collapsible Table of Contents [\#816](https://github.com/strictdoc-project/strictdoc/pull/816) ([mettta](https://github.com/mettta))
- core: project-level TOML config file [\#815](https://github.com/strictdoc-project/strictdoc/pull/815) ([stanislaw](https://github.com/stanislaw))
- server, UI: editing multiple requirement comments [\#814](https://github.com/strictdoc-project/strictdoc/pull/814) ([stanislaw](https://github.com/stanislaw))
- UI: Implement the new layout and behavior changes for the TOC [\#813](https://github.com/strictdoc-project/strictdoc/pull/813) ([mettta](https://github.com/mettta))

## [0.0.33](https://github.com/strictdoc-project/strictdoc/tree/0.0.33) (2023-02-09)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.32...0.0.33)

**Closed issues:**

- Problems with pyinstaller version \(Linux\) [\#835](https://github.com/strictdoc-project/strictdoc/issues/835)
- Automatically add the file format in the form in the project tree page [\#775](https://github.com/strictdoc-project/strictdoc/issues/775)
- strictdoc.toml: introduce project-level config file [\#587](https://github.com/strictdoc-project/strictdoc/issues/587)

## [0.0.32](https://github.com/strictdoc-project/strictdoc/tree/0.0.32) (2023-01-09)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.31...0.0.32)

**Closed issues:**

- Can't install 0.0.29 or 0.0.30: requirements.txt missing [\#803](https://github.com/strictdoc-project/strictdoc/issues/803)
- DEPRECATION: strictdoc is being installed using the legacy 'setup.py install' method [\#753](https://github.com/strictdoc-project/strictdoc/issues/753)

**Merged pull requests:**

- Bump version to 0.0.32 [\#810](https://github.com/strictdoc-project/strictdoc/pull/810) ([stanislaw](https://github.com/stanislaw))
- export/html: do not display "Export to ReqIF" in the static export [\#809](https://github.com/strictdoc-project/strictdoc/pull/809) ([stanislaw](https://github.com/stanislaw))
- docs: link health: add Bugseng article to exceptions [\#808](https://github.com/strictdoc-project/strictdoc/pull/808) ([stanislaw](https://github.com/stanislaw))
- UI: pan-with-space.js: Use \#pan-with-space instead of class [\#807](https://github.com/strictdoc-project/strictdoc/pull/807) ([mettta](https://github.com/mettta))
- server, UI: requirement form is rendered from all grammar fields [\#806](https://github.com/strictdoc-project/strictdoc/pull/806) ([stanislaw](https://github.com/stanislaw))
- Code climate: extend linting by flake8 and pylint to tests/\* [\#805](https://github.com/strictdoc-project/strictdoc/pull/805) ([stanislaw](https://github.com/stanislaw))

## [0.0.31](https://github.com/strictdoc-project/strictdoc/tree/0.0.31) (2023-01-05)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.30...0.0.31)

**Merged pull requests:**

- tasks, packaging: switch to pyproject.toml, remove setup.py [\#804](https://github.com/strictdoc-project/strictdoc/pull/804) ([stanislaw](https://github.com/stanislaw))
- server: main\_router: merge in complete main\_controller [\#802](https://github.com/strictdoc-project/strictdoc/pull/802) ([stanislaw](https://github.com/stanislaw))
- server: clean up the main controller using the new API [\#801](https://github.com/strictdoc-project/strictdoc/pull/801) ([stanislaw](https://github.com/stanislaw))
- server: editing requirement's UID [\#800](https://github.com/strictdoc-project/strictdoc/pull/800) ([stanislaw](https://github.com/stanislaw))
- server: editing requirement's rationale [\#799](https://github.com/strictdoc-project/strictdoc/pull/799) ([stanislaw](https://github.com/stanislaw))
- backend/excel/export: Support Excel Export of custom grammar fields [\#797](https://github.com/strictdoc-project/strictdoc/pull/797) ([GGBeer](https://github.com/GGBeer))
- Code climate: introduce helpers/auto\_described to print objects [\#796](https://github.com/strictdoc-project/strictdoc/pull/796) ([stanislaw](https://github.com/stanislaw))

## [0.0.30](https://github.com/strictdoc-project/strictdoc/tree/0.0.30) (2022-12-24)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.29...0.0.30)

**Fixed bugs:**

- server: zombie worker processes are left when Selenium timeouts [\#785](https://github.com/strictdoc-project/strictdoc/issues/785)
- UI: problem when adding \<\> symbols to editable fields [\#782](https://github.com/strictdoc-project/strictdoc/issues/782)
- backend/sdoc: fix the edge case when rstripping the multi-line fields [\#793](https://github.com/strictdoc-project/strictdoc/pull/793) ([stanislaw](https://github.com/stanislaw))

**Closed issues:**

- export/rst: doens't render the custom fields [\#779](https://github.com/strictdoc-project/strictdoc/issues/779)
- backend/reqif: import the complete documentation tree from a ReqIF file [\#777](https://github.com/strictdoc-project/strictdoc/issues/777)
- Partial evaluation of Jinja templates [\#453](https://github.com/strictdoc-project/strictdoc/issues/453)
- Basic unit and integration test coverage is missing [\#139](https://github.com/strictdoc-project/strictdoc/issues/139)
- export/html: RST-\>HTML rendering using docutils is a performance bottleneck [\#138](https://github.com/strictdoc-project/strictdoc/issues/138)

**Merged pull requests:**

- Bump version to 0.0.30 [\#795](https://github.com/strictdoc-project/strictdoc/pull/795) ([stanislaw](https://github.com/stanislaw))
- backend/reqif: update to the latest API [\#794](https://github.com/strictdoc-project/strictdoc/pull/794) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc/grammar: Add REFS-BibReference [\#792](https://github.com/strictdoc-project/strictdoc/pull/792) ([GGBeer](https://github.com/GGBeer))
- backend/sdoc/grammar: Refactoring REFS ParentReqReference, FileReference [\#791](https://github.com/strictdoc-project/strictdoc/pull/791) ([GGBeer](https://github.com/GGBeer))
- backend, sdoc, rst: remove trailing newlines by multistring fields [\#790](https://github.com/strictdoc-project/strictdoc/pull/790) ([stanislaw](https://github.com/stanislaw))
- export, rst: add custom grammar fields into jinja2 rendering [\#788](https://github.com/strictdoc-project/strictdoc/pull/788) ([BenGardiner](https://github.com/BenGardiner))
- server: exporting and importing complete document tree [\#787](https://github.com/strictdoc-project/strictdoc/pull/787) ([stanislaw](https://github.com/stanislaw))
- server: fix zombie worker processes issue when Selenium timeouts [\#786](https://github.com/strictdoc-project/strictdoc/pull/786) ([stanislaw](https://github.com/stanislaw))
- server: escape multi-line text when rendering edit forms \(requirement, section\) [\#784](https://github.com/strictdoc-project/strictdoc/pull/784) ([stanislaw](https://github.com/stanislaw))
- docs: Contributing: How can I help? [\#783](https://github.com/strictdoc-project/strictdoc/pull/783) ([stanislaw](https://github.com/stanislaw))
- export/rst: switch to Jinja template for rendering requirement to RST \(take 2\) [\#781](https://github.com/strictdoc-project/strictdoc/pull/781) ([stanislaw](https://github.com/stanislaw))
- export/rst: switch to Jinja template for rendering requirement to RST [\#780](https://github.com/strictdoc-project/strictdoc/pull/780) ([stanislaw](https://github.com/stanislaw))
- backend/reqif: exporting document's free text [\#778](https://github.com/strictdoc-project/strictdoc/pull/778) ([stanislaw](https://github.com/stanislaw))
-  server: basic importing and exporting ReqIF  [\#776](https://github.com/strictdoc-project/strictdoc/pull/776) ([stanislaw](https://github.com/stanislaw))
- Code climate: Do not rely on SD working dirname in ConfTest [\#773](https://github.com/strictdoc-project/strictdoc/pull/773) ([GGBeer](https://github.com/GGBeer))
- tests/integration: try a Windows-friendlier diff command [\#772](https://github.com/strictdoc-project/strictdoc/pull/772) ([stanislaw](https://github.com/stanislaw))
- backend/rst: handle SEVERE errors through the friendlier interface [\#771](https://github.com/strictdoc-project/strictdoc/pull/771) ([stanislaw](https://github.com/stanislaw))
- CI: try Selenium tests on macOS [\#770](https://github.com/strictdoc-project/strictdoc/pull/770) ([stanislaw](https://github.com/stanislaw))
- UI:  Make form fields have monospace font [\#769](https://github.com/strictdoc-project/strictdoc/pull/769) ([mettta](https://github.com/mettta))
- docs:strictdoc\_01\_user\_guide UGuide updates/restructuring [\#768](https://github.com/strictdoc-project/strictdoc/pull/768) ([GGBeer](https://github.com/GGBeer))
- server: read both single- and multi-line requirement statements [\#767](https://github.com/strictdoc-project/strictdoc/pull/767) ([stanislaw](https://github.com/stanislaw))
- docs: update contributing and development guides [\#766](https://github.com/strictdoc-project/strictdoc/pull/766) ([stanislaw](https://github.com/stanislaw))
-  server: trim all form fields, remove trailing whitespace  [\#765](https://github.com/strictdoc-project/strictdoc/pull/765) ([stanislaw](https://github.com/stanislaw))
-  docs: updates related to the new server work  [\#763](https://github.com/strictdoc-project/strictdoc/pull/763) ([stanislaw](https://github.com/stanislaw))
- UI: Filtering text in single line contenteditable fields [\#762](https://github.com/strictdoc-project/strictdoc/pull/762) ([mettta](https://github.com/mettta))
- docs: renumber the documents  [\#761](https://github.com/strictdoc-project/strictdoc/pull/761) ([stanislaw](https://github.com/stanislaw))
- UI: give the connection status message a more solid look [\#760](https://github.com/strictdoc-project/strictdoc/pull/760) ([mettta](https://github.com/mettta))
- backend/sdoc/grammar: Add optional DocumentConfig CLASSIFICATION field [\#759](https://github.com/strictdoc-project/strictdoc/pull/759) ([GGBeer](https://github.com/GGBeer))
- server: initial Web-based GUI \(editing doc tree and documents\)  [\#758](https://github.com/strictdoc-project/strictdoc/pull/758) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc/grammar: Add GRAMMAR for REFS-TypeValue variant [\#754](https://github.com/strictdoc-project/strictdoc/pull/754) ([GGBeer](https://github.com/GGBeer))

## [0.0.29](https://github.com/strictdoc-project/strictdoc/tree/0.0.29) (2022-12-05)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.28...0.0.29)

**Fixed bugs:**

- pip image for 0.0.27 missing requirements.txt [\#751](https://github.com/strictdoc-project/strictdoc/issues/751)

**Merged pull requests:**

- Bump version to 0.0.29 [\#757](https://github.com/strictdoc-project/strictdoc/pull/757) ([stanislaw](https://github.com/stanislaw))
- export/rst: fix case when requirements do not have titles [\#756](https://github.com/strictdoc-project/strictdoc/pull/756) ([stanislaw](https://github.com/stanislaw))

## [0.0.28](https://github.com/strictdoc-project/strictdoc/tree/0.0.28) (2022-11-30)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.27...0.0.28)

**Closed issues:**

- Create SDocObjectFactory to unify how the objects are created from non-grammar sources. [\#529](https://github.com/strictdoc-project/strictdoc/issues/529)

**Merged pull requests:**

- setup.py: fix issue with packaging requirements.txt file [\#752](https://github.com/strictdoc-project/strictdoc/pull/752) ([stanislaw](https://github.com/stanislaw))
- docs: minor updates to the contribution guideline [\#750](https://github.com/strictdoc-project/strictdoc/pull/750) ([stanislaw](https://github.com/stanislaw))
- Trivial refactoring of has/get\_children\_requirements and has/get\_pare… [\#749](https://github.com/strictdoc-project/strictdoc/pull/749) ([GGBeer](https://github.com/GGBeer))
- Use constants instead of hardcoded Requirement-Fieldname strings. [\#748](https://github.com/strictdoc-project/strictdoc/pull/748) ([GGBeer](https://github.com/GGBeer))
- Regenerate CHANGELOG [\#747](https://github.com/strictdoc-project/strictdoc/pull/747) ([stanislaw](https://github.com/stanislaw))

## [0.0.27](https://github.com/strictdoc-project/strictdoc/tree/0.0.27) (2022-11-27)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.26...0.0.27)

**Fixed bugs:**

- Bug: Left panel on the \_source\_file screen should always be open [\#713](https://github.com/strictdoc-project/strictdoc/issues/713)

**Closed issues:**

- Problem with Pyinstaller [\#740](https://github.com/strictdoc-project/strictdoc/issues/740)
- MathJax fonts not always synced [\#723](https://github.com/strictdoc-project/strictdoc/issues/723)
- Feature: HTML export: TBL improvement: switch to a wide Excel-like table [\#710](https://github.com/strictdoc-project/strictdoc/issues/710)
- Display document's meta information: UID and Version [\#480](https://github.com/strictdoc-project/strictdoc/issues/480)
- Recursive copying of assets from the output folders [\#456](https://github.com/strictdoc-project/strictdoc/issues/456)

**Merged pull requests:**

- Bump version to 0.0.27 [\#746](https://github.com/strictdoc-project/strictdoc/pull/746) ([stanislaw](https://github.com/stanislaw))
- docs: update Discord link [\#745](https://github.com/strictdoc-project/strictdoc/pull/745) ([stanislaw](https://github.com/stanislaw))
-  tasks: enable installation using PyInstaller  [\#744](https://github.com/strictdoc-project/strictdoc/pull/744) ([stanislaw](https://github.com/stanislaw))
- CI: remove last job with Python 3.6 [\#743](https://github.com/strictdoc-project/strictdoc/pull/743) ([stanislaw](https://github.com/stanislaw))
- traceability\_index: remove no longer used code: max depth count [\#739](https://github.com/strictdoc-project/strictdoc/pull/739) ([stanislaw](https://github.com/stanislaw))
- traceability\_index: annotate variables with numbers for readability [\#738](https://github.com/strictdoc-project/strictdoc/pull/738) ([stanislaw](https://github.com/stanislaw))
- models/document: remove deprecated "NAME:" field [\#737](https://github.com/strictdoc-project/strictdoc/pull/737) ([stanislaw](https://github.com/stanislaw))
- tests/integration: exercise the fix of incremental copying of assets [\#736](https://github.com/strictdoc-project/strictdoc/pull/736) ([stanislaw](https://github.com/stanislaw))
- CI: try 3.11 on macOS and Linux jobs [\#735](https://github.com/strictdoc-project/strictdoc/pull/735) ([stanislaw](https://github.com/stanislaw))
-     CI: Fix Python 3.10 and 3.11 issues [\#734](https://github.com/strictdoc-project/strictdoc/pull/734) ([stanislaw](https://github.com/stanislaw))
- Code climate: html\_generator: remove dead code [\#733](https://github.com/strictdoc-project/strictdoc/pull/733) ([stanislaw](https://github.com/stanislaw))
- traceability\_index: refactoring: split building index and generating docs [\#732](https://github.com/strictdoc-project/strictdoc/pull/732) ([stanislaw](https://github.com/stanislaw))
- traceability\_index: refactoring: bring in all data from the generators [\#731](https://github.com/strictdoc-project/strictdoc/pull/731) ([stanislaw](https://github.com/stanislaw))
- export\_action: refactoring: clean up ExportCommandConfig [\#730](https://github.com/strictdoc-project/strictdoc/pull/730) ([stanislaw](https://github.com/stanislaw))
- export\_action: refactoring: no need to pass an extra path argument [\#729](https://github.com/strictdoc-project/strictdoc/pull/729) ([stanislaw](https://github.com/stanislaw))
- cli: minor improvement in strictdoc's root path handling [\#727](https://github.com/strictdoc-project/strictdoc/pull/727) ([stanislaw](https://github.com/stanislaw))
- requirements: remove \<3.0 limitation on jinja2 [\#726](https://github.com/strictdoc-project/strictdoc/pull/726) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate Read the Docs [\#724](https://github.com/strictdoc-project/strictdoc/pull/724) ([stanislaw](https://github.com/stanislaw))
- Use raw directive for tex instead of double escaping [\#722](https://github.com/strictdoc-project/strictdoc/pull/722) ([lochsh](https://github.com/lochsh))

## [0.0.26](https://github.com/strictdoc-project/strictdoc/tree/0.0.26) (2022-06-20)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.25...0.0.26)

**Fixed bugs:**

- Bug: AttributeError: 'NoneType' object has no attribute 'required' [\#675](https://github.com/strictdoc-project/strictdoc/issues/675)
- bugfix: AttributeError: 'NoneType' object has no attribute 'required' [\#699](https://github.com/strictdoc-project/strictdoc/pull/699) ([stanislaw](https://github.com/stanislaw))

**Closed issues:**

- PyLint issue: Cyclic import \(strictdoc.backend.sdoc.processor -\> strictdoc.backend.sdoc.reader\) \(cyclic-import\) [\#681](https://github.com/strictdoc-project/strictdoc/issues/681)
- Windows support: known issues [\#491](https://github.com/strictdoc-project/strictdoc/issues/491)
- Option: support two types of documents: requirements with titles and requirements with no titles [\#462](https://github.com/strictdoc-project/strictdoc/issues/462)
- Option: Include/exclude requirements in TOC [\#365](https://github.com/strictdoc-project/strictdoc/issues/365)

**Merged pull requests:**

- Bump version to 0.0.26 [\#721](https://github.com/strictdoc-project/strictdoc/pull/721) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate Read the Docs [\#720](https://github.com/strictdoc-project/strictdoc/pull/720) ([stanislaw](https://github.com/stanislaw))
- export/HTML:  fixing white background cutoff in the table view [\#719](https://github.com/strictdoc-project/strictdoc/pull/719) ([mettta](https://github.com/mettta))
- export/HTML: Fixing left panel \(TOC\) behavior [\#718](https://github.com/strictdoc-project/strictdoc/pull/718) ([mettta](https://github.com/mettta))
- export/HTML: Isolate CSS for .content-view-table [\#717](https://github.com/strictdoc-project/strictdoc/pull/717) ([mettta](https://github.com/mettta))
- export/HTML: Fix white stripe above the table in table-view [\#716](https://github.com/strictdoc-project/strictdoc/pull/716) ([mettta](https://github.com/mettta))
- UI: ultimate table view [\#715](https://github.com/strictdoc-project/strictdoc/pull/715) ([mettta](https://github.com/mettta))
- docs: FAQ: add FRET and blog posts about StrictDoc [\#714](https://github.com/strictdoc-project/strictdoc/pull/714) ([stanislaw](https://github.com/stanislaw))
- docs: extract F.A.Q. to a separate document [\#712](https://github.com/strictdoc-project/strictdoc/pull/712) ([stanislaw](https://github.com/stanislaw))
- export/HTML: add document META to table view [\#709](https://github.com/strictdoc-project/strictdoc/pull/709) ([mettta](https://github.com/mettta))
- docs: move CONTRIBUTING to .sdoc [\#708](https://github.com/strictdoc-project/strictdoc/pull/708) ([stanislaw](https://github.com/stanislaw))
-  export/HTML: add document META to document view  [\#707](https://github.com/strictdoc-project/strictdoc/pull/707) ([mettta](https://github.com/mettta))
- grammar: document\_config: expose has\_meta\(\) [\#706](https://github.com/strictdoc-project/strictdoc/pull/706) ([stanislaw](https://github.com/stanislaw))
- export/HTML: UI: fix grid in .table-view \> .requirement\_meta [\#705](https://github.com/strictdoc-project/strictdoc/pull/705) ([mettta](https://github.com/mettta))
- tasks: fix dead links task [\#704](https://github.com/strictdoc-project/strictdoc/pull/704) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc: fix handling of LEVEL: None for composite requirements [\#703](https://github.com/strictdoc-project/strictdoc/pull/703) ([stanislaw](https://github.com/stanislaw))
- tasks: switch to python3 everywhere for now [\#702](https://github.com/strictdoc-project/strictdoc/pull/702) ([stanislaw](https://github.com/stanislaw))
- export/HTML: UI: the title is no longer a required field [\#701](https://github.com/strictdoc-project/strictdoc/pull/701) ([mettta](https://github.com/mettta))
- tasks: experimental "watch" task [\#700](https://github.com/strictdoc-project/strictdoc/pull/700) ([stanislaw](https://github.com/stanislaw))
-  Code climate: fix cyclic import in strictdoc.backend.sdoc.processor  [\#697](https://github.com/strictdoc-project/strictdoc/pull/697) ([stanislaw](https://github.com/stanislaw))
- grammar: REQUIREMENT\_HAS\_TITLE -\> REQUIREMENT\_IN\_TOC [\#696](https://github.com/strictdoc-project/strictdoc/pull/696) ([stanislaw](https://github.com/stanislaw))
- grammar: New option: REQUIREMENT\_HAS\_TITLE [\#695](https://github.com/strictdoc-project/strictdoc/pull/695) ([stanislaw](https://github.com/stanislaw))

## [0.0.25](https://github.com/strictdoc-project/strictdoc/tree/0.0.25) (2022-05-08)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.23...0.0.25)

**Fixed bugs:**

- Possible bug: flaky test in incremental\_generation/03\_when\_new\_child\_generate\_parents [\#665](https://github.com/strictdoc-project/strictdoc/issues/665)

**Closed issues:**

- Ordered list incorrect html rendering [\#653](https://github.com/strictdoc-project/strictdoc/issues/653)
- Jinja2 template not found \(HTML export\) [\#652](https://github.com/strictdoc-project/strictdoc/issues/652)
- Unnumbered sections [\#639](https://github.com/strictdoc-project/strictdoc/issues/639)

**Merged pull requests:**

-  docs: update documentation, introduce design document  [\#694](https://github.com/strictdoc-project/strictdoc/pull/694) ([stanislaw](https://github.com/stanislaw))
- tests/integration: move away from a grep-based test [\#693](https://github.com/strictdoc-project/strictdoc/pull/693) ([stanislaw](https://github.com/stanislaw))
- file traceability: improve handling of Windows-style paths [\#692](https://github.com/strictdoc-project/strictdoc/pull/692) ([stanislaw](https://github.com/stanislaw))
- tasks: on Windows: detect if Bash is available  [\#691](https://github.com/strictdoc-project/strictdoc/pull/691) ([stanislaw](https://github.com/stanislaw))
- tests/integration: improve rm.py [\#690](https://github.com/strictdoc-project/strictdoc/pull/690) ([stanislaw](https://github.com/stanislaw))
- export/html: integration test for UTF8 symbols in SDoc [\#689](https://github.com/strictdoc-project/strictdoc/pull/689) ([stanislaw](https://github.com/stanislaw))
- tests/integration: Python version of 'cp' and 'rm' to make them portable [\#688](https://github.com/strictdoc-project/strictdoc/pull/688) ([stanislaw](https://github.com/stanislaw))
- tests/integration: Python version of 'touch' and 'mkdir' to make them portable  [\#687](https://github.com/strictdoc-project/strictdoc/pull/687) ([stanislaw](https://github.com/stanislaw))
- tests/integration: Python version of cat to make it portable [\#686](https://github.com/strictdoc-project/strictdoc/pull/686) ([stanislaw](https://github.com/stanislaw))
-  tasks and tests/integration: portable clean, %cat, and %diff  [\#685](https://github.com/strictdoc-project/strictdoc/pull/685) ([stanislaw](https://github.com/stanislaw))
- export/html: link\_renderer: always print forward slashes \(Windows\) [\#684](https://github.com/strictdoc-project/strictdoc/pull/684) ([stanislaw](https://github.com/stanislaw))
- tasks: check\_environment: un-hardcode python3 because it fails on Windows [\#683](https://github.com/strictdoc-project/strictdoc/pull/683) ([stanislaw](https://github.com/stanislaw))
- tasks: fix the "The command line is too long." issue on Windows [\#682](https://github.com/strictdoc-project/strictdoc/pull/682) ([stanislaw](https://github.com/stanislaw))
- export/html: table-based requirement template  [\#680](https://github.com/strictdoc-project/strictdoc/pull/680) ([stanislaw](https://github.com/stanislaw))
- traceability: simplify handling of source file paths [\#679](https://github.com/strictdoc-project/strictdoc/pull/679) ([stanislaw](https://github.com/stanislaw))
- traceability: source\_files\_finder: ignored\_dirs argument and unit test [\#678](https://github.com/strictdoc-project/strictdoc/pull/678) ([stanislaw](https://github.com/stanislaw))
- HTML export improvements [\#677](https://github.com/strictdoc-project/strictdoc/pull/677) ([BenGardiner](https://github.com/BenGardiner))
- developer/design: add a sketch \(Affinity Design\) [\#676](https://github.com/strictdoc-project/strictdoc/pull/676) ([stanislaw](https://github.com/stanislaw))
- docs: small update in the dev plan [\#674](https://github.com/strictdoc-project/strictdoc/pull/674) ([stanislaw](https://github.com/stanislaw))
- excel/import: optional title for imported documents [\#673](https://github.com/strictdoc-project/strictdoc/pull/673) ([BenGardiner](https://github.com/BenGardiner))
- Code climate: tests/integration: prepare test folders [\#672](https://github.com/strictdoc-project/strictdoc/pull/672) ([stanislaw](https://github.com/stanislaw))
- Code climate: try \* to enforce named parameters [\#671](https://github.com/strictdoc-project/strictdoc/pull/671) ([stanislaw](https://github.com/stanislaw))
- Code climate: mypy: fix the "assignment" errors [\#670](https://github.com/strictdoc-project/strictdoc/pull/670) ([stanislaw](https://github.com/stanislaw))
- Code climate: mypy: enable --strict and disable remaining checks [\#669](https://github.com/strictdoc-project/strictdoc/pull/669) ([stanislaw](https://github.com/stanislaw))
- requirements.txt: constraint most of the deps to the same major version [\#668](https://github.com/strictdoc-project/strictdoc/pull/668) ([stanislaw](https://github.com/stanislaw))
- backend/excel: keep import and export together [\#667](https://github.com/strictdoc-project/strictdoc/pull/667) ([stanislaw](https://github.com/stanislaw))
- tasks: stop using @task for cleaning the itest artifacts [\#666](https://github.com/strictdoc-project/strictdoc/pull/666) ([stanislaw](https://github.com/stanislaw))
- tasks: do not reset the PATH when running sphinx task [\#664](https://github.com/strictdoc-project/strictdoc/pull/664) ([stanislaw](https://github.com/stanislaw))
- tasks: reset PATH when running from virtual environments [\#663](https://github.com/strictdoc-project/strictdoc/pull/663) ([stanislaw](https://github.com/stanislaw))
- feature: import excel [\#662](https://github.com/strictdoc-project/strictdoc/pull/662) ([BenGardiner](https://github.com/BenGardiner))
- docs: extract goals to the development plan draft [\#661](https://github.com/strictdoc-project/strictdoc/pull/661) ([stanislaw](https://github.com/stanislaw))
- requirements.txt: relax all dependencies to \>= [\#660](https://github.com/strictdoc-project/strictdoc/pull/660) ([stanislaw](https://github.com/stanislaw))
- requirements.development.txt: relax all dependencies to \>= [\#659](https://github.com/strictdoc-project/strictdoc/pull/659) ([stanislaw](https://github.com/stanislaw))
- tasks: fix dead links task [\#658](https://github.com/strictdoc-project/strictdoc/pull/658) ([stanislaw](https://github.com/stanislaw))
- docs: split the documents: User Manual, Requirements and Backlog [\#657](https://github.com/strictdoc-project/strictdoc/pull/657) ([stanislaw](https://github.com/stanislaw))
- CI: set up correct dependencies for periodic checking of dead links [\#656](https://github.com/strictdoc-project/strictdoc/pull/656) ([stanislaw](https://github.com/stanislaw))
- Code climate: improve css fix html rendering for ordered list [\#654](https://github.com/strictdoc-project/strictdoc/pull/654) ([gioboske](https://github.com/gioboske))
- export/html: support sections without a level [\#651](https://github.com/strictdoc-project/strictdoc/pull/651) ([stanislaw](https://github.com/stanislaw))

## [0.0.23](https://github.com/strictdoc-project/strictdoc/tree/0.0.23) (2022-04-05)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.22...0.0.23)

**Closed issues:**

- Establish workflow for pre-releases [\#597](https://github.com/strictdoc-project/strictdoc/issues/597)

**Merged pull requests:**

- setup.py: fix copying of the HTML files [\#655](https://github.com/strictdoc-project/strictdoc/pull/655) ([stanislaw](https://github.com/stanislaw))

## [0.0.22](https://github.com/strictdoc-project/strictdoc/tree/0.0.22) (2022-04-03)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.21...0.0.22)

**Fixed bugs:**

- tasks: fix broken mypy task [\#636](https://github.com/strictdoc-project/strictdoc/pull/636) ([stanislaw](https://github.com/stanislaw))

**Closed issues:**

- Hello World example seems broken [\#641](https://github.com/strictdoc-project/strictdoc/issues/641)
- Enhancement: docs: checking of dead links [\#570](https://github.com/strictdoc-project/strictdoc/issues/570)

**Merged pull requests:**

- docs/sphinx/source/conf.py: remove assert that breaks with readthedocs [\#650](https://github.com/strictdoc-project/strictdoc/pull/650) ([stanislaw](https://github.com/stanislaw))
- docs: update Docker instructions [\#649](https://github.com/strictdoc-project/strictdoc/pull/649) ([stanislaw](https://github.com/stanislaw))
- docs: document the new development workflow without Poetry [\#648](https://github.com/strictdoc-project/strictdoc/pull/648) ([stanislaw](https://github.com/stanislaw))
- CI: daily integration test [\#647](https://github.com/strictdoc-project/strictdoc/pull/647) ([stanislaw](https://github.com/stanislaw))
- tasks: make the venv types explicit [\#646](https://github.com/strictdoc-project/strictdoc/pull/646) ([stanislaw](https://github.com/stanislaw))
- tasks: "release" task [\#645](https://github.com/strictdoc-project/strictdoc/pull/645) ([stanislaw](https://github.com/stanislaw))
- setup.py: include requirements.txt to the egg [\#644](https://github.com/strictdoc-project/strictdoc/pull/644) ([stanislaw](https://github.com/stanislaw))
- Bump version to 0.0.22a1 [\#643](https://github.com/strictdoc-project/strictdoc/pull/643) ([stanislaw](https://github.com/stanislaw))
- tasks: simplify setting up dependencies [\#642](https://github.com/strictdoc-project/strictdoc/pull/642) ([stanislaw](https://github.com/stanislaw))
- tasks: replace Poetry with plain setup.py [\#640](https://github.com/strictdoc-project/strictdoc/pull/640) ([stanislaw](https://github.com/stanislaw))
- link\_health: check dead links in strict.sdoc [\#638](https://github.com/strictdoc-project/strictdoc/pull/638) ([stanislaw](https://github.com/stanislaw))
- Poetry: upgrade and update requirements.txt [\#637](https://github.com/strictdoc-project/strictdoc/pull/637) ([stanislaw](https://github.com/stanislaw))
- tasks: reduce repetition of "one\_line\_command" [\#635](https://github.com/strictdoc-project/strictdoc/pull/635) ([stanislaw](https://github.com/stanislaw))
- requirement: use multiline value for None values in meta fields [\#633](https://github.com/strictdoc-project/strictdoc/pull/633) ([BenGardiner](https://github.com/BenGardiner))
- Code climate: remove unused code "ng\_sections" [\#631](https://github.com/strictdoc-project/strictdoc/pull/631) ([stanislaw](https://github.com/stanislaw))
- new feature FRAGMENT\_FROM\_FILE [\#629](https://github.com/strictdoc-project/strictdoc/pull/629) ([BenGardiner](https://github.com/BenGardiner))
- tasks: tests-unit: allow running in focused mode [\#628](https://github.com/strictdoc-project/strictdoc/pull/628) ([stanislaw](https://github.com/stanislaw))

## [0.0.21](https://github.com/strictdoc-project/strictdoc/tree/0.0.21) (2022-03-07)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.20...0.0.21)

**Fixed bugs:**

- Enhancement: Custom grammars: "Hint: Requirement fields" should point to the grammar fields, not requirement's fields [\#625](https://github.com/strictdoc-project/strictdoc/issues/625)

**Closed issues:**

- Can we update to newer jinja2? [\#622](https://github.com/strictdoc-project/strictdoc/issues/622)

**Merged pull requests:**

- Bump version to 0.0.21 [\#627](https://github.com/strictdoc-project/strictdoc/pull/627) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc: custom grammar: fix an unimplemented aspect [\#626](https://github.com/strictdoc-project/strictdoc/pull/626) ([stanislaw](https://github.com/stanislaw))

## [0.0.20](https://github.com/strictdoc-project/strictdoc/tree/0.0.20) (2022-02-24)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.19...0.0.20)

**Closed issues:**

- Support for ReqIFz import [\#592](https://github.com/strictdoc-project/strictdoc/issues/592)
- SDoc to Reqif conversion not implemented yet [\#582](https://github.com/strictdoc-project/strictdoc/issues/582)
- Homebrew packaging [\#578](https://github.com/strictdoc-project/strictdoc/issues/578)

**Merged pull requests:**

- Bump version to 0.0.20 [\#624](https://github.com/strictdoc-project/strictdoc/pull/624) ([stanislaw](https://github.com/stanislaw))
- Relax version spec for jinja2 [\#623](https://github.com/strictdoc-project/strictdoc/pull/623) ([lochsh](https://github.com/lochsh))
- traceability: support linking Tex files to requirements  [\#620](https://github.com/strictdoc-project/strictdoc/pull/620) ([cbernt](https://github.com/cbernt))
- docs: remove a dead link [\#619](https://github.com/strictdoc-project/strictdoc/pull/619) ([stanislaw](https://github.com/stanislaw))
-  Code climate: backend/reqif: more consistent class naming  [\#618](https://github.com/strictdoc-project/strictdoc/pull/618) ([stanislaw](https://github.com/stanislaw))
- backend/reqif: export/import roundtrip: parent-child links [\#617](https://github.com/strictdoc-project/strictdoc/pull/617) ([stanislaw](https://github.com/stanislaw))
- Regenerate CHANGELOG [\#614](https://github.com/strictdoc-project/strictdoc/pull/614) ([stanislaw](https://github.com/stanislaw))

## [0.0.19](https://github.com/strictdoc-project/strictdoc/tree/0.0.19) (2022-02-13)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.18...0.0.19)

**Closed issues:**

- Add version subcommand [\#583](https://github.com/strictdoc-project/strictdoc/issues/583)
- Snap package [\#573](https://github.com/strictdoc-project/strictdoc/issues/573)
- Dockerized strictdoc [\#562](https://github.com/strictdoc-project/strictdoc/issues/562)

**Merged pull requests:**

- Bump version to 0.0.19 [\#613](https://github.com/strictdoc-project/strictdoc/pull/613) ([stanislaw](https://github.com/stanislaw))
- Code climate: remove archive/ for good [\#612](https://github.com/strictdoc-project/strictdoc/pull/612) ([stanislaw](https://github.com/stanislaw))
- grammar and \*: remove obsolete BODY and last artefacts of SPECIAL\_FIELDS [\#611](https://github.com/strictdoc-project/strictdoc/pull/611) ([stanislaw](https://github.com/stanislaw))
- docs: document experimental requirements to source code traceability [\#610](https://github.com/strictdoc-project/strictdoc/pull/610) ([stanislaw](https://github.com/stanislaw))
- docs: remove sandbox, introduce examples [\#609](https://github.com/strictdoc-project/strictdoc/pull/609) ([stanislaw](https://github.com/stanislaw))
- DocumentFinder: do not look for .sdoc files in the output/ folder [\#608](https://github.com/strictdoc-project/strictdoc/pull/608) ([stanislaw](https://github.com/stanislaw))
-  grammar: remove SPECIAL\_FIELDS support from everywhere  [\#607](https://github.com/strictdoc-project/strictdoc/pull/607) ([stanislaw](https://github.com/stanislaw))
- Code climate: archive the unused FmStudio code [\#606](https://github.com/strictdoc-project/strictdoc/pull/606) ([stanislaw](https://github.com/stanislaw))
-  reqif: minor cleanup using .create\(\) methods  [\#605](https://github.com/strictdoc-project/strictdoc/pull/605) ([stanislaw](https://github.com/stanislaw))
- minor: replace all FREE\_TEXT with FREETEXT [\#603](https://github.com/strictdoc-project/strictdoc/pull/603) ([BenGardiner](https://github.com/BenGardiner))
- backend/reqif: export SPECIFICATION-TYPE [\#600](https://github.com/strictdoc-project/strictdoc/pull/600) ([stanislaw](https://github.com/stanislaw))
- backend/reqif: export REQ-IF-HEADER with basic info about strictdoc [\#599](https://github.com/strictdoc-project/strictdoc/pull/599) ([stanislaw](https://github.com/stanislaw))
- reqif: upgrade to 0.0.13 [\#596](https://github.com/strictdoc-project/strictdoc/pull/596) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc: support multiline fields with empty string values [\#595](https://github.com/strictdoc-project/strictdoc/pull/595) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc and export/html: remove legacy BODY field [\#594](https://github.com/strictdoc-project/strictdoc/pull/594) ([stanislaw](https://github.com/stanislaw))
- backend/sdoc: support fields with empty string values [\#593](https://github.com/strictdoc-project/strictdoc/pull/593) ([stanislaw](https://github.com/stanislaw))
- backend/reqif: convert SDoc's COMMENT to ReqIF's NOTES and vice versa [\#586](https://github.com/strictdoc-project/strictdoc/pull/586) ([stanislaw](https://github.com/stanislaw))
- backend/reqif: make export/import follow some of the ReqIF guideline [\#585](https://github.com/strictdoc-project/strictdoc/pull/585) ([stanislaw](https://github.com/stanislaw))
- cli: add "version" command [\#584](https://github.com/strictdoc-project/strictdoc/pull/584) ([fkromer](https://github.com/fkromer))
- Create CONTRIBUTING.md [\#576](https://github.com/strictdoc-project/strictdoc/pull/576) ([stanislaw](https://github.com/stanislaw))
- add docker usage info to documentation [\#575](https://github.com/strictdoc-project/strictdoc/pull/575) ([fkromer](https://github.com/fkromer))
- add snap package [\#574](https://github.com/strictdoc-project/strictdoc/pull/574) ([fkromer](https://github.com/fkromer))
- add Dockerfile for dockerization of strictdoc [\#572](https://github.com/strictdoc-project/strictdoc/pull/572) ([fkromer](https://github.com/fkromer))

## [0.0.18](https://github.com/strictdoc-project/strictdoc/tree/0.0.18) (2022-01-01)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.17...0.0.18)

**Closed issues:**

- Reference to grammar in docs is broken [\#564](https://github.com/strictdoc-project/strictdoc/issues/564)

**Merged pull requests:**

- Bump version to 0.0.18 [\#568](https://github.com/strictdoc-project/strictdoc/pull/568) ([stanislaw](https://github.com/stanislaw))
- docs: fix links to the grammar.py and regenerate the docs [\#567](https://github.com/strictdoc-project/strictdoc/pull/567) ([stanislaw](https://github.com/stanislaw))
- docs: document ReqIF export/import workflows [\#565](https://github.com/strictdoc-project/strictdoc/pull/565) ([stanislaw](https://github.com/stanislaw))
- reqif: native: export/import roundtrip for multiline requirement fields [\#560](https://github.com/strictdoc-project/strictdoc/pull/560) ([stanislaw](https://github.com/stanislaw))
- reqif: native: export/import roundtrip for SECTION.FREETEXT [\#559](https://github.com/strictdoc-project/strictdoc/pull/559) ([stanislaw](https://github.com/stanislaw))
- reqif/export: case when requirement is lower-level than previous section [\#558](https://github.com/strictdoc-project/strictdoc/pull/558) ([stanislaw](https://github.com/stanislaw))
- reqif/export: case when requirement is lower-level than previous section [\#557](https://github.com/strictdoc-project/strictdoc/pull/557) ([stanislaw](https://github.com/stanislaw))
-  cli: dump-grammar command  [\#556](https://github.com/strictdoc-project/strictdoc/pull/556) ([stanislaw](https://github.com/stanislaw))
-  reqif: first integration and ReqIF-SDoc end-to-end tests  [\#555](https://github.com/strictdoc-project/strictdoc/pull/555) ([stanislaw](https://github.com/stanislaw))
- Poetry: integrate reqif 0.0.1 [\#554](https://github.com/strictdoc-project/strictdoc/pull/554) ([stanislaw](https://github.com/stanislaw))
- tasks: remove obsolete second Pylint task [\#553](https://github.com/strictdoc-project/strictdoc/pull/553) ([stanislaw](https://github.com/stanislaw))
- backend/dsl: support custom grammars and a basic type system [\#552](https://github.com/strictdoc-project/strictdoc/pull/552) ([stanislaw](https://github.com/stanislaw))
- backend/dsl: more 'passthrough' tests for new types [\#551](https://github.com/strictdoc-project/strictdoc/pull/551) ([stanislaw](https://github.com/stanislaw))
- backend/dsl: support grammar fields: SingleChoice, MultipleChoice, Tag [\#550](https://github.com/strictdoc-project/strictdoc/pull/550) ([stanislaw](https://github.com/stanislaw))
- backend/dsl: switch to dynamic fields, with validation [\#549](https://github.com/strictdoc-project/strictdoc/pull/549) ([stanislaw](https://github.com/stanislaw))
- backend/dsl/writer: print based on type information, not hardcoded [\#548](https://github.com/strictdoc-project/strictdoc/pull/548) ([stanislaw](https://github.com/stanislaw))
- backend/dsl: extract parsing processing to a separate class [\#547](https://github.com/strictdoc-project/strictdoc/pull/547) ([stanislaw](https://github.com/stanislaw))
- Code climate: introduce code coverage calculation [\#543](https://github.com/strictdoc-project/strictdoc/pull/543) ([stanislaw](https://github.com/stanislaw))
- Code climate: set Pylint target to 10.0 [\#542](https://github.com/strictdoc-project/strictdoc/pull/542) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix all remaining major Pylint warnings [\#541](https://github.com/strictdoc-project/strictdoc/pull/541) ([stanislaw](https://github.com/stanislaw))
- imports/reqif: REQIF.SPECIFICATION.LONG-NAME -\> SDOC.DOCUMENT.TITLE [\#540](https://github.com/strictdoc-project/strictdoc/pull/540) ([stanislaw](https://github.com/stanislaw))
- import/reqif: Doors parser: parse bullet point-based subreqs [\#539](https://github.com/strictdoc-project/strictdoc/pull/539) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix several Pylint warnings [\#538](https://github.com/strictdoc-project/strictdoc/pull/538) ([stanislaw](https://github.com/stanislaw))
- imports/reqif: Doors parser: initial parsing of images [\#537](https://github.com/strictdoc-project/strictdoc/pull/537) ([stanislaw](https://github.com/stanislaw))
- Code climate: mypy: make explicit which checks are enabled/disabled [\#536](https://github.com/strictdoc-project/strictdoc/pull/536) ([stanislaw](https://github.com/stanislaw))
- Code climate: introduce basic mypy checking [\#535](https://github.com/strictdoc-project/strictdoc/pull/535) ([stanislaw](https://github.com/stanislaw))
- import/reqif: native parser: parse custom fields [\#534](https://github.com/strictdoc-project/strictdoc/pull/534) ([stanislaw](https://github.com/stanislaw))
- Code climate: Fix strict Pylint warnings for newly added modules [\#533](https://github.com/strictdoc-project/strictdoc/pull/533) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix Pylint: W0235, W0613 [\#532](https://github.com/strictdoc-project/strictdoc/pull/532) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix Pylint: W0703, W0231 [\#531](https://github.com/strictdoc-project/strictdoc/pull/531) ([stanislaw](https://github.com/stanislaw))
- import/reqif: parsing SpecRelation [\#530](https://github.com/strictdoc-project/strictdoc/pull/530) ([stanislaw](https://github.com/stanislaw))
-  tests/unit: group stage1 parser-related tests  [\#528](https://github.com/strictdoc-project/strictdoc/pull/528) ([stanislaw](https://github.com/stanislaw))
- import/reqif: Doors parser: parse tables stored as XHTML fields [\#527](https://github.com/strictdoc-project/strictdoc/pull/527) ([stanislaw](https://github.com/stanislaw))
- grammar and export/html: document markup option: HTML fragment writer [\#526](https://github.com/strictdoc-project/strictdoc/pull/526) ([stanislaw](https://github.com/stanislaw))
-  reqif: switch to selecting parser via an argument  [\#525](https://github.com/strictdoc-project/strictdoc/pull/525) ([stanislaw](https://github.com/stanislaw))
- Code climate: pylint: fix C1801 [\#524](https://github.com/strictdoc-project/strictdoc/pull/524) ([stanislaw](https://github.com/stanislaw))
- tasks: make pylint always be 10.0 for whitelisted fixed warnings [\#523](https://github.com/strictdoc-project/strictdoc/pull/523) ([stanislaw](https://github.com/stanislaw))
- grammar: introduce \[DOCUMENT\].OPTIONS.AUTO\_LEVELS [\#522](https://github.com/strictdoc-project/strictdoc/pull/522) ([stanislaw](https://github.com/stanislaw))
- import/reqif: from ReqIF to SDoc: initial implementation [\#521](https://github.com/strictdoc-project/strictdoc/pull/521) ([stanislaw](https://github.com/stanislaw))
- grammar: improve handling of the multiline fields [\#519](https://github.com/strictdoc-project/strictdoc/pull/519) ([stanislaw](https://github.com/stanislaw))
- backend/source\_file\_syntax: simplify handling of the source lines [\#518](https://github.com/strictdoc-project/strictdoc/pull/518) ([stanislaw](https://github.com/stanislaw))
- Code climate: increase pylint limit again [\#517](https://github.com/strictdoc-project/strictdoc/pull/517) ([stanislaw](https://github.com/stanislaw))
- traceability: fix calculation of locations when there are empty source lines [\#516](https://github.com/strictdoc-project/strictdoc/pull/516) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix more pylint warnings [\#513](https://github.com/strictdoc-project/strictdoc/pull/513) ([stanislaw](https://github.com/stanislaw))
- Code climate: a few missing \_\_init\_\_.py's to prepare for mypy [\#512](https://github.com/strictdoc-project/strictdoc/pull/512) ([stanislaw](https://github.com/stanislaw))
- export/html: reuse markup renderer to improve performance [\#511](https://github.com/strictdoc-project/strictdoc/pull/511) ([stanislaw](https://github.com/stanislaw))
- export/html-standalone: embed favicon [\#509](https://github.com/strictdoc-project/strictdoc/pull/509) ([stanislaw](https://github.com/stanislaw))
- CI: Enable Python 3.10 [\#508](https://github.com/strictdoc-project/strictdoc/pull/508) ([stanislaw](https://github.com/stanislaw))

## [0.0.17](https://github.com/strictdoc-project/strictdoc/tree/0.0.17) (2021-10-21)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.16...0.0.17)

**Closed issues:**

- HTML not being regenerated correctly with multiple SDoc Files [\#494](https://github.com/strictdoc-project/strictdoc/issues/494)

**Merged pull requests:**

- CI: fix broken Poetry installation when Python 3.10 is used [\#507](https://github.com/strictdoc-project/strictdoc/pull/507) ([stanislaw](https://github.com/stanislaw))
- Bump version to 0.0.17 [\#506](https://github.com/strictdoc-project/strictdoc/pull/506) ([stanislaw](https://github.com/stanislaw))
- tests/integration: use sandbox approach to fix an incr. generation test [\#504](https://github.com/strictdoc-project/strictdoc/pull/504) ([stanislaw](https://github.com/stanislaw))
- export/html: regenerate all parent docs if new child is found  [\#503](https://github.com/strictdoc-project/strictdoc/pull/503) ([Relasym](https://github.com/Relasym))
- export/html: regenerate all parent docs if the child doc changes [\#501](https://github.com/strictdoc-project/strictdoc/pull/501) ([stanislaw](https://github.com/stanislaw))
- export: print how long it takes to collect the traceability info [\#500](https://github.com/strictdoc-project/strictdoc/pull/500) ([stanislaw](https://github.com/stanislaw))
- docs: add "Document archetypes" draft requirement [\#499](https://github.com/strictdoc-project/strictdoc/pull/499) ([stanislaw](https://github.com/stanislaw))
- export/html: regenerate all child docs if the parent doc changes [\#497](https://github.com/strictdoc-project/strictdoc/pull/497) ([stanislaw](https://github.com/stanislaw))
- traceability\_index: extract file traceability container to a separate file [\#496](https://github.com/strictdoc-project/strictdoc/pull/496) ([stanislaw](https://github.com/stanislaw))
- html, html-standalone, rst: fix UTF8 when stdout + reading and writing files [\#495](https://github.com/strictdoc-project/strictdoc/pull/495) ([stanislaw](https://github.com/stanislaw))
- docs: add "Contact developers" [\#493](https://github.com/strictdoc-project/strictdoc/pull/493) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate rst using the new file name convention [\#492](https://github.com/strictdoc-project/strictdoc/pull/492) ([stanislaw](https://github.com/stanislaw))
- traceability: \[nosdoc\] directive to disable requirements search in source files [\#490](https://github.com/strictdoc-project/strictdoc/pull/490) ([stanislaw](https://github.com/stanislaw))
- traceability: switch to UTF-8 when reading and generating source files [\#489](https://github.com/strictdoc-project/strictdoc/pull/489) ([stanislaw](https://github.com/stanislaw))
- CI: Remove Ubuntu 16 workflow [\#488](https://github.com/strictdoc-project/strictdoc/pull/488) ([stanislaw](https://github.com/stanislaw))
- Poetry: update FileCheck [\#487](https://github.com/strictdoc-project/strictdoc/pull/487) ([stanislaw](https://github.com/stanislaw))
- tests/integration: enable back the HTML markup test [\#486](https://github.com/strictdoc-project/strictdoc/pull/486) ([stanislaw](https://github.com/stanislaw))
- Create codeql-analysis.yml [\#485](https://github.com/strictdoc-project/strictdoc/pull/485) ([stanislaw](https://github.com/stanislaw))

## [0.0.16](https://github.com/strictdoc-project/strictdoc/tree/0.0.16) (2021-09-05)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.15...0.0.16)

**Merged pull requests:**

- docs: switch back to guzzle\_sphinx\_theme for better support by Read the Docs [\#484](https://github.com/strictdoc-project/strictdoc/pull/484) ([stanislaw](https://github.com/stanislaw))
- docs: switch to sphinx\_rtd\_theme for better support by Read the Docs [\#483](https://github.com/strictdoc-project/strictdoc/pull/483) ([stanislaw](https://github.com/stanislaw))
- Bump version to 0.0.16 [\#482](https://github.com/strictdoc-project/strictdoc/pull/482) ([stanislaw](https://github.com/stanislaw))
- docs: --project-title option [\#481](https://github.com/strictdoc-project/strictdoc/pull/481) ([stanislaw](https://github.com/stanislaw))
- docs: --project-title option [\#479](https://github.com/strictdoc-project/strictdoc/pull/479) ([stanislaw](https://github.com/stanislaw))
- export/html: config option --project-title and display project title [\#478](https://github.com/strictdoc-project/strictdoc/pull/478) ([stanislaw](https://github.com/stanislaw))
- pyproject: remove guzzle\_sphinx\_theme, switch theme to bizstyle [\#477](https://github.com/strictdoc-project/strictdoc/pull/477) ([stanislaw](https://github.com/stanislaw))
- traceability: validation: do not allow dangling inline links [\#476](https://github.com/strictdoc-project/strictdoc/pull/476) ([stanislaw](https://github.com/stanislaw))
- Feature: Inline links to Sections and Requirements [\#475](https://github.com/strictdoc-project/strictdoc/pull/475) ([stanislaw](https://github.com/stanislaw))

## [0.0.15](https://github.com/strictdoc-project/strictdoc/tree/0.0.15) (2021-08-19)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.14...0.0.15)

**Closed issues:**

- Document-level option to select or disable markup language \(RST vs plain text\) [\#465](https://github.com/strictdoc-project/strictdoc/issues/465)

**Merged pull requests:**

- Bump version to 0.0.15 [\#474](https://github.com/strictdoc-project/strictdoc/pull/474) ([stanislaw](https://github.com/stanislaw))
- export/html: fix section-title line-height [\#473](https://github.com/strictdoc-project/strictdoc/pull/473) ([mettta](https://github.com/mettta))
- export/html: stop decapitalizing custom field name in the meta table [\#472](https://github.com/strictdoc-project/strictdoc/pull/472) ([stanislaw](https://github.com/stanislaw))
- export/html: requirement meta: fix margins in traceability [\#471](https://github.com/strictdoc-project/strictdoc/pull/471) ([mettta](https://github.com/mettta))
- export/html: requirement meta: fix margins, fix background color in t… [\#470](https://github.com/strictdoc-project/strictdoc/pull/470) ([mettta](https://github.com/mettta))
- export/html: fix bottom border in requirement meta-table [\#469](https://github.com/strictdoc-project/strictdoc/pull/469) ([mettta](https://github.com/mettta))
- export/html: fix bottom border in requirement meta-table [\#468](https://github.com/strictdoc-project/strictdoc/pull/468) ([mettta](https://github.com/mettta))
- export/html: styles for table-view, update styles for requirement meta-table [\#467](https://github.com/strictdoc-project/strictdoc/pull/467) ([mettta](https://github.com/mettta))
- grammar: document-level option to specify markup \(RST and Text for now\) [\#466](https://github.com/strictdoc-project/strictdoc/pull/466) ([stanislaw](https://github.com/stanislaw))

## [0.0.14](https://github.com/strictdoc-project/strictdoc/tree/0.0.14) (2021-08-18)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.13...0.0.14)

**Merged pull requests:**

- Bump version to 0.0.14 [\#464](https://github.com/strictdoc-project/strictdoc/pull/464) ([stanislaw](https://github.com/stanislaw))
- Add pygments to pyproject.toml [\#463](https://github.com/strictdoc-project/strictdoc/pull/463) ([adamgreig](https://github.com/adamgreig))
- Regenerate CHANGELOG [\#461](https://github.com/strictdoc-project/strictdoc/pull/461) ([stanislaw](https://github.com/stanislaw))

## [0.0.13](https://github.com/strictdoc-project/strictdoc/tree/0.0.13) (2021-08-16)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.12...0.0.13)

**Closed issues:**

- traceability: improve resolution of full paths during validation checks [\#448](https://github.com/strictdoc-project/strictdoc/issues/448)

**Merged pull requests:**

- Bump version to 0.0.13 [\#460](https://github.com/strictdoc-project/strictdoc/pull/460) ([stanislaw](https://github.com/stanislaw))
- export/html: ignore "tests" when looking for \_assets for now [\#459](https://github.com/strictdoc-project/strictdoc/pull/459) ([stanislaw](https://github.com/stanislaw))
- export/html: update source-file-view, use micro requirement blocks [\#458](https://github.com/strictdoc-project/strictdoc/pull/458) ([mettta](https://github.com/mettta))
- export/html: fix reqs in table view, fix reqs width in deep-traceability view, make TR and DTR screens use the same requirement tree [\#457](https://github.com/strictdoc-project/strictdoc/pull/457) ([mettta](https://github.com/mettta))
- export/html: prevent recursive search of assets in the output directories [\#455](https://github.com/strictdoc-project/strictdoc/pull/455) ([stanislaw](https://github.com/stanislaw))
- export/html: improve path resolution for source-to-source links [\#454](https://github.com/strictdoc-project/strictdoc/pull/454) ([stanislaw](https://github.com/stanislaw))
-  export/html: improve handling of relative paths between reqs and files  [\#452](https://github.com/strictdoc-project/strictdoc/pull/452) ([stanislaw](https://github.com/stanislaw))
- traceability: fix the missing source file and requirement warnings [\#450](https://github.com/strictdoc-project/strictdoc/pull/450) ([stanislaw](https://github.com/stanislaw))
- traceability: simplify and improve source files grammar [\#449](https://github.com/strictdoc-project/strictdoc/pull/449) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate Read the Docs [\#446](https://github.com/strictdoc-project/strictdoc/pull/446) ([stanislaw](https://github.com/stanislaw))

## [0.0.12](https://github.com/strictdoc-project/strictdoc/tree/0.0.12) (2021-08-05)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.11...0.0.12)

**Closed issues:**

- Allow images to be displayed in output [\#445](https://github.com/strictdoc-project/strictdoc/issues/445)
- Include mathjax in HTML template to allow for TeX rendering in exported HTML [\#443](https://github.com/strictdoc-project/strictdoc/issues/443)
- export/html: the TOC does not work for sections or requirements with identical name [\#431](https://github.com/strictdoc-project/strictdoc/issues/431)

**Merged pull requests:**

- Bump version to 0.0.12 [\#447](https://github.com/strictdoc-project/strictdoc/pull/447) ([stanislaw](https://github.com/stanislaw))
- Add Mathjax to base HTML template to allow for TeX rendering [\#444](https://github.com/strictdoc-project/strictdoc/pull/444) ([lochsh](https://github.com/lochsh))
- Code climate: fix unnecessary lambda warning [\#442](https://github.com/strictdoc-project/strictdoc/pull/442) ([stanislaw](https://github.com/stanislaw))
- traceability: 2 validations of consistency of the req-source links [\#441](https://github.com/strictdoc-project/strictdoc/pull/441) ([stanislaw](https://github.com/stanislaw))
- Code climate: split: traceability\_index and traceability\_index\_builder [\#440](https://github.com/strictdoc-project/strictdoc/pull/440) ([stanislaw](https://github.com/stanislaw))
- traceability: extract and simplify cycle detection code [\#439](https://github.com/strictdoc-project/strictdoc/pull/439) ([stanislaw](https://github.com/stanislaw))
- traceability: detect cycles between requirements [\#438](https://github.com/strictdoc-project/strictdoc/pull/438) ([stanislaw](https://github.com/stanislaw))
-  export/html: add requirement-tree to traceability [\#437](https://github.com/strictdoc-project/strictdoc/pull/437) ([mettta](https://github.com/mettta))
- Regenerate CHANGELOG [\#436](https://github.com/strictdoc-project/strictdoc/pull/436) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix unnecessary lambda warning [\#435](https://github.com/strictdoc-project/strictdoc/pull/435) ([stanislaw](https://github.com/stanislaw))
- Code climate: fix several long line warnings from flake8 [\#434](https://github.com/strictdoc-project/strictdoc/pull/434) ([stanislaw](https://github.com/stanislaw))
- export/html: Sec and Req anchors section number to ensure link uniqueness [\#433](https://github.com/strictdoc-project/strictdoc/pull/433) ([stanislaw](https://github.com/stanislaw))
-  export/html: requirements and source coverage: correct links to source files  [\#432](https://github.com/strictdoc-project/strictdoc/pull/432) ([stanislaw](https://github.com/stanislaw))
- docs: add project-level config todo [\#430](https://github.com/strictdoc-project/strictdoc/pull/430) ([stanislaw](https://github.com/stanislaw))
- export/html: Requirements Tree with files branch [\#429](https://github.com/strictdoc-project/strictdoc/pull/429) ([mettta](https://github.com/mettta))
- export/html: add files tree in requirements\_coverage [\#428](https://github.com/strictdoc-project/strictdoc/pull/428) ([mettta](https://github.com/mettta))
- @mettta export/html: requirements-coverage.js [\#426](https://github.com/strictdoc-project/strictdoc/pull/426) ([mettta](https://github.com/mettta))
- export/html: hide new traceability-related work under a feature toggle [\#425](https://github.com/strictdoc-project/strictdoc/pull/425) ([stanislaw](https://github.com/stanislaw))
- docs: update backlog [\#424](https://github.com/strictdoc-project/strictdoc/pull/424) ([stanislaw](https://github.com/stanislaw))
- export/rst: catch and report RST-to-HTML conversion warnings [\#423](https://github.com/strictdoc-project/strictdoc/pull/423) ([stanislaw](https://github.com/stanislaw))
- export/html: stop using deprecated window.event [\#422](https://github.com/strictdoc-project/strictdoc/pull/422) ([stanislaw](https://github.com/stanislaw))
- export/html: Requirements Coverage page boilerplate improvements [\#421](https://github.com/strictdoc-project/strictdoc/pull/421) ([mettta](https://github.com/mettta))
- Code climate: fix several flake8 warnings [\#420](https://github.com/strictdoc-project/strictdoc/pull/420) ([stanislaw](https://github.com/stanislaw))
- export/html: Requirements Coverage page boilerplate [\#419](https://github.com/strictdoc-project/strictdoc/pull/419) ([stanislaw](https://github.com/stanislaw))
- export/html: fix space behavior in pan-with-space.js [\#418](https://github.com/strictdoc-project/strictdoc/pull/418) ([mettta](https://github.com/mettta))
- Code climate: fix unused imports [\#417](https://github.com/strictdoc-project/strictdoc/pull/417) ([stanislaw](https://github.com/stanislaw))
- Code climate: add flake8 linter [\#416](https://github.com/strictdoc-project/strictdoc/pull/416) ([stanislaw](https://github.com/stanislaw))
- export/html: introduce static\_path variable [\#415](https://github.com/strictdoc-project/strictdoc/pull/415) ([stanislaw](https://github.com/stanislaw))
- export/html: move root\_path and document\_iterator vars to Python level [\#414](https://github.com/strictdoc-project/strictdoc/pull/414) ([stanislaw](https://github.com/stanislaw))
- export/html: use Jinja's StrictUndefined, fix found issues [\#413](https://github.com/strictdoc-project/strictdoc/pull/413) ([stanislaw](https://github.com/stanislaw))
- export/html: put index & coverage pages into the base template [\#412](https://github.com/strictdoc-project/strictdoc/pull/412) ([mettta](https://github.com/mettta))
- @mettta export/html: source code coverage [\#411](https://github.com/strictdoc-project/strictdoc/pull/411) ([mettta](https://github.com/mettta))
- Code climate: Fix several Pylint warnings [\#410](https://github.com/strictdoc-project/strictdoc/pull/410) ([stanislaw](https://github.com/stanislaw))
- traceability: simplify logic of finding source file reqs [\#409](https://github.com/strictdoc-project/strictdoc/pull/409) ([stanislaw](https://github.com/stanislaw))
- traceability: render source lines with reqs in Jinja template [\#408](https://github.com/strictdoc-project/strictdoc/pull/408) ([stanislaw](https://github.com/stanislaw))
- traceability: Support turning on Pygments for C and C++ files [\#407](https://github.com/strictdoc-project/strictdoc/pull/407) ([stanislaw](https://github.com/stanislaw))
- Poetry: update dependencies [\#406](https://github.com/strictdoc-project/strictdoc/pull/406) ([stanislaw](https://github.com/stanislaw))
- export/html: source coverage: simplify source file syntax [\#405](https://github.com/strictdoc-project/strictdoc/pull/405) ([stanislaw](https://github.com/stanislaw))
- export/html: source coverage: generate SDoc keywords in a special way [\#404](https://github.com/strictdoc-project/strictdoc/pull/404) ([stanislaw](https://github.com/stanislaw))
- export/html: add index link in aside header content for doc/coverage … [\#403](https://github.com/strictdoc-project/strictdoc/pull/403) ([mettta](https://github.com/mettta))
- export/html: Source code coverage \(classes & hashchange\) [\#402](https://github.com/strictdoc-project/strictdoc/pull/402) ([mettta](https://github.com/mettta))
- export/html:  css fix [\#401](https://github.com/strictdoc-project/strictdoc/pull/401) ([mettta](https://github.com/mettta))
- traceability: source coverage displays source coverage \(3 cases\)  [\#400](https://github.com/strictdoc-project/strictdoc/pull/400) ([stanislaw](https://github.com/stanislaw))
- Code climate: traceability\_index: better function naming  [\#399](https://github.com/strictdoc-project/strictdoc/pull/399) ([stanislaw](https://github.com/stanislaw))
- traceability: source coverage page: show stats [\#398](https://github.com/strictdoc-project/strictdoc/pull/398) ([stanislaw](https://github.com/stanislaw))
- traceability: calculate source file coverage at the time of parsing [\#397](https://github.com/strictdoc-project/strictdoc/pull/397) ([stanislaw](https://github.com/stanislaw))
- traceability: read empty and one-line source files [\#396](https://github.com/strictdoc-project/strictdoc/pull/396) ([stanislaw](https://github.com/stanislaw))
- traceability: no ranges, when no requirements point to a source file [\#395](https://github.com/strictdoc-project/strictdoc/pull/395) ([stanislaw](https://github.com/stanislaw))
- traceability: Source Coverage page \(draft\) [\#394](https://github.com/strictdoc-project/strictdoc/pull/394) ([mettta](https://github.com/mettta))
- file\_tree: naming improvements, prepare for reuse [\#393](https://github.com/strictdoc-project/strictdoc/pull/393) ([stanislaw](https://github.com/stanislaw))
- document\_finder: switch to top-down search and some cleanups [\#392](https://github.com/strictdoc-project/strictdoc/pull/392) ([stanislaw](https://github.com/stanislaw))
- export/html: fix template\_type in the title [\#391](https://github.com/strictdoc-project/strictdoc/pull/391) ([mettta](https://github.com/mettta))
- export/html: Source code coverage [\#390](https://github.com/strictdoc-project/strictdoc/pull/390) ([mettta](https://github.com/mettta))
- Source file view: reqs list [\#389](https://github.com/strictdoc-project/strictdoc/pull/389) ([mettta](https://github.com/mettta))
- Making the BASE tpl. shared by documents and source-code pages; TOC improving. [\#388](https://github.com/strictdoc-project/strictdoc/pull/388) ([mettta](https://github.com/mettta))
- Code climate: fix some of the LGTM warnings [\#387](https://github.com/strictdoc-project/strictdoc/pull/387) ([stanislaw](https://github.com/stanislaw))
- Code climate: source\_files\_finder: more meaningful variable names [\#386](https://github.com/strictdoc-project/strictdoc/pull/386) ([stanislaw](https://github.com/stanislaw))
- traceability: detect when requirement link points to the current file [\#385](https://github.com/strictdoc-project/strictdoc/pull/385) ([stanislaw](https://github.com/stanislaw))
- traceability: ensure no requirement duplicates, when multiple file lines [\#384](https://github.com/strictdoc-project/strictdoc/pull/384) ([stanislaw](https://github.com/stanislaw))
-  traceability: single file case: fix finding Python files  [\#383](https://github.com/strictdoc-project/strictdoc/pull/383) ([stanislaw](https://github.com/stanislaw))
- docs: constraint for sphinx: ~=3.0 [\#381](https://github.com/strictdoc-project/strictdoc/pull/381) ([stanislaw](https://github.com/stanislaw))

## [0.0.11](https://github.com/strictdoc-project/strictdoc/tree/0.0.11) (2021-05-17)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.10...0.0.11)

**Closed issues:**

- The \_assets folder is not copied when a doc tree is a single file [\#341](https://github.com/strictdoc-project/strictdoc/issues/341)

**Merged pull requests:**

- Bump version to 0.0.11 [\#380](https://github.com/strictdoc-project/strictdoc/pull/380) ([stanislaw](https://github.com/stanislaw))
- export/html: fix the generation of assets for a single file case [\#379](https://github.com/strictdoc-project/strictdoc/pull/379) ([stanislaw](https://github.com/stanislaw))
- tests/integration: basic test: how assets are exported [\#378](https://github.com/strictdoc-project/strictdoc/pull/378) ([stanislaw](https://github.com/stanislaw))
- Poetry: sphinx: change to caret-based [\#377](https://github.com/strictdoc-project/strictdoc/pull/377) ([stanislaw](https://github.com/stanislaw))
- \[Snyk\] Fix for 4 vulnerabilities [\#376](https://github.com/strictdoc-project/strictdoc/pull/376) ([snyk-bot](https://github.com/snyk-bot))
-  docs: regenerate Read the Docs, update CHANGELOG [\#375](https://github.com/strictdoc-project/strictdoc/pull/375) ([stanislaw](https://github.com/stanislaw))

## [0.0.10](https://github.com/strictdoc-project/strictdoc/tree/0.0.10) (2021-04-18)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.9...0.0.10)

**Closed issues:**

- ModuleNotFoundError: No module named 'bs4' [\#336](https://github.com/strictdoc-project/strictdoc/issues/336)
- Parallelization: when Jinja crashes, the parent process is not signalled [\#320](https://github.com/strictdoc-project/strictdoc/issues/320)
- Error message: "requirement already exists": make more detailed [\#318](https://github.com/strictdoc-project/strictdoc/issues/318)
- export/html: Fix Pan.js to reflect the latest grid-based layout [\#232](https://github.com/strictdoc-project/strictdoc/issues/232)

**Merged pull requests:**

- Bump version to 0.0.10 [\#374](https://github.com/strictdoc-project/strictdoc/pull/374) ([stanislaw](https://github.com/stanislaw))
- cli: add a warning that the traceability is not complete  [\#373](https://github.com/strictdoc-project/strictdoc/pull/373) ([stanislaw](https://github.com/stanislaw))
- export/rst: preserve original file name instead of using document title  [\#372](https://github.com/strictdoc-project/strictdoc/pull/372) ([stanislaw](https://github.com/stanislaw))
- Poetry: use caret "^" for docutils, jinja, and lxml [\#371](https://github.com/strictdoc-project/strictdoc/pull/371) ([stanislaw](https://github.com/stanislaw))
- \[Snyk\] Security upgrade urllib3 from 1.26.3 to 1.26.4 [\#370](https://github.com/strictdoc-project/strictdoc/pull/370) ([snyk-bot](https://github.com/snyk-bot))
- \[Snyk\] Security upgrade Pygments from 2.5.2 to 2.7.4 [\#367](https://github.com/strictdoc-project/strictdoc/pull/367) ([snyk-bot](https://github.com/snyk-bot))
- Code climate: ExportAction: remove self, simplify code [\#364](https://github.com/strictdoc-project/strictdoc/pull/364) ([stanislaw](https://github.com/stanislaw))
- Code climate: move MarkupRenderer down to generators [\#363](https://github.com/strictdoc-project/strictdoc/pull/363) ([stanislaw](https://github.com/stanislaw))
- grammar: Document number [\#362](https://github.com/strictdoc-project/strictdoc/pull/362) ([stanislaw](https://github.com/stanislaw))
- grammar: Document version [\#361](https://github.com/strictdoc-project/strictdoc/pull/361) ([stanislaw](https://github.com/stanislaw))
- cli: include root path to the ExportConfig object [\#360](https://github.com/strictdoc-project/strictdoc/pull/360) ([stanislaw](https://github.com/stanislaw))
- README: Fix badges to the master branch [\#359](https://github.com/strictdoc-project/strictdoc/pull/359) ([stanislaw](https://github.com/stanislaw))
- Front: large number of requirements in aside [\#353](https://github.com/strictdoc-project/strictdoc/pull/353) ([mettta](https://github.com/mettta))
- Front: translate code block with boundaries [\#352](https://github.com/strictdoc-project/strictdoc/pull/352) ([mettta](https://github.com/mettta))
- scrolling and highlighting code Block depending on  parameters in URL [\#351](https://github.com/strictdoc-project/strictdoc/pull/351) ([mettta](https://github.com/mettta))
- Front: params in URL [\#350](https://github.com/strictdoc-project/strictdoc/pull/350) ([mettta](https://github.com/mettta))
- Front: source page [\#349](https://github.com/strictdoc-project/strictdoc/pull/349) ([mettta](https://github.com/mettta))
- sandbox: add a non-range link for hello\_world.py [\#348](https://github.com/strictdoc-project/strictdoc/pull/348) ([stanislaw](https://github.com/stanislaw))
-  export/html: pan-with-space.js: fix scrolling  [\#347](https://github.com/strictdoc-project/strictdoc/pull/347) ([stanislaw](https://github.com/stanislaw))
- export/html: source file view: print all range requirements [\#346](https://github.com/strictdoc-project/strictdoc/pull/346) ([stanislaw](https://github.com/stanislaw))
-  export/html: source files: improve \<pre\> rendering and no last newline  [\#345](https://github.com/strictdoc-project/strictdoc/pull/345) ([stanislaw](https://github.com/stanislaw))
- export/html: source files: split contents from Pygments by lines [\#344](https://github.com/strictdoc-project/strictdoc/pull/344) ([stanislaw](https://github.com/stanislaw))
- config: ExportCommandConfig for grouping config options [\#343](https://github.com/strictdoc-project/strictdoc/pull/343) ([stanislaw](https://github.com/stanislaw))
- Basic forward and reverse traceability between SDoc and source files [\#342](https://github.com/strictdoc-project/strictdoc/pull/342) ([stanislaw](https://github.com/stanislaw))
- Parallelizer: switch from Pool to Process: handle exits and exceptions [\#340](https://github.com/strictdoc-project/strictdoc/pull/340) ([stanislaw](https://github.com/stanislaw))
-  traceability\_index: "requirement already exists" - more detailed message  [\#339](https://github.com/strictdoc-project/strictdoc/pull/339) ([stanislaw](https://github.com/stanislaw))

## [0.0.9](https://github.com/strictdoc-project/strictdoc/tree/0.0.9) (2021-02-01)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.8...0.0.9)

**Closed issues:**

- Installation problems on Ubuntu 20.04 [\#326](https://github.com/strictdoc-project/strictdoc/issues/326)
- Enable testing on older Linux distributions [\#325](https://github.com/strictdoc-project/strictdoc/issues/325)

**Merged pull requests:**

- Bump version to 0.0.9 [\#338](https://github.com/strictdoc-project/strictdoc/pull/338) ([stanislaw](https://github.com/stanislaw))
- Poetry: move bs4 to normal dependencies [\#337](https://github.com/strictdoc-project/strictdoc/pull/337) ([stanislaw](https://github.com/stanislaw))
- docs: update the clone URL [\#335](https://github.com/strictdoc-project/strictdoc/pull/335) ([stanislaw](https://github.com/stanislaw))
- docs: resolve a few RST syntax-related issues [\#334](https://github.com/strictdoc-project/strictdoc/pull/334) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate Read the Docs [\#333](https://github.com/strictdoc-project/strictdoc/pull/333) ([stanislaw](https://github.com/stanislaw))
- CI: add Ubuntu 16.04 workflow [\#332](https://github.com/strictdoc-project/strictdoc/pull/332) ([stanislaw](https://github.com/stanislaw))
-  docs: Grammar elements  [\#331](https://github.com/strictdoc-project/strictdoc/pull/331) ([stanislaw](https://github.com/stanislaw))
- docs: Document structure and two strict rules of SDoc [\#330](https://github.com/strictdoc-project/strictdoc/pull/330) ([stanislaw](https://github.com/stanislaw))
- tasks: remove dependency on poetry run [\#329](https://github.com/strictdoc-project/strictdoc/pull/329) ([stanislaw](https://github.com/stanislaw))
- tasks: make black make changes right away and exit with 1 [\#328](https://github.com/strictdoc-project/strictdoc/pull/328) ([stanislaw](https://github.com/stanislaw))
-  README: Expand the second installation option section.  [\#327](https://github.com/strictdoc-project/strictdoc/pull/327) ([stanislaw](https://github.com/stanislaw))
- README: remove "under construction", add summary [\#324](https://github.com/strictdoc-project/strictdoc/pull/324) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate Read the Docs and CHANGELOG [\#323](https://github.com/strictdoc-project/strictdoc/pull/323) ([stanislaw](https://github.com/stanislaw))

## [0.0.8](https://github.com/strictdoc-project/strictdoc/tree/0.0.8) (2021-01-24)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.7...0.0.8)

**Fixed bugs:**

- Parallelizing with multiprocessing can leave Zombie processes running [\#313](https://github.com/strictdoc-project/strictdoc/issues/313)

**Closed issues:**

- export/html: store Google font as a local asset [\#306](https://github.com/strictdoc-project/strictdoc/issues/306)
- HTML distribution as one file [\#279](https://github.com/strictdoc-project/strictdoc/issues/279)
- tasks and CI: Set up Black [\#238](https://github.com/strictdoc-project/strictdoc/issues/238)
- export/html: Document tree: adjust styles to handle single files without folders [\#236](https://github.com/strictdoc-project/strictdoc/issues/236)

**Merged pull requests:**

- Bump version to 0.0.8 [\#322](https://github.com/strictdoc-project/strictdoc/pull/322) ([stanislaw](https://github.com/stanislaw))
- export/html: print children links, allow full left-right navigation [\#321](https://github.com/strictdoc-project/strictdoc/pull/321) ([stanislaw](https://github.com/stanislaw))
- document\_finder: include case when intermediate folder has no .sdoc files [\#319](https://github.com/strictdoc-project/strictdoc/pull/319) ([stanislaw](https://github.com/stanislaw))
- tasks: fix install-local task issue [\#317](https://github.com/strictdoc-project/strictdoc/pull/317) ([stanislaw](https://github.com/stanislaw))
- docs: performance feature highlight [\#316](https://github.com/strictdoc-project/strictdoc/pull/316) ([stanislaw](https://github.com/stanislaw))
- tests/integration: test that no fork\(\) warning appears [\#315](https://github.com/strictdoc-project/strictdoc/pull/315) ([stanislaw](https://github.com/stanislaw))
- parallelizer: fix hanging and zombie processes when child processes misbehave [\#314](https://github.com/strictdoc-project/strictdoc/pull/314) ([stanislaw](https://github.com/stanislaw))
-  CI: add invoke lint task  [\#312](https://github.com/strictdoc-project/strictdoc/pull/312) ([stanislaw](https://github.com/stanislaw))
- Code climate: black-format the rest of strictdoc/\*\*/\* files [\#311](https://github.com/strictdoc-project/strictdoc/pull/311) ([stanislaw](https://github.com/stanislaw))
- Enable Python 3.9: Related fixes in the code, enable GitHub action. [\#309](https://github.com/strictdoc-project/strictdoc/pull/309) ([stanislaw](https://github.com/stanislaw))

## [0.0.7](https://github.com/strictdoc-project/strictdoc/tree/0.0.7) (2021-01-10)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.6...0.0.7)

**Closed issues:**

- Fix lost links in TOC on the DEEP TRACEABILITY page [\#180](https://github.com/strictdoc-project/strictdoc/issues/180)

**Merged pull requests:**

- Bump version to 0.0.7 [\#308](https://github.com/strictdoc-project/strictdoc/pull/308) ([stanislaw](https://github.com/stanislaw))
-  docs: finish two TBDs  [\#307](https://github.com/strictdoc-project/strictdoc/pull/307) ([stanislaw](https://github.com/stanislaw))
- dsl: requirement: has\_requirements -\> ng\_has\_requirements [\#305](https://github.com/strictdoc-project/strictdoc/pull/305) ([stanislaw](https://github.com/stanislaw))
- Code climate: black-format requirement and helpers [\#304](https://github.com/strictdoc-project/strictdoc/pull/304) ([stanislaw](https://github.com/stanislaw))
- export/html: DTR: display sections that have requirements [\#303](https://github.com/strictdoc-project/strictdoc/pull/303) ([stanislaw](https://github.com/stanislaw))
- grammar: deprecate \[DOCUMENT\].NAME [\#302](https://github.com/strictdoc-project/strictdoc/pull/302) ([stanislaw](https://github.com/stanislaw))
- grammar: deprecate \[SECTION\].level [\#301](https://github.com/strictdoc-project/strictdoc/pull/301) ([stanislaw](https://github.com/stanislaw))
- grammar: COMPOSITE-REQUIREMENT -\> COMPOSITE\_REQUIREMENT [\#299](https://github.com/strictdoc-project/strictdoc/pull/299) ([stanislaw](https://github.com/stanislaw))
- Create LICENSE [\#298](https://github.com/strictdoc-project/strictdoc/pull/298) ([stanislaw](https://github.com/stanislaw))
- docs/sphinx: fix nav bar presentation [\#297](https://github.com/strictdoc-project/strictdoc/pull/297) ([stanislaw](https://github.com/stanislaw))
-  docs/sphinx: switch to guzzle\_sphinx\_theme, improve presentation of meta  [\#296](https://github.com/strictdoc-project/strictdoc/pull/296) ([stanislaw](https://github.com/stanislaw))

## [0.0.6](https://github.com/strictdoc-project/strictdoc/tree/0.0.6) (2021-01-07)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.5...0.0.6)

**Merged pull requests:**

- Bump version to 0.0.6 [\#295](https://github.com/strictdoc-project/strictdoc/pull/295) ([stanislaw](https://github.com/stanislaw))
-  docs: regenerate Read the Docs  [\#294](https://github.com/strictdoc-project/strictdoc/pull/294) ([stanislaw](https://github.com/stanislaw))
-  docs: all export options and --no-parallelization option  [\#293](https://github.com/strictdoc-project/strictdoc/pull/293) ([stanislaw](https://github.com/stanislaw))
- docs: regenerate readthedocs [\#291](https://github.com/strictdoc-project/strictdoc/pull/291) ([stanislaw](https://github.com/stanislaw))
- docs: update to the latest state [\#290](https://github.com/strictdoc-project/strictdoc/pull/290) ([stanislaw](https://github.com/stanislaw))
- docs: Other tools: Sphinx-Needs and StrictDoc [\#289](https://github.com/strictdoc-project/strictdoc/pull/289) ([stanislaw](https://github.com/stanislaw))
- export/html: correct width for \<img\> tags [\#288](https://github.com/strictdoc-project/strictdoc/pull/288) ([stanislaw](https://github.com/stanislaw))
- export/html: new 'standlone' export with assets embedded in HTML [\#287](https://github.com/strictdoc-project/strictdoc/pull/287) ([stanislaw](https://github.com/stanislaw))

## [0.0.5](https://github.com/strictdoc-project/strictdoc/tree/0.0.5) (2021-01-04)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.4...0.0.5)

**Closed issues:**

- export/excel: make fields configurable [\#272](https://github.com/strictdoc-project/strictdoc/issues/272)
- Custom fields usage [\#269](https://github.com/strictdoc-project/strictdoc/issues/269)
- HTML anchors are not working [\#268](https://github.com/strictdoc-project/strictdoc/issues/268)
- Excel export [\#258](https://github.com/strictdoc-project/strictdoc/issues/258)
- Styles: Requirement Rationale [\#249](https://github.com/strictdoc-project/strictdoc/issues/249)
- Styles: basic styles for \<table\> [\#248](https://github.com/strictdoc-project/strictdoc/issues/248)
- export/rst: Print requirement parents  [\#237](https://github.com/strictdoc-project/strictdoc/issues/237)

**Merged pull requests:**

- .github/workflows/release.yml: switch to using $GITHUB\_ENV [\#286](https://github.com/strictdoc-project/strictdoc/pull/286) ([stanislaw](https://github.com/stanislaw))
- Bump version to 0.0.5 [\#285](https://github.com/strictdoc-project/strictdoc/pull/285) ([stanislaw](https://github.com/stanislaw))
- tests/integration: excel/02\_no\_reqs\_to\_export: remove copy paste garbage [\#283](https://github.com/strictdoc-project/strictdoc/pull/283) ([stanislaw](https://github.com/stanislaw))
- export/excel: export special fields [\#282](https://github.com/strictdoc-project/strictdoc/pull/282) ([stumpyfr](https://github.com/stumpyfr))
- grammar: only allow special fields of type 'String' [\#281](https://github.com/strictdoc-project/strictdoc/pull/281) ([stanislaw](https://github.com/stanislaw))
- export/html: display requirement's special fields [\#280](https://github.com/strictdoc-project/strictdoc/pull/280) ([mettta](https://github.com/mettta))
- black-format: tools/confluence\_html\_table\_import.py [\#278](https://github.com/strictdoc-project/strictdoc/pull/278) ([stanislaw](https://github.com/stanislaw))
- dsl: special fields support [\#277](https://github.com/strictdoc-project/strictdoc/pull/277) ([stanislaw](https://github.com/stanislaw))
- invoke: create\_local\_setup task [\#276](https://github.com/strictdoc-project/strictdoc/pull/276) ([stanislaw](https://github.com/stanislaw))
- CHANGELOG: initial commit and invoke task [\#275](https://github.com/strictdoc-project/strictdoc/pull/275) ([stanislaw](https://github.com/stanislaw))
- export/html: requirements' hyperlinks are implemented consistently [\#274](https://github.com/strictdoc-project/strictdoc/pull/274) ([stanislaw](https://github.com/stanislaw))
- export/html: link\_renderer: render -\> render\_local\_anchor [\#273](https://github.com/strictdoc-project/strictdoc/pull/273) ([stanislaw](https://github.com/stanislaw))
- export/excel: basic Excel export [\#271](https://github.com/strictdoc-project/strictdoc/pull/271) ([stanislaw](https://github.com/stanislaw))
- dsl/reader: Requirement\#document and CompositeRequirement\#document fields  [\#270](https://github.com/strictdoc-project/strictdoc/pull/270) ([mettta](https://github.com/mettta))
- cli/cli\_arg\_parser: support multiple export formats [\#266](https://github.com/strictdoc-project/strictdoc/pull/266) ([stanislaw](https://github.com/stanislaw))
- export\_action: create output folders only when requested [\#265](https://github.com/strictdoc-project/strictdoc/pull/265) ([stanislaw](https://github.com/stanislaw))
- cli: generate RST only when --formats=rst is provided [\#264](https://github.com/strictdoc-project/strictdoc/pull/264) ([stanislaw](https://github.com/stanislaw))
-  export/html/html\_generator: contain most of the HTML-related export code  [\#263](https://github.com/strictdoc-project/strictdoc/pull/263) ([stanislaw](https://github.com/stanislaw))
- backend/dsl/reader: black-format [\#262](https://github.com/strictdoc-project/strictdoc/pull/262) ([stanislaw](https://github.com/stanislaw))
- Rename: SingleDocumentRSTExport -\> DocumentRSTGenerator  [\#261](https://github.com/strictdoc-project/strictdoc/pull/261) ([stanislaw](https://github.com/stanislaw))
- cli: argparse --format argument [\#260](https://github.com/strictdoc-project/strictdoc/pull/260) ([stanislaw](https://github.com/stanislaw))
-  tests/integration: commands/export/rst/01\_basic\_rst\_export  [\#259](https://github.com/strictdoc-project/strictdoc/pull/259) ([stanislaw](https://github.com/stanislaw))
- export/html: add CSS for table [\#257](https://github.com/strictdoc-project/strictdoc/pull/257) ([mettta](https://github.com/mettta))
- export/html: add Rationale [\#256](https://github.com/strictdoc-project/strictdoc/pull/256) ([mettta](https://github.com/mettta))
- export/rst: print parent and child links [\#255](https://github.com/strictdoc-project/strictdoc/pull/255) ([stanislaw](https://github.com/stanislaw))
- cli/main: black-format [\#254](https://github.com/strictdoc-project/strictdoc/pull/254) ([stanislaw](https://github.com/stanislaw))
- Test increasing pylint tolerance [\#253](https://github.com/strictdoc-project/strictdoc/pull/253) ([stanislaw](https://github.com/stanislaw))
- Poetry and tasks: introduce pylint [\#252](https://github.com/strictdoc-project/strictdoc/pull/252) ([stanislaw](https://github.com/stanislaw))
- tasks: install-local via Poetry/setup.py [\#251](https://github.com/strictdoc-project/strictdoc/pull/251) ([stanislaw](https://github.com/stanislaw))
- Requirement: basic requirement\_from\_dict\(\) constructor [\#250](https://github.com/strictdoc-project/strictdoc/pull/250) ([stanislaw](https://github.com/stanislaw))
- sandbox: basic table example using RST syntax [\#247](https://github.com/strictdoc-project/strictdoc/pull/247) ([stanislaw](https://github.com/stanislaw))
- Poetry: add Black, PyEnv: bump to 3.6.2  [\#246](https://github.com/strictdoc-project/strictdoc/pull/246) ([stanislaw](https://github.com/stanislaw))
- Poetry: add BeautifulSoup to dev dependencies [\#245](https://github.com/strictdoc-project/strictdoc/pull/245) ([stanislaw](https://github.com/stanislaw))
- tools: parsing reqs from Confluence HTML table [\#244](https://github.com/strictdoc-project/strictdoc/pull/244) ([stanislaw](https://github.com/stanislaw))
- grammar: support RATIONALE, single and multiline string field [\#243](https://github.com/strictdoc-project/strictdoc/pull/243) ([stanislaw](https://github.com/stanislaw))
- docs/sphinx/pdf: minor change in how doc title is displayed [\#242](https://github.com/strictdoc-project/strictdoc/pull/242) ([stanislaw](https://github.com/stanislaw))
- docs/sphinx: disable fncychap [\#241](https://github.com/strictdoc-project/strictdoc/pull/241) ([stanislaw](https://github.com/stanislaw))
- export/html: new styles for Document Tree [\#240](https://github.com/strictdoc-project/strictdoc/pull/240) ([mettta](https://github.com/mettta))
-  Bump version to 0.0.4  [\#239](https://github.com/strictdoc-project/strictdoc/pull/239) ([stanislaw](https://github.com/stanislaw))

## [0.0.4](https://github.com/strictdoc-project/strictdoc/tree/0.0.4) (2020-11-17)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.3...0.0.4)

**Closed issues:**

- Sphinx PDF vs HTML: Resolve 'single document' vs 'multiple documents' document tree problem [\#230](https://github.com/strictdoc-project/strictdoc/issues/230)
- CI: GitHub Actions deprecation warning: The `set-env` command is deprecated and will be disabled soon [\#220](https://github.com/strictdoc-project/strictdoc/issues/220)
- export/html: Finish the Table page: remove sections, make the headers float [\#215](https://github.com/strictdoc-project/strictdoc/issues/215)
- export: decide if passing files instead of folders should also work [\#144](https://github.com/strictdoc-project/strictdoc/issues/144)

**Merged pull requests:**

- export/html: enable passing single files as input [\#235](https://github.com/strictdoc-project/strictdoc/pull/235) ([stanislaw](https://github.com/stanislaw))
- export/html: fix traceability view \(central column width\) and  'code' styles [\#234](https://github.com/strictdoc-project/strictdoc/pull/234) ([mettta](https://github.com/mettta))
- export/rst: do not generate top-level header if single document tree [\#233](https://github.com/strictdoc-project/strictdoc/pull/233) ([stanislaw](https://github.com/stanislaw))
- docs/sphinx: add requirements.txt [\#231](https://github.com/strictdoc-project/strictdoc/pull/231) ([stanislaw](https://github.com/stanislaw))
-  docs: regenerate HTML  [\#229](https://github.com/strictdoc-project/strictdoc/pull/229) ([stanislaw](https://github.com/stanislaw))
- export/html: Switch to grid layout  [\#228](https://github.com/strictdoc-project/strictdoc/pull/228) ([mettta](https://github.com/mettta))
- export/html: fix tables template \(remove sections and add sticky headers\) [\#227](https://github.com/strictdoc-project/strictdoc/pull/227) ([mettta](https://github.com/mettta))
- docs/sphinx: Read the version from Poetry [\#226](https://github.com/strictdoc-project/strictdoc/pull/226) ([stanislaw](https://github.com/stanislaw))
- docs: section about Sphinx [\#225](https://github.com/strictdoc-project/strictdoc/pull/225) ([stanislaw](https://github.com/stanislaw))
- CI: Try to fix a deprecation warning from GitHub actions \(usage of set-env\) [\#224](https://github.com/strictdoc-project/strictdoc/pull/224) ([stanislaw](https://github.com/stanislaw))
- export/html: Add template Inheritance for views \(except doc-tree\) & styles for tables [\#223](https://github.com/strictdoc-project/strictdoc/pull/223) ([mettta](https://github.com/mettta))
- Bump version to 0.0.2 [\#222](https://github.com/strictdoc-project/strictdoc/pull/222) ([stanislaw](https://github.com/stanislaw))

## [0.0.3](https://github.com/strictdoc-project/strictdoc/tree/0.0.3) (2020-11-10)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.2...0.0.3)

## [0.0.2](https://github.com/strictdoc-project/strictdoc/tree/0.0.2) (2020-11-10)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/0.0.1...0.0.2)

## [0.0.1](https://github.com/strictdoc-project/strictdoc/tree/0.0.1) (2020-11-10)

[Full Changelog](https://github.com/strictdoc-project/strictdoc/compare/f03d6f8f97f3efc65554e974c2c66245b938455c...0.0.1)

**Fixed bugs:**

- TOC doesn't have "TOC" printed on the GNC page [\#210](https://github.com/strictdoc-project/strictdoc/issues/210)
- document width on the Columbus page is too wide [\#202](https://github.com/strictdoc-project/strictdoc/issues/202)
- requirement.has\_meta should work [\#185](https://github.com/strictdoc-project/strictdoc/issues/185)
- export/html: Document Tree: vertical lines connecting folders and files are sometimes longer than needed [\#131](https://github.com/strictdoc-project/strictdoc/issues/131)
- export/html: link class ".reference.external" misaligns links [\#126](https://github.com/strictdoc-project/strictdoc/issues/126)
- export: weird behavior of search when there is a "/" symbol after an input folder [\#117](https://github.com/strictdoc-project/strictdoc/issues/117)

**Closed issues:**

- Find a solution for TOC with reqs. without headers [\#187](https://github.com/strictdoc-project/strictdoc/issues/187)
- Requirement href: create generic helper [\#184](https://github.com/strictdoc-project/strictdoc/issues/184)
- export/html: Fix structure of single\_document template [\#182](https://github.com/strictdoc-project/strictdoc/issues/182)
- export/html: Document page: print requirement parents [\#176](https://github.com/strictdoc-project/strictdoc/issues/176)
- export/html: make TOC closeable [\#171](https://github.com/strictdoc-project/strictdoc/issues/171)
-  export/html: Document page: styles for \<blockquote\> [\#167](https://github.com/strictdoc-project/strictdoc/issues/167)
- export/html: Document page: add left margin/padding to bullet points inside freetext  [\#166](https://github.com/strictdoc-project/strictdoc/issues/166)
- TOC: consider including requirement titles as well [\#162](https://github.com/strictdoc-project/strictdoc/issues/162)
- Separate requirements visually on the "plain" requirements documents [\#160](https://github.com/strictdoc-project/strictdoc/issues/160)
- Introduce CI: GitHub Actions / macOS [\#158](https://github.com/strictdoc-project/strictdoc/issues/158)
- export/html: Unify Requirements partials [\#156](https://github.com/strictdoc-project/strictdoc/issues/156)
- export/html: Fix table view [\#149](https://github.com/strictdoc-project/strictdoc/issues/149)
- textX: parallelize reading sdoc files [\#147](https://github.com/strictdoc-project/strictdoc/issues/147)
- export/html: Main req. cards in Traceability & Deep traceability views must be sharper [\#143](https://github.com/strictdoc-project/strictdoc/issues/143)
- export/html: TOC must be visible on all pages [\#142](https://github.com/strictdoc-project/strictdoc/issues/142)
- CLI: option to provide export output folder [\#140](https://github.com/strictdoc-project/strictdoc/issues/140)
- export/html: The title of the document must be fixed [\#136](https://github.com/strictdoc-project/strictdoc/issues/136)
- export/html: Document Tree: rework generation and improve CSS styles [\#132](https://github.com/strictdoc-project/strictdoc/issues/132)
- export/html: Deep Traceability middle column sometimes gets its cells incorrectly aligned [\#130](https://github.com/strictdoc-project/strictdoc/issues/130)
- export/html: Style for UID field [\#129](https://github.com/strictdoc-project/strictdoc/issues/129)
- export/html: Set correct margin for the Document Tree page [\#128](https://github.com/strictdoc-project/strictdoc/issues/128)
- export: Copy image assets to the export destination directory [\#109](https://github.com/strictdoc-project/strictdoc/issues/109)
- export/html: Add HTML markup validation to the integration tests [\#108](https://github.com/strictdoc-project/strictdoc/issues/108)
- Table view: scroll bar appears for no good reason when switching a table view cell to edit mode [\#21](https://github.com/strictdoc-project/strictdoc/issues/21)
- Recognize header level when parsing RST [\#12](https://github.com/strictdoc-project/strictdoc/issues/12)
- Logger: introduce generic class that can be subclassed to enable logging functionality [\#11](https://github.com/strictdoc-project/strictdoc/issues/11)
- RSTReader: throw exceptions when docutils throws errors/warnings [\#8](https://github.com/strictdoc-project/strictdoc/issues/8)
- RST to HTML writer: check how standalone headers are rendered [\#4](https://github.com/strictdoc-project/strictdoc/issues/4)
- Introduce functional testing [\#3](https://github.com/strictdoc-project/strictdoc/issues/3)

**Merged pull requests:**

- CI: GitHub action config for releases [\#221](https://github.com/strictdoc-project/strictdoc/pull/221) ([stanislaw](https://github.com/stanislaw))
- CI: GitHub Actions file for Windows [\#219](https://github.com/strictdoc-project/strictdoc/pull/219) ([stanislaw](https://github.com/stanislaw))
- tasks: echo executed commands [\#218](https://github.com/strictdoc-project/strictdoc/pull/218) ([stanislaw](https://github.com/stanislaw))
-  docs: regenerate readthedocs content  [\#217](https://github.com/strictdoc-project/strictdoc/pull/217) ([stanislaw](https://github.com/stanislaw))
- CI: GitHub Actions file for Linux [\#214](https://github.com/strictdoc-project/strictdoc/pull/214) ([stanislaw](https://github.com/stanislaw))
- export/html: fix empty tags case [\#213](https://github.com/strictdoc-project/strictdoc/pull/213) ([mettta](https://github.com/mettta))
- export/html: fix TOC [\#212](https://github.com/strictdoc-project/strictdoc/pull/212) ([mettta](https://github.com/mettta))
- export/html: print requirement parents [\#211](https://github.com/strictdoc-project/strictdoc/pull/211) ([mettta](https://github.com/mettta))
- export/html: TAGs block [\#209](https://github.com/strictdoc-project/strictdoc/pull/209) ([mettta](https://github.com/mettta))
- export/html: TOC and titles [\#208](https://github.com/strictdoc-project/strictdoc/pull/208) ([mettta](https://github.com/mettta))
- CI: Python 3.8-related fixes for macOS [\#207](https://github.com/strictdoc-project/strictdoc/pull/207) ([stanislaw](https://github.com/stanislaw))
-  CI: GitHub Actions file for macOS  [\#206](https://github.com/strictdoc-project/strictdoc/pull/206) ([stanislaw](https://github.com/stanislaw))
-  export/html: resolve remaining HTML/XML markup errors + integration test  [\#205](https://github.com/strictdoc-project/strictdoc/pull/205) ([stanislaw](https://github.com/stanislaw))
- export/html: document tree: resolve major HTML markup issues [\#204](https://github.com/strictdoc-project/strictdoc/pull/204) ([stanislaw](https://github.com/stanislaw))
- tests/integration: html markup validator draft [\#203](https://github.com/strictdoc-project/strictdoc/pull/203) ([stanislaw](https://github.com/stanislaw))
- export/html: correct links for the documents on the table of contents [\#201](https://github.com/strictdoc-project/strictdoc/pull/201) ([stanislaw](https://github.com/stanislaw))
- dsl/models: minor cleanup and semantic improvements [\#200](https://github.com/strictdoc-project/strictdoc/pull/200) ([stanislaw](https://github.com/stanislaw))
- dsl/models: RequirementContext and SectionContext to store runtime info  [\#199](https://github.com/strictdoc-project/strictdoc/pull/199) ([stanislaw](https://github.com/stanislaw))
- export/html: Add TOC bar with pseudo-links [\#198](https://github.com/strictdoc-project/strictdoc/pull/198) ([mettta](https://github.com/mettta))
- export/html: TOC and document header improvements, :target highlighting [\#197](https://github.com/strictdoc-project/strictdoc/pull/197) ([mettta](https://github.com/mettta))
- export/html: LinkRenderer to manage how the links are created [\#196](https://github.com/strictdoc-project/strictdoc/pull/196) ([stanislaw](https://github.com/stanislaw))
- export/html: delete obsolete html/css files [\#195](https://github.com/strictdoc-project/strictdoc/pull/195) ([mettta](https://github.com/mettta))
- export/html: Numerous changes to the layout and styles [\#194](https://github.com/strictdoc-project/strictdoc/pull/194) ([mettta](https://github.com/mettta))
- grammar: make sure that the UID field is either a value or None [\#192](https://github.com/strictdoc-project/strictdoc/pull/192) ([stanislaw](https://github.com/stanislaw))
- cli: --no-parallelization option [\#191](https://github.com/strictdoc-project/strictdoc/pull/191) ([stanislaw](https://github.com/stanislaw))
- export/html: fix include rule \(requirement.jinja.html\) in recursive\_c… [\#190](https://github.com/strictdoc-project/strictdoc/pull/190) ([mettta](https://github.com/mettta))
- view-table on flex [\#189](https://github.com/strictdoc-project/strictdoc/pull/189) ([mettta](https://github.com/mettta))
- export/html: fix include rule \(requirement.jinja.html\) in recursive\_cell  [\#188](https://github.com/strictdoc-project/strictdoc/pull/188) ([mettta](https://github.com/mettta))
- export/html: Unify Requirements partials \(except tables\) [\#186](https://github.com/strictdoc-project/strictdoc/pull/186) ([mettta](https://github.com/mettta))
-  grammar and export: free text is fixed to the sections and document  [\#183](https://github.com/strictdoc-project/strictdoc/pull/183) ([stanislaw](https://github.com/stanislaw))
- export/html: Styles for requirements & fix anchors on all pages [\#181](https://github.com/strictdoc-project/strictdoc/pull/181) ([mettta](https://github.com/mettta))
- docs: add links to html, sphinx html, pdf [\#179](https://github.com/strictdoc-project/strictdoc/pull/179) ([stanislaw](https://github.com/stanislaw))
-  docs: add StrictDoc HTML export  [\#178](https://github.com/strictdoc-project/strictdoc/pull/178) ([stanislaw](https://github.com/stanislaw))
- docs: readthedocs integration [\#177](https://github.com/strictdoc-project/strictdoc/pull/177) ([stanislaw](https://github.com/stanislaw))
- docs: update goals [\#175](https://github.com/strictdoc-project/strictdoc/pull/175) ([stanislaw](https://github.com/stanislaw))
- export/html: Document page: styles for \<blockquote\> [\#174](https://github.com/strictdoc-project/strictdoc/pull/174) ([mettta](https://github.com/mettta))
- export/html: fix margins for P and UL [\#173](https://github.com/strictdoc-project/strictdoc/pull/173) ([mettta](https://github.com/mettta))
- Make TOC closable [\#172](https://github.com/strictdoc-project/strictdoc/pull/172) ([mettta](https://github.com/mettta))
- tests/integration: simple test of parallelized reading and export  [\#170](https://github.com/strictdoc-project/strictdoc/pull/170) ([stanislaw](https://github.com/stanislaw))
- helpers/parallelizer: working code for parallelization of textX I/O [\#169](https://github.com/strictdoc-project/strictdoc/pull/169) ([stanislaw](https://github.com/stanislaw))
- docs: fill in some missing parts: Intro, Examples, Doorstop [\#168](https://github.com/strictdoc-project/strictdoc/pull/168) ([stanislaw](https://github.com/stanislaw))
- export/html: Fix table view \(media queries\) [\#165](https://github.com/strictdoc-project/strictdoc/pull/165) ([mettta](https://github.com/mettta))
- export/html: Fix table view [\#164](https://github.com/strictdoc-project/strictdoc/pull/164) ([mettta](https://github.com/mettta))
- export/html: Fix table view [\#163](https://github.com/strictdoc-project/strictdoc/pull/163) ([mettta](https://github.com/mettta))
- export/html: Makes empty TOC container visible on all pages [\#161](https://github.com/strictdoc-project/strictdoc/pull/161) ([mettta](https://github.com/mettta))
- export: fix egde case: input folder with a trailing slash  [\#159](https://github.com/strictdoc-project/strictdoc/pull/159) ([stanislaw](https://github.com/stanislaw))
- Remove strictdoc's first generation code  [\#157](https://github.com/strictdoc-project/strictdoc/pull/157) ([stanislaw](https://github.com/stanislaw))
- export/html: fix border for meta in requirements [\#155](https://github.com/strictdoc-project/strictdoc/pull/155) ([mettta](https://github.com/mettta))
- export/html: meta table for Req., data-attr for titles and requirements [\#154](https://github.com/strictdoc-project/strictdoc/pull/154) ([mettta](https://github.com/mettta))
- README: replace TBD [\#153](https://github.com/strictdoc-project/strictdoc/pull/153) ([stanislaw](https://github.com/stanislaw))
- dsl: Requirement@has\_meta [\#152](https://github.com/strictdoc-project/strictdoc/pull/152) ([stanislaw](https://github.com/stanislaw))
- docs: add sandbox.sdoc for experiments [\#151](https://github.com/strictdoc-project/strictdoc/pull/151) ([stanislaw](https://github.com/stanislaw))
- export: support both full and relative output paths [\#150](https://github.com/strictdoc-project/strictdoc/pull/150) ([stanislaw](https://github.com/stanislaw))
- cli: export: --output-dir command [\#148](https://github.com/strictdoc-project/strictdoc/pull/148) ([stanislaw](https://github.com/stanislaw))
-  cli: cli\_arg\_parser: parsing is extracted and improved  [\#146](https://github.com/strictdoc-project/strictdoc/pull/146) ([stanislaw](https://github.com/stanislaw))
-  tests/integration: more basic "export" and "passthrough" itests  [\#145](https://github.com/strictdoc-project/strictdoc/pull/145) ([stanislaw](https://github.com/stanislaw))
- export/html: Fixes view-traceability-deep layout [\#141](https://github.com/strictdoc-project/strictdoc/pull/141) ([mettta](https://github.com/mettta))
- traceability\_index: fix the calculation of the document req depth [\#137](https://github.com/strictdoc-project/strictdoc/pull/137) ([stanislaw](https://github.com/stanislaw))
- export/html: Document Tree markup fixes [\#135](https://github.com/strictdoc-project/strictdoc/pull/135) ([mettta](https://github.com/mettta))
- export/html: document tree: switch to ul/li-based styles [\#134](https://github.com/strictdoc-project/strictdoc/pull/134) ([mettta](https://github.com/mettta))
- export/html: add main.content to index; move 'toc' vars to :root [\#133](https://github.com/strictdoc-project/strictdoc/pull/133) ([mettta](https://github.com/mettta))
- export/html: fix a.reference.external [\#127](https://github.com/strictdoc-project/strictdoc/pull/127) ([mettta](https://github.com/mettta))
- docs: good tweaks of the PDF front page  [\#125](https://github.com/strictdoc-project/strictdoc/pull/125) ([stanislaw](https://github.com/stanislaw))
- docs/sphinx: section numbers and titles: fix bottom alignment [\#124](https://github.com/strictdoc-project/strictdoc/pull/124) ([stanislaw](https://github.com/stanislaw))
- docs/sphinx: minor tweaks [\#123](https://github.com/strictdoc-project/strictdoc/pull/123) ([stanislaw](https://github.com/stanislaw))
- docs: merge all sdocs into one strictdoc.sdoc [\#122](https://github.com/strictdoc-project/strictdoc/pull/122) ([stanislaw](https://github.com/stanislaw))
- Revert: saturn -\> strictdoc :\) [\#121](https://github.com/strictdoc-project/strictdoc/pull/121) ([stanislaw](https://github.com/stanislaw))
- Rename: strictdoc -\> saturn  [\#120](https://github.com/strictdoc-project/strictdoc/pull/120) ([stanislaw](https://github.com/stanislaw))
- Styles [\#119](https://github.com/strictdoc-project/strictdoc/pull/119) ([mettta](https://github.com/mettta))
- docs: update roadmap and reqs [\#118](https://github.com/strictdoc-project/strictdoc/pull/118) ([stanislaw](https://github.com/stanislaw))
- Add Poetry skeleton  [\#116](https://github.com/strictdoc-project/strictdoc/pull/116) ([stanislaw](https://github.com/stanislaw))
- export/html: TOC: print req.uid if it is present otherwise NO TITLE  [\#115](https://github.com/strictdoc-project/strictdoc/pull/115) ([stanislaw](https://github.com/stanislaw))
- export/html: reuse requirement partial on TRACE and DEEP-TRACE pages [\#114](https://github.com/strictdoc-project/strictdoc/pull/114) ([stanislaw](https://github.com/stanislaw))
- export/html: view-traceability css \(arrows fix\) [\#113](https://github.com/strictdoc-project/strictdoc/pull/113) ([mettta](https://github.com/mettta))
- Styles [\#112](https://github.com/strictdoc-project/strictdoc/pull/112) ([mettta](https://github.com/mettta))
- grammar: fix single/multiline comments + regenerate tree if strictdoc changes [\#111](https://github.com/strictdoc-project/strictdoc/pull/111) ([stanislaw](https://github.com/stanislaw))
- export/html: export assets to \_assets folders  [\#110](https://github.com/strictdoc-project/strictdoc/pull/110) ([stanislaw](https://github.com/stanislaw))
- docs: update strictdoc reqs [\#107](https://github.com/strictdoc-project/strictdoc/pull/107) ([stanislaw](https://github.com/stanislaw))
- export/html: incremental generation of the documents [\#106](https://github.com/strictdoc-project/strictdoc/pull/106) ([stanislaw](https://github.com/stanislaw))
- export\_action: parallelize HTML generation and print duration time [\#105](https://github.com/strictdoc-project/strictdoc/pull/105) ([stanislaw](https://github.com/stanislaw))
-  export\_action: almost ready for parallelization but not  [\#104](https://github.com/strictdoc-project/strictdoc/pull/104) ([stanislaw](https://github.com/stanislaw))
-  export/html: rework output file structure \(now mirror source\)  [\#103](https://github.com/strictdoc-project/strictdoc/pull/103) ([stanislaw](https://github.com/stanislaw))
- docs: add implementation and scalability requirements [\#102](https://github.com/strictdoc-project/strictdoc/pull/102) ([stanislaw](https://github.com/stanislaw))
- Fix imports broken by CLion [\#101](https://github.com/strictdoc-project/strictdoc/pull/101) ([stanislaw](https://github.com/stanislaw))
- export/html: extract to generator classes to separate files [\#100](https://github.com/strictdoc-project/strictdoc/pull/100) ([stanislaw](https://github.com/stanislaw))
- export/html: Renderer: switch to cashing per object, not per text [\#99](https://github.com/strictdoc-project/strictdoc/pull/99) ([stanislaw](https://github.com/stanislaw))
- export/html: Traceability page: render RST [\#98](https://github.com/strictdoc-project/strictdoc/pull/98) ([stanislaw](https://github.com/stanislaw))
- Styles [\#97](https://github.com/strictdoc-project/strictdoc/pull/97) ([mettta](https://github.com/mettta))
- export/html:   top align table content [\#96](https://github.com/strictdoc-project/strictdoc/pull/96) ([mettta](https://github.com/mettta))
- export/html: table view \( html / css \) [\#95](https://github.com/strictdoc-project/strictdoc/pull/95) ([mettta](https://github.com/mettta))
- export/html: wrap sections into "\<div\>.section" [\#94](https://github.com/strictdoc-project/strictdoc/pull/94) ([stanislaw](https://github.com/stanislaw))
- export/html: Document page: add 'requirement' to outer requirement's div [\#93](https://github.com/strictdoc-project/strictdoc/pull/93) ([stanislaw](https://github.com/stanislaw))
- export/html: Table page: render RST-\>HTML [\#92](https://github.com/strictdoc-project/strictdoc/pull/92) ([stanislaw](https://github.com/stanislaw))
- export/html: new CSS styles for the Document page \(also first CSS work on Table\) [\#91](https://github.com/strictdoc-project/strictdoc/pull/91) ([stanislaw](https://github.com/stanislaw))
- single\_document.css: main.content typograph. styles [\#90](https://github.com/strictdoc-project/strictdoc/pull/90) ([mettta](https://github.com/mettta))
- docs: update roadmap, add Getting Started boilerplate [\#89](https://github.com/strictdoc-project/strictdoc/pull/89) ([stanislaw](https://github.com/stanislaw))
- export/html: remove \<br\>s [\#88](https://github.com/strictdoc-project/strictdoc/pull/88) ([stanislaw](https://github.com/stanislaw))
- layout-main-with-toc.css: fix .link-back-to-index [\#87](https://github.com/strictdoc-project/strictdoc/pull/87) ([mettta](https://github.com/mettta))
- export/html: render bold comment word with CSS [\#86](https://github.com/strictdoc-project/strictdoc/pull/86) ([stanislaw](https://github.com/stanislaw))
-  export/html: render comments via RST as well  [\#85](https://github.com/strictdoc-project/strictdoc/pull/85) ([stanislaw](https://github.com/stanislaw))
- export/html: add Table of Contents panel as \<aside\> tag with CSS styles [\#84](https://github.com/strictdoc-project/strictdoc/pull/84) ([stanislaw](https://github.com/stanislaw))
- export/html: \<span\> to each section/requirement to allow jumping to them [\#83](https://github.com/strictdoc-project/strictdoc/pull/83) ([stanislaw](https://github.com/stanislaw))
- export/html: Document page: render RST statements and free text with docutils [\#82](https://github.com/strictdoc-project/strictdoc/pull/82) ([stanislaw](https://github.com/stanislaw))
- export/html: Document page: introduce .section-number CSS class [\#81](https://github.com/strictdoc-project/strictdoc/pull/81) ([stanislaw](https://github.com/stanislaw))
- export/html: Document page: remove artificial space [\#80](https://github.com/strictdoc-project/strictdoc/pull/80) ([stanislaw](https://github.com/stanislaw))
-  export/html: table of contents template: switch to \<ul\> and \<li\>  [\#79](https://github.com/strictdoc-project/strictdoc/pull/79) ([stanislaw](https://github.com/stanislaw))
- export/html: new CSS styles for the document tree page [\#78](https://github.com/strictdoc-project/strictdoc/pull/78) ([stanislaw](https://github.com/stanislaw))
- export/pdf: fix TOC layout when starting from level 3 [\#77](https://github.com/strictdoc-project/strictdoc/pull/77) ([stanislaw](https://github.com/stanislaw))
- export/pdf improvements: switch to DejaVu Sans font, introduce metadata table instead of table logo [\#76](https://github.com/strictdoc-project/strictdoc/pull/76) ([stanislaw](https://github.com/stanislaw))
- docs: 2 items to roadmap [\#75](https://github.com/strictdoc-project/strictdoc/pull/75) ([stanislaw](https://github.com/stanislaw))
- export/html: add last class class to simplify CSS [\#74](https://github.com/strictdoc-project/strictdoc/pull/74) ([stanislaw](https://github.com/stanislaw))
- dsl/reader: specific case of setting ng\_level for composite requirement [\#73](https://github.com/strictdoc-project/strictdoc/pull/73) ([stanislaw](https://github.com/stanislaw))
- docs: add empty introduction [\#72](https://github.com/strictdoc-project/strictdoc/pull/72) ([stanislaw](https://github.com/stanislaw))
- export/html: add more classes to enable further CSS styles work [\#71](https://github.com/strictdoc-project/strictdoc/pull/71) ([stanislaw](https://github.com/stanislaw))
-  export/html: table view: switch from 'display: table' to \<table\>  [\#70](https://github.com/strictdoc-project/strictdoc/pull/70) ([stanislaw](https://github.com/stanislaw))
-  export/html: document\_tree: split into name and document link cells  [\#69](https://github.com/strictdoc-project/strictdoc/pull/69) ([stanislaw](https://github.com/stanislaw))
- document\_finder: switch to depth-first search [\#68](https://github.com/strictdoc-project/strictdoc/pull/68) ([stanislaw](https://github.com/stanislaw))
-  export/pdf: better layout of the table logo and other styles [\#67](https://github.com/strictdoc-project/strictdoc/pull/67) ([stanislaw](https://github.com/stanislaw))
- export/pdf: automatic generation of the PDF using Sphinx [\#66](https://github.com/strictdoc-project/strictdoc/pull/66) ([stanislaw](https://github.com/stanislaw))
- export/rst: Initial export code [\#65](https://github.com/strictdoc-project/strictdoc/pull/65) ([stanislaw](https://github.com/stanislaw))
- tests/integration: self-testing passthrough [\#64](https://github.com/strictdoc-project/strictdoc/pull/64) ([stanislaw](https://github.com/stanislaw))
- tests/integration: Hello World passthrough test [\#63](https://github.com/strictdoc-project/strictdoc/pull/63) ([stanislaw](https://github.com/stanislaw))
- Support mounting multiple doc trees into a single export [\#62](https://github.com/strictdoc-project/strictdoc/pull/62) ([stanislaw](https://github.com/stanislaw))
-  export/html: Improve automatic numeration of the titles  [\#61](https://github.com/strictdoc-project/strictdoc/pull/61) ([stanislaw](https://github.com/stanislaw))
- export/html: single\_document\_table: minor fix [\#60](https://github.com/strictdoc-project/strictdoc/pull/60) ([stanislaw](https://github.com/stanislaw))
- docs: add more titles and some links  [\#59](https://github.com/strictdoc-project/strictdoc/pull/59) ([stanislaw](https://github.com/stanislaw))
- export/html: enable HTML title counters [\#58](https://github.com/strictdoc-project/strictdoc/pull/58) ([stanislaw](https://github.com/stanislaw))
- Grammar: Support \[COMPOSITE-REQUIREMENT\] [\#57](https://github.com/strictdoc-project/strictdoc/pull/57) ([stanislaw](https://github.com/stanislaw))
- export/html: simplify traceability page styles for now [\#56](https://github.com/strictdoc-project/strictdoc/pull/56) ([stanislaw](https://github.com/stanislaw))
- grammar: support \[FREETEXT\] [\#55](https://github.com/strictdoc-project/strictdoc/pull/55) ([stanislaw](https://github.com/stanislaw))
- export/html: initial table view page [\#54](https://github.com/strictdoc-project/strictdoc/pull/54) ([stanislaw](https://github.com/stanislaw))
- export/html/export.py: remove obsolete code [\#53](https://github.com/strictdoc-project/strictdoc/pull/53) ([stanislaw](https://github.com/stanislaw))
- export/html: print statement in paragraphs [\#52](https://github.com/strictdoc-project/strictdoc/pull/52) ([stanislaw](https://github.com/stanislaw))
- pan-with-space.js: fix copy and paste functionality that was blocked [\#51](https://github.com/strictdoc-project/strictdoc/pull/51) ([stanislaw](https://github.com/stanislaw))
- DSL: Grammar: Support multiline statements [\#50](https://github.com/strictdoc-project/strictdoc/pull/50) ([stanislaw](https://github.com/stanislaw))
- export/html: Pan with space key and scroll to middle on Deep Traceability pages  [\#49](https://github.com/strictdoc-project/strictdoc/pull/49) ([stanislaw](https://github.com/stanislaw))
- export/html: remove \<pre\> from content body part [\#48](https://github.com/strictdoc-project/strictdoc/pull/48) ([stanislaw](https://github.com/stanislaw))
- export/html: Table-based document tree [\#47](https://github.com/strictdoc-project/strictdoc/pull/47) ([stanislaw](https://github.com/stanislaw))
- html/export: Deep Traceability document, first take  [\#46](https://github.com/strictdoc-project/strictdoc/pull/46) ([stanislaw](https://github.com/stanislaw))
- export/html: global CSS style [\#45](https://github.com/strictdoc-project/strictdoc/pull/45) ([stanislaw](https://github.com/stanislaw))
- export/html: display tags [\#44](https://github.com/strictdoc-project/strictdoc/pull/44) ([stanislaw](https://github.com/stanislaw))
-  export/html and dsl: introduce multiline comments  [\#43](https://github.com/strictdoc-project/strictdoc/pull/43) ([stanislaw](https://github.com/stanislaw))
-  export/html: traceability page displays comments  [\#42](https://github.com/strictdoc-project/strictdoc/pull/42) ([stanislaw](https://github.com/stanislaw))
- export/html: hacks to make borders collapse on traceability page [\#41](https://github.com/strictdoc-project/strictdoc/pull/41) ([stanislaw](https://github.com/stanislaw))
-  export/html: better styles for traceability page  [\#40](https://github.com/strictdoc-project/strictdoc/pull/40) ([stanislaw](https://github.com/stanislaw))
-  export/html: traceability: anchor links to sections  [\#39](https://github.com/strictdoc-project/strictdoc/pull/39) ([stanislaw](https://github.com/stanislaw))
- export/html: first traceability matrix [\#38](https://github.com/strictdoc-project/strictdoc/pull/38) ([stanislaw](https://github.com/stanislaw))
- DSL: Newline after \[/SECTION\] [\#37](https://github.com/strictdoc-project/strictdoc/pull/37) ([stanislaw](https://github.com/stanislaw))
- DSL: Tags support. Also introduce skipws everywhere in the grammar.  [\#36](https://github.com/strictdoc-project/strictdoc/pull/36) ([stanislaw](https://github.com/stanislaw))
-  export/html: export sections recursively, export TOCs  [\#35](https://github.com/strictdoc-project/strictdoc/pull/35) ([stanislaw](https://github.com/stanislaw))
- Export HTML: Sort dirs/files, add links [\#34](https://github.com/strictdoc-project/strictdoc/pull/34) ([stanislaw](https://github.com/stanislaw))
- export/html: switch to Jinja2 template engine [\#33](https://github.com/strictdoc-project/strictdoc/pull/33) ([stanislaw](https://github.com/stanislaw))
- export: basic export to HTML: document tree structure [\#32](https://github.com/strictdoc-project/strictdoc/pull/32) ([stanislaw](https://github.com/stanislaw))
- strictdoc/backend/dsl: introduce optional REQUIREMENT\#STATUS parameter [\#31](https://github.com/strictdoc-project/strictdoc/pull/31) ([stanislaw](https://github.com/stanislaw))
- strictdoc.strictdoc: document requirement item: existing fields [\#30](https://github.com/strictdoc-project/strictdoc/pull/30) ([stanislaw](https://github.com/stanislaw))
- strictdoc/backend/dsl: introduce optional REQUIREMENT\#UID parameter [\#29](https://github.com/strictdoc-project/strictdoc/pull/29) ([stanislaw](https://github.com/stanislaw))
- strictdoc/backend/dsl: Requirement has\_many references [\#28](https://github.com/strictdoc-project/strictdoc/pull/28) ([stanislaw](https://github.com/stanislaw))
-  New StrictDoc DSL: reading input and writing output  [\#27](https://github.com/strictdoc-project/strictdoc/pull/27) ([stanislaw](https://github.com/stanislaw))
- Table view: detecting right click on cells and showing context menu [\#26](https://github.com/strictdoc-project/strictdoc/pull/26) ([stanislaw](https://github.com/stanislaw))
- table view: stretching text to the full cell width seems to work [\#25](https://github.com/strictdoc-project/strictdoc/pull/25) ([stanislaw](https://github.com/stanislaw))
-  table view: fix animation of background cell when editing  [\#24](https://github.com/strictdoc-project/strictdoc/pull/24) ([stanislaw](https://github.com/stanislaw))
- Styles, document model and item delegate: remove blue selection, fix margins [\#23](https://github.com/strictdoc-project/strictdoc/pull/23) ([stanislaw](https://github.com/stanislaw))
- TableView: disable horizontal and vertical headers for now [\#22](https://github.com/strictdoc-project/strictdoc/pull/22) ([stanislaw](https://github.com/stanislaw))
- document metadata: specify fields that must be recognized in metadata nodes [\#20](https://github.com/strictdoc-project/strictdoc/pull/20) ([stanislaw](https://github.com/stanislaw))
- rst\_node\_finder: fix looking for paragraphs which are easier to find parents for [\#19](https://github.com/strictdoc-project/strictdoc/pull/19) ([stanislaw](https://github.com/stanislaw))
-  strictdoc/core/logger: logger class to allow logging of selected classes  [\#18](https://github.com/strictdoc-project/strictdoc/pull/18) ([stanislaw](https://github.com/stanislaw))
-  backend/rst/rst\_document\_editor: replace paragraph with paragraph  [\#17](https://github.com/strictdoc-project/strictdoc/pull/17) ([stanislaw](https://github.com/stanislaw))
-  backend/rst: moving basic nodes around RST tree  [\#16](https://github.com/strictdoc-project/strictdoc/pull/16) ([stanislaw](https://github.com/stanislaw))
- backend/rst: recognize level 4 headers [\#15](https://github.com/strictdoc-project/strictdoc/pull/15) ([stanislaw](https://github.com/stanislaw))
- backend/rst: switch to parsing header levels based on their source code lines [\#14](https://github.com/strictdoc-project/strictdoc/pull/14) ([stanislaw](https://github.com/stanislaw))
- tests/unit: move tests out of the src/ [\#13](https://github.com/strictdoc-project/strictdoc/pull/13) ([stanislaw](https://github.com/stanislaw))
- Document: Rendering HTML in view mode and RST in edit mode \(first steps\) [\#10](https://github.com/strictdoc-project/strictdoc/pull/10) ([stanislaw](https://github.com/stanislaw))
- rst: assign header level to the section nodes when reading RST [\#9](https://github.com/strictdoc-project/strictdoc/pull/9) ([stanislaw](https://github.com/stanislaw))
- backend/rst: basic test\_rst\_reader unit test [\#7](https://github.com/strictdoc-project/strictdoc/pull/7) ([stanislaw](https://github.com/stanislaw))
- strictdoc/backend/rst: proper namespacing [\#6](https://github.com/strictdoc-project/strictdoc/pull/6) ([stanislaw](https://github.com/stanislaw))
- backend/rst: create dedicated Parser and Reader classes [\#5](https://github.com/strictdoc-project/strictdoc/pull/5) ([stanislaw](https://github.com/stanislaw))
- backend: rst to html writer prototype [\#2](https://github.com/strictdoc-project/strictdoc/pull/2) ([stanislaw](https://github.com/stanislaw))
- gui: make a table cell resize when its edit-mode cell is being edited/resized [\#1](https://github.com/strictdoc-project/strictdoc/pull/1) ([stanislaw](https://github.com/stanislaw))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
