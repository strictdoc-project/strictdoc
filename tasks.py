# Invoke is broken on Python 3.11
# https://github.com/pyinvoke/invoke/issues/833#issuecomment-1293148106
import inspect
import os
import re
import shutil
import sys
import tempfile
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

import invoke
from invoke import task

# Specifying encoding because Windows crashes otherwise when running Invoke
# tasks below:
# UnicodeEncodeError: 'charmap' codec can't encode character '\ufffd'
# in position 16: character maps to <undefined>
# People say, it might also be possible to export PYTHONIOENCODING=utf8 but this
# seems to work.
# FIXME: If you are a Windows user and expert, please advise on how to do this
# properly.
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)

STRICTDOC_TMP_DIR = os.path.join(tempfile.gettempdir(), "strictdoc_tmp_dir")
TEST_REPORTS_DIR = "build/test_reports"


# To prevent all tasks from building to the same virtual environment.
# All values correspond to the configuration in the tox.ini config file.
class ToxEnvironment(str, Enum):
    DEVELOPMENT = "development"
    CHECK = "check"
    DOCUMENTATION = "documentation"
    RELEASE = "release"
    RELEASE_LOCAL = "release-local"
    PYINSTALLER = "pyinstaller"


def run_invoke(
    context,
    cmd,
    environment: Optional[dict] = None,
    pty: bool = False,
    warn: bool = False,
) -> invoke.runners.Result:
    def one_line_command(string):
        return re.sub("\\s+", " ", string).strip()

    return context.run(
        one_line_command(cmd),
        env=environment,
        hide=False,
        warn=warn,
        pty=pty,
        echo=True,
    )


def run_invoke_with_tox(
    context,
    environment_type: ToxEnvironment,
    command: str,
    environment: Optional[Dict] = None,
    pty: bool = False,
) -> invoke.runners.Result:
    assert isinstance(environment_type, ToxEnvironment)
    assert isinstance(command, str)

    tox_py_version = f"py{sys.version_info.major}{sys.version_info.minor}"

    return run_invoke(
        context,
        f"""
            tox
                -e {tox_py_version}-{environment_type.value} --
                {command}
        """,
        environment=environment,
        pty=pty,
    )


@task(default=True)
def list_tasks(context):
    clean_command = """
        invoke --list
    """
    run_invoke(context, clean_command)


@task
def clean(context):
    # https://unix.stackexchange.com/a/689930/77389
    clean_command = """
        rm -rf output/ docs/sphinx/build/
    """
    run_invoke(context, clean_command)


@task(aliases=["s"])
def server(context, input_path=".", config=None):
    assert os.path.isdir(input_path), input_path
    if config is not None:
        assert os.path.isfile(config), config
    config_argument = f"--config {config}" if config is not None else ""
    run_invoke_with_tox(
        context,
        ToxEnvironment.DEVELOPMENT,
        f"""
            python -m strictdoc.cli.main
                server {input_path} {config_argument}
                    --host 127.0.0.1
                    --output-path ./output/server
                    --reload
        """,
    )


@task(aliases=["d"])
def docs(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            python3 strictdoc/cli/main.py
                export .
                    --formats=html
                    --output-dir output/strictdoc_website
                    --project-title "StrictDoc"
        """,
    )

    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            python3 strictdoc/cli/main.py
                export ./
                    --formats=rst
                    --output-dir output/sphinx
                    --project-title "StrictDoc"
        """,
    )

    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            cp -r output/sphinx/rst/docs/* docs/sphinx/source/ &&
            cp -r output/sphinx/rst/docs_extra/* docs/sphinx/source/ &&
            mkdir -p docs/sphinx/source/_assets/ &&
            cp -v docs/_assets/* docs/sphinx/source/_assets/
        """,
    )

    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            make --directory docs/sphinx html latexpdf SPHINXOPTS="-W --keep-going"
        """,
    )

    run_invoke(
        context,
        (
            """
                open docs/sphinx/build/latex/strictdoc.pdf
            """
        ),
    )


@task(aliases=["tus"])
def test_unit_server(context, focus=None):
    focus_argument = f"-k {focus}" if focus is not None else ""

    Path(TEST_REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    cwd = os.getcwd()

    path_to_coverage_file = f"{cwd}/build/coverage/unit_server/.coverage"

    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            coverage run
            --rcfile=.coveragerc.unit_server
            --data-file={path_to_coverage_file}
            -m pytest
            tests/unit_server/
                {focus_argument}
                --junit-xml={TEST_REPORTS_DIR}/tests_unit_server.pytest.junit.xml
                -o junit_suite_name="StrictDoc Web Server Unit Tests"
                -o cache_dir=build/pytest_unit_server
        """,
    )


@task(test_unit_server, aliases=["tusc"])
def test_unit_server_report(context):
    cwd = os.getcwd()

    path_to_coverage_file = f"{cwd}/build/coverage/unit_server/.coverage"

    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            coverage html
                --rcfile=.coveragerc.unit_server
                --data-file={path_to_coverage_file}
        """,
    )


@task(aliases=["te"])
def test_end2end(
    context,
    *,
    focus=None,
    exit_first=False,
    parallelize=False,
    long_timeouts=False,
    headless=False,
    shard=None,
    test_path=None,
    coverage: bool = False,
):
    environment = {}

    coverage_command_or_none = ""
    coverage_argument_or_none = ""

    if coverage:
        cwd = os.getcwd()
        coverage_file_dir = f"{cwd}/build/coverage/end2end/"
        coverage_file_dir2 = f"{cwd}/build/coverage/end2end_strictdoc/"
        coverage_file = os.path.join(coverage_file_dir, ".coverage")
        coverage_rc = os.path.join(cwd, ".coveragerc.end2end")
        shutil.rmtree(coverage_file_dir, ignore_errors=True)
        shutil.rmtree(coverage_file_dir2, ignore_errors=True)
        coverage_command_or_none = f"""
            coverage run
                --rcfile={coverage_rc}
                --data-file={coverage_file}
                -m
        """
        coverage_argument_or_none = "--strictdoc-coverage"

    long_timeouts_argument = (
        "--strictdoc-long-timeouts" if long_timeouts else ""
    )

    parallelize_argument = ""
    if parallelize:
        print(  # noqa: T201
            "warning: "
            "Running parallelized end-2-end tests is supported "
            "but is not stable."
        )
        parallelize_argument = "--numprocesses=2 --strictdoc-parallelize"

    assert shard is None or re.match(r"[1-9][0-9]*/[1-9][0-9]*", shard), (
        f"--shard argument has an incorrect format: {shard}."
    )
    shard_argument = f"--strictdoc-shard={shard}" if shard else ""

    focus_argument = f"-k {focus}" if focus is not None else ""
    exit_first_argument = "--exitfirst" if exit_first else ""
    headless_argument = "--headless2" if headless else ""
    test_command = f"""
            {coverage_command_or_none}
            pytest
            --failed-first
            --capture=no
            --reuse-session
            {parallelize_argument}
            {shard_argument}
            {coverage_argument_or_none}
            {focus_argument}
            {exit_first_argument}
            {long_timeouts_argument}
            {headless_argument}
            --junit-xml={TEST_REPORTS_DIR}/tests_end2end.pytest.junit.xml
            -o junit_suite_name="StrictDoc End-to-End Tests"
            -o cache_dir=build/pytest_end2end
            tests/end2end
    """
    if test_path:
        test_command = test_command.rstrip() + f"/{test_path}"

    Path(TEST_REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    # On Windows, GitHub Actions fails with:
    # response = {'status': 500, 'value':
    # '{"value":{"error":"unknown error",
    # "message":"unknown error: cannot find Chrome binary",  # noqa: ERA001
    # This very likely has to do with PATH isolation that Tox does.
    # FIXME: If you are a Windows expert, please fix this to run on Tox.
    if os.name == "nt":
        run_invoke(context, test_command)
        return

    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        test_command,
        environment=environment,
    )


@task(aliases=["tu"])
def test_unit(context, focus=None, output=False):
    Path(TEST_REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    focus_argument = f"-k {focus}" if focus is not None else ""
    output_argument = "--capture=no" if output else ""

    cwd = os.getcwd()

    path_to_coverage_file = f"{cwd}/build/coverage/unit/.coverage"
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            coverage run
            --rcfile=.coveragerc.unit
            --data-file={path_to_coverage_file}
            -m pytest
            {focus_argument}
            {output_argument}
            --junit-xml={TEST_REPORTS_DIR}/tests_unit.pytest.junit.xml
            -o cache_dir=build/pytest_unit_with_coverage
            -o junit_suite_name="StrictDoc Unit Tests"
            tests/unit/
        """,
    )
    if not focus:
        run_invoke_with_tox(
            context,
            ToxEnvironment.CHECK,
            f"""
                coverage report
                    --sort=cover
                    --rcfile=.coveragerc.unit
                    --data-file={path_to_coverage_file}
            """,
        )


@task(test_unit, aliases=["tuc"])
def test_unit_report(context):
    cwd = os.getcwd()

    path_to_coverage_file = f"{cwd}/build/coverage/unit/.coverage"

    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            coverage html
                --rcfile=.coveragerc.unit
                --data-file={path_to_coverage_file}
        """,
    )


@task(aliases=["ti"])
def test_integration(
    context,
    focus=None,
    debug=False,
    no_parallelization=False,
    fail_first=False,
    coverage=False,
    strictdoc=None,
    html2pdf=False,
    shard=None,
    environment=ToxEnvironment.CHECK,
):
    cwd = os.getcwd()

    if strictdoc is None:
        strictdoc_exec = f'python3 \\"{cwd}/strictdoc/cli/main.py\\"'
    else:
        strictdoc_exec = strictdoc

    coverage_path_argument = ""
    if coverage:
        path_to_coverage_rc = f"{cwd}/.coveragerc.integration"
        strictdoc_exec = f'coverage run --rcfile={path_to_coverage_rc} \\"{cwd}/strictdoc/cli/main.py\\"'
        if html2pdf:
            path_to_coverage_dir = f"{cwd}/build/coverage/integration_html2pdf/"
        else:
            path_to_coverage_dir = f"{cwd}/build/coverage/integration/"
        path_to_coverage = os.path.join(path_to_coverage_dir, ".coverage")
        shutil.rmtree(path_to_coverage_dir, ignore_errors=True)
        coverage_path_argument = (
            f'--param COVERAGE_FILE="{path_to_coverage}" '
            f'--param COVERAGE_PROCESS_START="{path_to_coverage_rc}"'
        )

    debug_opts = "-vv --show-all" if debug else ""
    focus_or_none = f"--filter {focus}" if focus else ""
    fail_first_argument = "--max-failures 1" if fail_first else ""
    junit_xml_report_argument = (
        "--xunit-xml-output build/test_reports/tests_integration_html2pdf.lit.junit.xml"
        if html2pdf
        else "--xunit-xml-output build/test_reports/tests_integration.lit.junit.xml"
    )

    # Allow partitioning of integration and html2pdf tests
    partition_opts = ""
    if shard is not None:
        match = re.match(r"([1-9][0-9]*)/([1-9][0-9]*)", shard)
        assert match, f"--shard argument has an incorrect format: {shard}."
        run_shard = int(match.group(1))
        num_shards = int(match.group(2))
        partition_opts = f"--num-shards={num_shards} --run-shard={run_shard}"

    # HTML2PDF tests are running Chrome Driver which does not seem to be
    # parallelizable, or at least not in the way StrictDoc uses it.
    # If HTML2PDF option is provided, do not parallelize and only run the
    # HTML2PDF-specific tests.
    # HTML2PDF tests can be safely partitioned.
    chromedriver_param = ""
    if not html2pdf:
        parallelize_opts = "" if not no_parallelization else "--threads 1"
        html2pdf_param = ""
        test_folder = f"{cwd}/tests/integration"
        test_output_dir = "build/tests_integration"
    else:
        parallelize_opts = "--threads 1"
        html2pdf_param = "--param TEST_HTML2PDF=1"
        chromedriver_path = os.environ.get("CHROMEWEBDRIVER")
        if chromedriver_path is not None:
            # NOTE: isfile() check does not work on GitHub Actions / Linux,
            #       the exists() check works.
            assert os.path.exists(chromedriver_path), chromedriver_path
            chromedriver_param = f"--param CHROMEDRIVER={os.path.join(chromedriver_path, 'chromedriver')}"
            if os.name == "nt":
                # On Windows, its chromdriver.exe
                chromedriver_param = chromedriver_param + ".exe"
        test_folder = f"{cwd}/tests/integration/features/html2pdf"
        test_output_dir = "build/tests_integration_html2pdf"

    # The command sometimes exits with 1 even if the files are deleted.
    # warn=True ensures that the execution continues.
    run_invoke(
        context,
        f"""
        rm -rf {test_output_dir}
        """,
        warn=True,
    )

    run_invoke(
        context,
        f"""
        rm -rf {STRICTDOC_TMP_DIR}
        """,
    )

    Path(STRICTDOC_TMP_DIR).mkdir(exist_ok=True)
    Path(TEST_REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    itest_command = f"""
        lit
        --param STRICTDOC_EXEC="{strictdoc_exec}"
        --param STRICTDOC_TMP_DIR="{STRICTDOC_TMP_DIR}"
        --param TEST_OUTPUT_DIR="{test_output_dir}"
        --timeout 180
        --order smart
        {junit_xml_report_argument}
        {coverage_path_argument}
        {html2pdf_param}
        {chromedriver_param}
        -v
        {debug_opts}
        {focus_or_none}
        {fail_first_argument}
        {parallelize_opts}
        {partition_opts}
        {test_folder}
    """

    # It looks like LIT does not open the RUN: subprocesses in the same
    # environment from which it itself is run from. This issue has been known by
    # us for a couple of years by now. Not using Tox on Windows for the time
    # being.
    if os.name == "nt":
        run_invoke(context, itest_command)
        return

    run_invoke_with_tox(
        context,
        environment,
        itest_command,
        environment={"STRICTDOC_CACHE_DIR": "Output/_cache"},
    )


@task
def coverage_combine(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            coverage combine
                --data-file build/coverage/.coverage.combined
                --keep
                build/coverage/end2end_strictdoc/.coverage.*
                build/coverage/integration/.coverage.*
                build/coverage/integration_html2pdf/.coverage.*
                build/coverage/unit/.coverage
                build/coverage/unit_server/.coverage
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            coverage html
                --rcfile .coveragerc.combined
                --data-file build/coverage/.coverage.combined
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            coverage json
                --rcfile .coveragerc.combined
                --data-file build/coverage/.coverage.combined
                --pretty-print
                -o build/coverage/coverage.combined.json
        """,
    )


@task
def lint_black(context):
    result: invoke.runners.Result = run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            black
                *.py
                developer/
                strictdoc/
                tests/unit/
                tests/integration/*.py
                tests/end2end/
            --color --line-length 80 2>&1
        """,
    )
    # black always exits with 0, so we handle the output.
    if "reformatted" in result.stdout:
        print("invoke: black found issues")  # noqa: T201
        result.exited = 1
        raise invoke.exceptions.UnexpectedExit(result)


@task
def lint_ruff_format(context):
    result: invoke.runners.Result = run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            ruff
                format
                *.py
                developer/
                strictdoc/
                tests/unit/
                tests/integration/*.py
                tests/end2end/
        """,
    )
    # Ruff always exits with 0, so we handle the output.
    if "reformatted" in result.stdout:
        print("invoke: ruff format found issues")  # noqa: T201
        result.exited = 1
        raise invoke.exceptions.UnexpectedExit(result)


@task(aliases=["lr"])
def lint_ruff(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            ruff check . --fix --cache-dir build/ruff
        """,
    )


# @sdoc[SDOC-SRS-43]
@task(aliases=["lm"])
def lint_mypy(context):
    # These checks do not seem to be useful:
    # - import
    # - misc
    # type-abstract is ignored on purpose because of assert_cast() implementation.
    # See https://stackoverflow.com/a/74073453/598057.
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            mypy strictdoc/
                --show-error-codes
                --disable-error-code=import
                --disable-error-code=misc
                --disable-error-code=type-abstract
                --cache-dir=build/mypy
                --strict
                --python-version=3.8
        """,
    )


# # @sdoc[/SDOC-SRS-43]


@task(aliases=["lf"])
def lint_fixit(context, fix=False, auto=False, path="strictdoc/"):
    if fix:
        auto_argument = "--automatic" if auto else ""
        run_invoke_with_tox(
            context,
            ToxEnvironment.CHECK,
            f"""
                fixit fix {path} {auto_argument}
            """,
            pty=True,
        )
    else:
        run_invoke_with_tox(
            context,
            ToxEnvironment.CHECK,
            f"""
                fixit lint --diff {path}
            """,
        )


@task(aliases=["l"])
def lint(context):
    lint_ruff_format(context)
    lint_ruff(context)
    lint_mypy(context)


@task(aliases=["t"])
def test(context, shard=None):
    test_unit(context)
    test_unit_server(context)
    test_integration(context, shard=shard)
    test_integration(context, shard=shard, html2pdf=True)


@task(aliases=["ta"])
def test_all(context, coverage=False, headless=False):
    test_unit(context)
    test_unit_server(context)
    test_integration(context, coverage=coverage)
    test_integration(context, coverage=coverage, html2pdf=True)
    test_end2end(context, coverage=coverage, headless=headless)


@task(aliases=["c"])
def check(context):
    lint(context)
    test(context)


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(context, github_token):
    # The alpha release tags are excluded from the changelog.
    command = f"""
        github_changelog_generator
        --token {github_token}
        --user strictdoc-project
        --exclude-tags-regex ".*a\\d+"
        --project strictdoc
        """
    run_invoke(context, command)


@task
def dump_grammar(context, output_file):
    command = f"""
        python3 strictdoc/cli/main.py dump-grammar {output_file}
    """
    run_invoke(context, command)


@task
def check_dead_links(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_01_user_guide.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_02_feature_map.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_03_faq.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_04_release_notes.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_05_troubleshooting.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_10_contributing.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_11_developer_guide.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_24_development_plan.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_20_L1_Open_Requirements_Tool.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_21_L2_StrictDoc_Requirements.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_25_design.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py CONTRIBUTING.md
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py NOTICE
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py README.md
        """,
    )


@task
def release_local(context):
    run_invoke(
        context,
        """
            rm -rfv dist/ build/
        """,
    )
    run_invoke(
        context,
        """
            pip uninstall strictdoc -y
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.RELEASE_LOCAL,
        """
            python -m build
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.RELEASE_LOCAL,
        """
            twine check dist/*
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.RELEASE_LOCAL,
        """
            pip install dist/*.tar.gz
        """,
    )
    test_integration(
        context, strictdoc="strictdoc", environment=ToxEnvironment.RELEASE_LOCAL
    )


@task
def release(context, test_pypi=False, username=None, password=None):
    """
    A release can be made to PyPI or test package index (TestPyPI):
    https://pypi.org/project/strictdoc/
    https://test.pypi.org/project/strictdoc/
    """

    # When a username is provided, we also need password, and then we don't use
    # tokens set up on a local machine.
    assert username is None or password is not None

    repository_argument_or_none = (
        ""
        if username
        else (
            "--repository strictdoc_test"
            if test_pypi
            else "--repository strictdoc_release"
        )
    )
    user_password = f"-u{username} -p{password}" if username is not None else ""

    run_invoke(
        context,
        """
            rm -rfv dist/
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.RELEASE,
        """
            python3 -m build
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.RELEASE,
        """
            twine check dist/*
        """,
    )
    # The token is in a core developer's .pypirc file.
    # https://test.pypi.org/manage/account/token/
    # https://packaging.python.org/en/latest/specifications/pypirc/#pypirc
    run_invoke_with_tox(
        context,
        ToxEnvironment.RELEASE,
        f"""
            twine upload dist/strictdoc-*.tar.gz
                {repository_argument_or_none}
                {user_password}
        """,
    )


@task
def release_pyinstaller(context):
    path_to_pyi_dist = "/tmp/strictdoc"

    # The --hidden-import strictdoc.server.app flag is needed because without
    # it, the following is produced:
    # ERROR: Error loading ASGI app. Could not import
    # module "strictdoc.server.app".
    # Solution found here: https://stackoverflow.com/a/71340437/598057
    # This behavior is not surprising because that's how the uvicorn loads the
    # application separately from the parent process.
    command = f"""
        pyinstaller
            --clean
            --name strictdoc
            --noconfirm
            --additional-hooks-dir developer/pyinstaller_hooks
            --distpath {path_to_pyi_dist}
            --hidden-import strictdoc.server.app
            --add-data strictdoc/export/html/templates:templates/html
            --add-data strictdoc/export/rst/templates:templates/rst
            --add-data strictdoc/export/html/_static:_static
            --add-data strictdoc/export/html/_static_extra:_static_extra
            strictdoc/cli/main.py
    """

    run_invoke_with_tox(
        context,
        ToxEnvironment.PYINSTALLER,
        """
    pyinstaller --version
    """,
    )

    run_invoke_with_tox(context, ToxEnvironment.PYINSTALLER, command)


@task
def watch(context, sdocs_path="."):
    strictdoc_command = f"""
        python strictdoc/cli/main.py
            export
            {sdocs_path}
            --output-dir output/
            --experimental-enable-file-traceability
    """

    run_invoke_with_tox(
        context,
        ToxEnvironment.DEVELOPMENT,
        f"""
            {strictdoc_command}
        """,
    )

    paths_to_watch = "."
    run_invoke_with_tox(
        context,
        ToxEnvironment.DEVELOPMENT,
        f"""
            watchmedo shell-command
            --patterns="*.py;*.sdoc;*.jinja;*.html;*.css;*.js"
            --recursive
            --ignore-pattern='output/;tests/integration'
            --command='{strictdoc_command}'
            --drop
            {paths_to_watch}
        """,
    )


@task
def run(context, command):
    run_invoke_with_tox(
        context,
        ToxEnvironment.DEVELOPMENT,
        f"""
            {command}
        """,
    )


@task
def nuitka(context):
    run_invoke(
        context,
        f"""
        PYTHONPATH="{os.getcwd()}"
        python -m nuitka
            --static-libpython=no
            --standalone
            --include-module=textx
            --include-module=strictdoc.server.app
            --include-module=docutils
            --include-module=docutils.readers.standalone
            --include-module=docutils.parsers.rst
            --include-data-dir=strictdoc/export/html/templates=templates/html
            --include-data-dir=strictdoc/export/rst/templates=templates/rst
            --include-data-dir=strictdoc/export/html/_static=_static
            --include-data-dir=strictdoc/export/html/_static_extra/mathjax=_static_extra/mathjax
            --include-package-data=docutils
            strictdoc/cli/main.py
        """,
    )


# https://github.com/jrfonseca/gprof2dot
# pip install gprof2dot
@task()
def performance(context):
    command = """
        python -m cProfile -o output/profile.prof
            strictdoc/cli/main.py export . --no-parallelization &&
        gprof2dot -f pstats output/profile.prof | dot -Tpng -o output/output.png
    """
    run_invoke(context, command)


@task(performance)
def performance_snakeviz(context):
    command = """
        snakeviz output/profile.prof
    """
    run_invoke(context, command)


@task()
def autouid(context):
    run_invoke(
        context,
        """
            python strictdoc/cli/main.py
                manage auto-uid
                drafts/requirements
        """,
    )


@task(aliases=["bd"])
def build_docker(
    context,
    image: str = "strictdoc:latest",
    no_cache: bool = False,
    source="pypi",
):
    no_cache_argument = "--no-cache" if no_cache else ""
    run_invoke(
        context,
        f"""
        docker build .
            --build-arg STRICTDOC_SOURCE={source}
            -t {image}
            {no_cache_argument}
        """,
    )


@task(aliases=["rd"])
def run_docker(
    context, image: str = "strictdoc:latest", command: Optional[str] = None
):
    command_argument = (
        f'/bin/bash -c "{command}"' if command is not None else ""
    )

    run_invoke(
        context,
        f"""
        docker run
            --name strictdoc
            --rm
            -it
            -e HOST_UID=$(id -u) -e HOST_GID=$(id -g)
            -v "$(pwd):/data"
            {image}
            {command_argument}
        """,
        pty=True,
    )


@task(aliases=["td"])
def test_docker(context, image: str = "strictdoc:latest"):
    run_invoke(
        context,
        """
        rm -rf output/ && mkdir -p output/ && chmod 777 output/
        """,
    )
    run_docker(
        context,
        image=image,
        command="strictdoc export --formats=html,html2pdf .",
    )

    def check_file_owner(filepath):
        import pwd  # noqa: PLC0415

        file_owner = pwd.getpwuid(os.stat(filepath).st_uid).pw_name
        current_user = os.environ.get("USER", "")
        return file_owner == current_user

    assert check_file_owner(
        "output/html2pdf/pdf/docs/strictdoc_01_user_guide.pdf"
    )


@task(aliases=["q"])
def qualification(context):
    test_all(context, coverage=True, headless=True)
    coverage_combine(context)
