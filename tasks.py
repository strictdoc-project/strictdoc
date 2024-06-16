# Invoke is broken on Python 3.11
# https://github.com/pyinvoke/invoke/issues/833#issuecomment-1293148106
import inspect
import os
import re
import sys
import tempfile
from enum import Enum
from typing import Optional

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
    warn: bool = False,
) -> invoke.runners.Result:
    def one_line_command(string):
        return re.sub("\\s+", " ", string).strip()

    return context.run(
        one_line_command(cmd),
        env=environment,
        hide=False,
        warn=warn,
        pty=False,
        echo=True,
    )


def run_invoke_with_tox(
    context,
    environment_type: ToxEnvironment,
    command: str,
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
    )


@task
def clean(context):
    # https://unix.stackexchange.com/a/689930/77389
    clean_command = """
        rm -rfv output/ docs/sphinx/build/
    """
    run_invoke(context, clean_command)


@task
def clean_itest_artifacts(context):
    # https://unix.stackexchange.com/a/689930/77389
    find_command = """
        git clean -dfX tests/integration/
    """
    # The command sometimes exits with 1 even if the files are deleted.
    # warn=True ensures that the execution continues.
    run_invoke(context, find_command, warn=True)


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
                server {input_path} {config_argument} --reload
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

    assert os.path.isdir(
        "strictdoc-project.github.io/"
    ), "Expecting the documentation to be cloned."
    assert os.path.isdir(
        "strictdoc-project.github.io/.git/"
    ), "Expecting the documentation to be a valid Git repository."
    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            cp -rv output/strictdoc_website/html/* strictdoc-project.github.io/
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


@task(aliases=["tu"])
def test_unit(context, focus=None):
    focus_argument = f"-k {focus}" if focus is not None else ""
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            pytest tests/unit/ {focus_argument} -o cache_dir=build/pytest_unit
        """,
    )


@task
def test_unit_server(context, focus=None):
    focus_argument = f"-k {focus}" if focus is not None else ""
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            pytest tests/unit_server/ {focus_argument} -o cache_dir=build/pytest_unit_server
        """,
    )


@task(aliases=["te"])
def test_end2end(
    context,
    focus=None,
    exit_first=False,
    parallelize=False,
    long_timeouts=False,
    headless=False,
    shard=None,
):
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

    assert shard is None or re.match(
        r"[1-9][0-9]*/[1-9][0-9]*", shard
    ), f"--shard argument has an incorrect format: {shard}."
    shard_argument = f"--strictdoc-shard={shard}" if shard else ""

    focus_argument = f"-k {focus}" if focus is not None else ""
    exit_first_argument = "--exitfirst" if exit_first else ""
    headless_argument = "--headless" if headless else ""

    test_command = f"""
        pytest
            --failed-first
            --capture=no
            --reuse-session
            {parallelize_argument}
            {shard_argument}
            {focus_argument}
            {exit_first_argument}
            {long_timeouts_argument}
            {headless_argument}
            -o cache_dir=build/pytest_end2end
            tests/end2end
    """

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
    )


@task
def test_unit_coverage(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            coverage run
            --rcfile=.coveragerc
            --branch
            --omit=.venv*/*
            -m pytest
            -o cache_dir=build/pytest_unit_with_coverage
            tests/unit/
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            coverage report --sort=cover
        """,
    )


@task(test_unit_coverage)
def test_coverage_report(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            coverage html
        """,
    )


@task(aliases=["ti"])
def test_integration(
    context,
    focus=None,
    debug=False,
    no_parallelization=False,
    fail_first=False,
    strictdoc=None,
    html2pdf=False,
    environment=ToxEnvironment.CHECK,
):
    clean_itest_artifacts(context)

    cwd = os.getcwd()

    if strictdoc is None:
        strictdoc_exec = f'python3 \\"{cwd}/strictdoc/cli/main.py\\"'
    else:
        strictdoc_exec = strictdoc

    debug_opts = "-vv --show-all" if debug else ""
    focus_or_none = f"--filter {focus}" if focus else ""
    fail_first_argument = "--max-failures 1" if fail_first else ""

    # HTML2PDF tests are running Chrome Driver which does not seem to be
    # parallelizable, or at least not in the way StrictDoc uses it.
    # If HTML2PDF option is provided, do not parallelize and only run the
    # HTML2PDF-specific tests.
    if not html2pdf:
        parallelize_opts = "" if not no_parallelization else "--threads 1"
        html2pdf_param = ""
        test_folder = f"{cwd}/tests/integration"
    else:
        parallelize_opts = "--threads 1"
        html2pdf_param = "--param TEST_HTML2PDF=1"
        test_folder = f"{cwd}/tests/integration/features/html2pdf"

    strictdoc_cache_dir = os.path.join(tempfile.gettempdir(), "strictdoc_cache")

    itest_command = f"""
        lit
        --param STRICTDOC_EXEC="{strictdoc_exec}"
        --param STRICTDOC_CACHE_DIR="{strictdoc_cache_dir}"
        {html2pdf_param}
        -v
        {debug_opts}
        {focus_or_none}
        {fail_first_argument}
        {parallelize_opts}
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
    # FIXME
    if sys.version_info >= (3, 8):
        return

    # These checks do not seem to be useful:
    # - import
    # - misc
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            mypy strictdoc/
                --show-error-codes
                --disable-error-code=import
                --disable-error-code=misc
                --cache-dir=build/mypy
                --strict
                --python-version=3.7
        """,
    )


# # @sdoc[/SDOC-SRS-43]


@task(aliases=["l"])
def lint(context):
    lint_ruff_format(context)
    lint_ruff(context)
    lint_mypy(context)


@task(aliases=["t"])
def test(context):
    test_unit_coverage(context)
    test_unit_server(context)
    test_integration(context)
    test_integration(context, html2pdf=True)


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
            python3 tools/link_health.py docs/strictdoc_02_faq.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_03_development_plan.sdoc
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
            --add-data strictdoc/export/html2pdf/html2pdf.py:.
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
