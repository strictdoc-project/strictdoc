# GCOV/gcovr: C++ namespaces and function-name matching

## WHAT

- Improve GCOV/gcovr interoperability for C++ namespaced member functions.
- Resolve the two issues pointed out by the user:
  - GCOV report links used a file path/hash that did not exist.
  - gcovr C++ function names did not match the names extracted by StrictDoc's C/C++ reader.
- Follow the Dev Guide.
- Always add tests.

## WHY

GCOV support in StrictDoc is still rudimentary as of June 2026.

We received a bug report where a user is trying to use GCOV/gcovr against a C++ program that is larger than a trivial Hello World:

https://github.com/strictdoc-project/strictdoc/issues/2717

They summarize the issues as follows:

> Currently the link in the coverage report uses a filename/path which does not exist. Additionally, when running this on C++ code the function names provided by gcov do not match the function names detected by treesitter (in the reader_c.py).

## HOW

### Implementation details

- Fixed GCOV JSON reader function-name handling for C++.
  - gcovr can emit both `name` and `demangled_name`.
  - StrictDoc now prefers `demangled_name` and falls back to `name`.

- Fixed GCOV HTML detail links.
  - The link hash now uses the actual source file path from the gcovr JSON report.
  - This removed the previous hardcoded `src/main.c` behavior.
  - gcovr file paths are normalized in the GCOV reader before StrictDoc uses
    them for UIDs, file references, and gcov HTML detail links.
  - On Windows, absolute gcovr paths are relativized against
    `project_config.source_root_path`, so StrictDoc uses the same
    project-relative POSIX paths as the source-file index.

- Added gcovr-style C++ function-name matching.
  - StrictDoc/tree-sitter names such as:
    - `test::Adder::add(const int& a, const int& b)`
  - can now match gcovr names such as:
    - `test::Adder::add(int const&, int const&)`
  - `FileTraceabilityIndex.get_function_matching_names()` now tries:
    - display name,
    - full parser name,
    - gcovr-style canonical name.

- Added `strictdoc/backend/gcov/helpers.py`.
  - Contains GCOV-specific C++ name canonicalization helpers.
  - Internal helper functions are private and documented with examples.

- Added regression tests.
  - Unit tests for GCOV/gcovr C++ name conversion.
  - Unit tests for GCOV JSON `demangled_name` precedence.
  - Unit tests for real source-file hash links.
  - Unit tests for Windows-style and Windows-absolute gcovr source paths.
  - Integration test:
    - `tests/integration/features/code_coverage_gcov/02_cpp_namespace_gcovr_issue_2717`

- Adjusted the integration test to avoid Windows-fragile global source coverage table assumptions.
  - The stronger assertion is now on the generated `functions.cpp` source-file page, scoped to the file under test.

### Verification

- Focused unit tests:
  - `tests/unit/strictdoc/core/test_file_traceability_index.py`
  - `tests/unit/strictdoc/backend/gcov/test_helpers.py`
  - `tests/unit/strictdoc/backend/sdoc_source_code/coverage_reports/test_gcov.py`
- Integration tests:
  - `invoke ti --focus code_coverage_gcov`
- Lint:
  - `ruff check` on changed Python files.
