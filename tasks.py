# Invoke is broken on Python 3.11
# https://github.com/pyinvoke/invoke/issues/833#issuecomment-1293148106
import inspect
import os
import re
import sys
from enum import Enum
from typing import Optional

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

import invoke  # pylint: disable=wrong-import-position
from invoke import task  # pylint: disable=wrong-import-position

# Specifying encoding because Windows crashes otherwise when running Invoke
# tasks below:
# UnicodeEncodeError: 'charmap' codec can't encode character '\ufffd'
# in position 16: character maps to <undefined>
# People say, it might also be possible to export PYTHONIOENCODING=utf8 but this
# seems to work.
# FIXME: If you are a Windows user and expert, please advise on how to do this
# properly.
sys.stdout = open(  # pylint: disable=consider-using-with
    1, "w", encoding="utf-8", closefd=False, buffering=1
)


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


@task
def server(context, input_path="."):
    assert os.path.isdir(input_path), input_path
    run_invoke_with_tox(
        context,
        ToxEnvironment.DEVELOPMENT,
        f"""
            python strictdoc/cli/main.py server {input_path} --reload
        """,
    )


@task
def docs(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            python3 strictdoc/cli/main.py
                export docs/
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
                export docs/
                    --formats=rst
                    --output-dir output/sphinx
                    --project-title "StrictDoc"
        """,
    )

    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            cp -v output/sphinx/rst/strictdoc*.rst docs/sphinx/source/
        """,
    )

    run_invoke_with_tox(
        context,
        ToxEnvironment.DOCUMENTATION,
        """
            make --directory docs/sphinx html latexpdf
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


@task
def test_unit(context, focus=None):
    focus_argument = f"-k {focus}" if focus is not None else ""
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            pytest tests/unit/ {focus_argument}
        """,
    )


@task
def test_unit_server(context, focus=None):
    focus_argument = f"-k {focus}" if focus is not None else ""
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        f"""
            pytest tests/unit_server/ {focus_argument}
        """,
    )


@task
def test_end2end(
    context,
    focus=None,
    exit_first=False,
    parallelize=False,
    long_timeouts=False,
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

    focus_argument = f"-k {focus}" if focus is not None else ""
    exit_first_argument = "--exitfirst" if exit_first else ""

    test_command = f"""
        pytest
            --failed-first
            --capture=no
            --reuse-session
            {parallelize_argument}
            {focus_argument}
            {exit_first_argument}
            {long_timeouts_argument}
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


@task
def test_integration(
    context,
    focus=None,
    debug=False,
    strictdoc=None,
    environment=ToxEnvironment.CHECK,
):
    clean_itest_artifacts(context)

    cwd = os.getcwd()

    if strictdoc is None:
        strictdoc_exec = f'python3 \\"{cwd}/strictdoc/cli/main.py\\"'
    else:
        strictdoc_exec = strictdoc

    focus_or_none = f"--filter {focus}" if focus else ""
    debug_opts = "-vv --show-all" if debug else ""

    itest_command = f"""
        lit
        --param STRICTDOC_EXEC="{strictdoc_exec}"
        -v
        {debug_opts}
        {focus_or_none}
        {cwd}/tests/integration
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
def lint_pylint(context):
    # TODO: Fix --disable=import-error
    try:
        run_invoke_with_tox(
            context,
            ToxEnvironment.CHECK,
            """
                pylint
                  --rcfile=.pylint.ini
                  --disable=c-extension-no-member
                  --disable=import-error
                  strictdoc/ tests/ tasks.py
            """,
        )
    except invoke.exceptions.UnexpectedExit as exc:
        # pylink doesn't show an error message when exit code != 0, so we do.
        print(  # noqa: T201
            f"invoke: pylint exited with error code {exc.result.exited}"
        )
        raise exc


@task
def lint_flake8(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            flake8
                strictdoc/ tests/
                --statistics
                --max-line-length 80
                --show-source
        """,
    )


@task
def lint_ruff(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            ruff .
        """,
    )


@task
def lint_mypy(context):
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            mypy strictdoc/
                --show-error-codes
                --disable-error-code=arg-type
                --disable-error-code=attr-defined
                --disable-error-code=import
                --disable-error-code=misc
                --disable-error-code=no-any-return
                --disable-error-code=no-redef
                --disable-error-code=no-untyped-call
                --disable-error-code=no-untyped-def
                --disable-error-code=operator
                --disable-error-code=type-arg
                --disable-error-code=var-annotated
                --disable-error-code=union-attr
                --strict
        """,
    )


@task
def lint(context):
    lint_black(context)
    lint_ruff(context)
    lint_pylint(context)
    lint_flake8(context)
    lint_mypy(context)


@task
def test(context):
    test_unit_coverage(context)
    test_unit_server(context)
    test_integration(context)


@task
def check(context):
    lint(context)
    test(context)


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(context, github_token):
    command = f"""
        github_changelog_generator
        --token {github_token}
        --user strictdoc-project
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
            python3 tools/link_health.py docs/strictdoc_04_backlog.sdoc
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
            python3 tools/link_health.py docs/strictdoc_20_requirements.sdoc
        """,
    )
    run_invoke_with_tox(
        context,
        ToxEnvironment.CHECK,
        """
            python3 tools/link_health.py docs/strictdoc_21_design.sdoc
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

    # The --additional-hooks-dir is a workaround against the following error
    # that is produced by pybibtex:
    # """
    # pkg_resources.DistributionNotFound: The 'six' distribution was not found
    # and is required by the application.
    # """
    # Solution found here:
    # https://stackoverflow.com/a/64473931/598057
    #
    # The --hidden-import strictdoc.server.app flag is needed because without
    # it, the following is produced:
    # ERROR: Error loading ASGI app. Could not import
    # module "strictdoc.server.app".
    # Solution found here: https://stackoverflow.com/a/71340437/598057
    # This behavior is not surprising because that's how the uvicorn loads the
    # application separately from the parent process.
    command = f"""
        pip install pyinstaller toml &&
        python developer/pip_install_strictdoc_deps.py &&
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
    run_invoke(context, command)


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
            --include-module=pybtex.database.input.bibtex
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
