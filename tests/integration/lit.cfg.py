# ruff: noqa: F821

import os
import sys
from typing import Any

import lit.formats

config: Any
lit_config: Any

config.name = "StrictDoc integration tests"
config.test_format = lit.formats.ShTest("0")

current_dir = os.getcwd()

strictdoc_exec = lit_config.params["STRICTDOC_EXEC"]
assert strictdoc_exec

config.substitutions.append(
    ("%STRICTDOC_TMP_DIR", lit_config.params["STRICTDOC_TMP_DIR"])
)

# NOTE: All substitutions work for the RUN: statements but they don't for CHECK:.
#       That's how LLVM LIT works.
config.substitutions.append(("%THIS_TEST_FOLDER", '$(basename "%S")'))

config.substitutions.append(("%strictdoc_root", current_dir))
config.substitutions.append(("%strictdoc", strictdoc_exec))

config.substitutions.append(
    ("%cat", f'python "{current_dir}/tests/integration/cat.py"')
)
config.substitutions.append(
    (
        "%check_exists",
        f'python "{current_dir}/tests/integration/check_exists.py"',
    )
)
config.substitutions.append(
    ("%cp", f'python "{current_dir}/tests/integration/cp.py"')
)
config.substitutions.append(("%diff", "diff --strip-trailing-cr"))
config.substitutions.append(
    (
        "%excel_diff",
        f'python "{current_dir}/tests/integration/excel_diff.py"',
    )
)
config.substitutions.append(
    (
        "%expect_exit",
        f'python "{current_dir}/tests/integration/expect_exit.py"',
    )
)
config.substitutions.append(
    (
        "%html_markup_validator",
        f'python "{current_dir}/tests/integration/html_markup_validator.py"',
    )
)
config.substitutions.append(
    ("%mkdir", f'python "{current_dir}/tests/integration/mkdir.py"')
)
config.substitutions.append(
    ("%rm", f'python "{current_dir}/tests/integration/rm.py"')
)
config.substitutions.append(
    ("%touch", f'python "{current_dir}/tests/integration/touch.py"')
)

config.suffixes = [".itest"]

if sys.version_info >= (3, 9):
    config.available_features.add("PYTHON_39_OR_HIGHER")

config.is_windows = lit_config.isWindows
if not lit_config.isWindows:
    config.available_features.add("PLATFORM_IS_NOT_WINDOWS")

if "TEST_HTML2PDF" in lit_config.params:
    config.name = "StrictDoc HTML2PDF integration tests"
    # In Linux CI, $HOME is required for Chrome as it needs to access things in ~/.local
    config.environment["HOME"] = os.environ.get("HOME", "/tmp")

    # In Windows CI, %ProgramW6432% is required for Selenium to properly detect browsers
    config.environment["ProgramW6432"] = os.environ.get("ProgramW6432", "")

    config.available_features.add("TEST_HTML2PDF")
    if "CHROMEDRIVER" in lit_config.params:
        chromedriver = lit_config.params["CHROMEDRIVER"]
        if lit_config.isWindows:
            # On Windows, we need to escape the backward-slashes as lit runs this through another shell
            chromedriver = chromedriver.replace("\\", "\\\\")
        config.substitutions.append(("%chromedriver", chromedriver))
        config.available_features.add("SYSTEM_CHROMEDRIVER")

if "COVERAGE_FILE" in lit_config.params:
    config.environment["COVERAGE_FILE"] = lit_config.params["COVERAGE_FILE"]
    config.environment["COVERAGE_PROCESS_START"] = lit_config.params[
        "COVERAGE_PROCESS_START"
    ]

if (env_cache_dir := os.getenv("STRICTDOC_CACHE_DIR", None)) is not None:
    config.environment["STRICTDOC_CACHE_DIR"] = env_cache_dir

# GITHUB_ACTIONS must be passed in order for StrictDoc's environment.py to see it.
if (env_github_actions_ci := os.getenv("GITHUB_ACTIONS", None)) is not None:
    config.environment["GITHUB_ACTIONS"] = env_github_actions_ci

config.excludes.add("test.ignored.itest")
