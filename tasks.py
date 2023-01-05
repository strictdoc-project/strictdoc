# Invoke is broken on Python 3.11
# https://github.com/pyinvoke/invoke/issues/833#issuecomment-1293148106
import inspect
import os
import platform
import re
from enum import Enum
from shutil import which

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

import invoke  # pylint: disable=wrong-import-position
from invoke import task  # pylint: disable=wrong-import-position

# A flag that stores which virtual environment is used for executing tasks.
VENV_FOLDER = "VENV_FOLDER"
# A flag that is used to allow checking the readiness of virtual environment
# only once independently of which task or a sequence of tasks is executed.
VENV_DEPS_CHECK_PASSED = "VENV_DEPS_CHECK_PASSED"

COMMAND_SETUP_DEPS = "pip install .[development]"


def one_line_command(string):
    return re.sub("\\s+", " ", string).strip()


def get_venv_command(venv_path: str, reset_path=True):
    venv_command_activate = (
        f". {venv_path}/bin/activate"
        if platform.system() != "Windows"
        else rf"{venv_path}\Scripts\activate"
    )
    venv_command = f"""
        python3 -m venv {venv_path} && 
            {venv_command_activate}
    """
    if reset_path:
        venv_command += f'&& export PATH="{venv_path}/bin:/usr/bin:/bin"'

    # TODO: Doing true & or VER>NUL & could be eliminated.
    if platform.system() == "Windows":
        # 1) SHELL seems to not be available in Windows shell or Powershell.
        # 2) If SHELL is not available, this means we may be running a
        # Windows shell or Powershell but LIT still tries to use bash if it is
        # available. Therefore, here try to check "bash" as well.
        # If LIT cannot find it, it prints:
        # ...LitConfig.py: warning: Unable to find a usable version of bash.
        if os.getenv("SHELL") is not None or which("bash") is not None:
            venv_command = "true"
        else:
            venv_command = "VER>NUL"
    return one_line_command(venv_command)


# To prevent all tasks from building to the same virtual environment.
class VenvFolderType(str, Enum):
    RELEASE_DEFAULT = "default"
    RELEASE_LOCAL = "release-local"
    RELEASE_PYPI = "release-pypi"
    RELEASE_PYPI_TEST = "release-pypi-test"
    RELEASE_PYINSTALLER = "release-pyinstaller"


def run_invoke_cmd(
    context, cmd, warn: bool = False, reset_path: bool = True
) -> invoke.runners.Result:
    postfix = (
        context[VENV_FOLDER]
        if VENV_FOLDER in context
        else VenvFolderType.RELEASE_DEFAULT
    )
    venv_path = os.path.join(os.getcwd(), f".venv-{postfix}")

    with context.prefix(get_venv_command(venv_path, reset_path=reset_path)):
        if VENV_DEPS_CHECK_PASSED not in context:
            result = context.run(
                one_line_command(
                    """
                    pip install toml &&
                    python3 check_environment.py
                    """
                ),
                env=None,
                hide=False,
                warn=True,
                pty=False,
                echo=True,
            )
            if result.exited == 11:
                result = context.run(
                    one_line_command(COMMAND_SETUP_DEPS),
                    env=None,
                    hide=False,
                    warn=False,
                    pty=False,
                    echo=True,
                )
                if result.exited != 0:
                    return result
            elif result.exited != 0:
                raise invoke.exceptions.UnexpectedExit(result)
            context[VENV_DEPS_CHECK_PASSED] = True

        return context.run(
            one_line_command(cmd),
            env=None,
            hide=False,
            warn=warn,
            pty=False,
            echo=True,
        )


@task
def clean(context):
    # https://unix.stackexchange.com/a/689930/77389
    clean_command = """
        rm -rfv output/ docs/sphinx/build/    
    """
    run_invoke_cmd(context, clean_command)


@task
def clean_itest_artifacts(context):
    # https://unix.stackexchange.com/a/689930/77389
    find_command = """
        git clean -dfX tests/integration/    
    """
    # The command sometimes exits with 1 even if the files are deleted.
    # warn=True ensures that the execution continues.
    run_invoke_cmd(context, find_command, warn=True)


@task
def server(context, input_path="developer/sandbox"):
    assert os.path.isdir(input_path), input_path
    run_invoke_cmd(
        context,
        one_line_command(
            f"""
                python strictdoc/cli/main.py server {input_path} --reload
            """
        ),
    )  # --reload


@task
def sphinx(context):
    run_invoke_cmd(
        context,
        (
            """
            python3 strictdoc/cli/main.py
                export docs/
                    --formats=html
                    --output-dir output/sphinx
                    --project-title "StrictDoc"
            """
        ),
    )

    run_invoke_cmd(
        context,
        (
            """
            python3 strictdoc/cli/main.py
                export docs/
                    --formats=rst
                    --output-dir output/sphinx
                    --project-title "StrictDoc"
            """
        ),
    )

    run_invoke_cmd(
        context,
        (
            """
            cp -v output/sphinx/rst/strictdoc*.rst docs/sphinx/source/ &&
            mkdir -p docs/strictdoc-html/strictdoc-html &&
            cp -rv output/sphinx/html/* docs/strictdoc-html/strictdoc-html
            """
        ),
    )

    run_invoke_cmd(
        context,
        (
            """
            cd docs/sphinx &&
                make html latexpdf &&
                open build/latex/strictdoc.pdf
            """
        ),
        reset_path=False,
    )


@task
def test_unit(context, focus=None):
    focus_argument = f"-k {focus}" if focus is not None else ""
    run_invoke_cmd(
        context,
        (
            f"""
                pytest tests/unit/ {focus_argument}
            """
        ),
    )


@task
def test_unit_server(context, focus=None):
    focus_argument = f"-k {focus}" if focus is not None else ""
    run_invoke_cmd(
        context,
        (
            f"""
                pytest tests/unit_server/ {focus_argument}
            """
        ),
    )


@task
def test_end2end(context, focus=None, long_timeouts=False):
    focus_argument = f"-k {focus}" if focus is not None else ""
    timeouts_argument = "STRICTDOC_LONGER_TIMEOUTS=1" if long_timeouts else ""
    run_invoke_cmd(
        context,
        one_line_command(
            f"""
            {timeouts_argument}
            pytest
                --exitfirst
                --capture=no
                {focus_argument}
                tests/end2end
            """
        ),
    )


@task
def test_unit_coverage(context):
    run_invoke_cmd(
        context,
        (
            """
                coverage run
                --rcfile=.coveragerc
                --branch
                --omit=.venv*/*
                -m pytest
                tests/unit/
            """
        ),
    )
    run_invoke_cmd(
        context,
        (
            """
        coverage report --sort=cover
        """
        ),
    )


@task(test_unit_coverage)
def test_coverage_report(context):
    run_invoke_cmd(
        context,
        (
            """
        coverage html
        """
        ),
    )


@task
def test_integration(context, focus=None, debug=False, strictdoc=None):
    clean_itest_artifacts(context)

    cwd = os.getcwd()

    if strictdoc is None:
        strictdoc_exec = f'python3 \\"{cwd}/strictdoc/cli/main.py\\"'
    else:
        strictdoc_exec = strictdoc

    focus_or_none = f"--filter {focus}" if focus else ""
    debug_opts = "-vv --show-all" if debug else ""

    command = f"""
        lit
        --param STRICTDOC_EXEC="{strictdoc_exec}"
        -v
        {debug_opts}
        {focus_or_none}
        {cwd}/tests/integration
        """

    run_invoke_cmd(context, command)


@task
def lint_black_diff(context):
    command = """
        black . --color --line-length 80 2>&1
        """
    result = run_invoke_cmd(context, command)

    # black always exits with 0, so we handle the output.
    if "reformatted" in result.stdout:
        print("invoke: black found issues")
        result.exited = 1
        raise invoke.exceptions.UnexpectedExit(result)


@task
def lint_pylint(context):
    command = """
        pylint
          --rcfile=.pylint.ini
          --disable=c-extension-no-member
          strictdoc/ tests/ tasks.py
        """  # pylint: disable=line-too-long
    try:
        run_invoke_cmd(context, command)
    except invoke.exceptions.UnexpectedExit as exc:
        # pylink doesn't show an error message when exit code != 0, so we do.
        print(f"invoke: pylint exited with error code {exc.result.exited}")
        raise exc


@task
def lint_flake8(context):
    command = """
        flake8 strictdoc/ tests/ --statistics --max-line-length 80 --show-source
        """
    run_invoke_cmd(context, command)


@task
def lint_mypy(context):
    # Need to delete the cache every time because otherwise mypy gets
    # stuck with 0 warnings very often.
    run_invoke_cmd(
        context,
        """
        rm -rfv .mypy_cache/ &&
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
    lint_black_diff(context)
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
    run_invoke_cmd(context, command)


@task
def dump_grammar(context, output_file):
    command = f"""
            python3 strictdoc/cli/main.py dump-grammar {output_file}
        """
    run_invoke_cmd(context, command)


@task
def check_dead_links(context):
    command = """
        python3 tools/link_health.py docs/strictdoc_01_user_guide.sdoc &&
        python3 tools/link_health.py docs/strictdoc_02_faq.sdoc &&
        python3 tools/link_health.py docs/strictdoc_03_development_plan.sdoc &&
        python3 tools/link_health.py docs/strictdoc_04_backlog.sdoc &&
        python3 tools/link_health.py docs/strictdoc_10_contributing.sdoc &&
        python3 tools/link_health.py docs/strictdoc_20_requirements.sdoc &&
        python3 tools/link_health.py docs/strictdoc_21_design.sdoc
    """
    run_invoke_cmd(context, command)


@task
def setup_development_deps(context):
    run_invoke_cmd(context, COMMAND_SETUP_DEPS)


@task
def release_local(context):
    context[VENV_FOLDER] = VenvFolderType.RELEASE_LOCAL
    command = """
        rm -rfv dist/ build/ && 
        pip uninstall strictdoc -y &&
        python3 -m build &&
        twine check dist/* &&
        pip install dist/*.tar.gz
    """
    run_invoke_cmd(context, command)
    test_integration(context, strictdoc="strictdoc")


@task
def release(context, username=None, password=None):
    user_password = f"-u{username} -p{password}" if username is not None else ""

    context[VENV_FOLDER] = VenvFolderType.RELEASE_PYPI
    command = f"""
        rm -rfv dist/ &&
        python3 -m build &&
            twine check dist/* &&
            twine upload dist/strictdoc-*.tar.gz
                {user_password}
    """
    run_invoke_cmd(context, command)


@task
def release_test(context):
    context[VENV_FOLDER] = VenvFolderType.RELEASE_PYPI_TEST
    setup_development_deps(context)

    command = """
        rm -rfv dist/ &&
        python3 -m build &&
            twine check dist/* &&
            twine upload
                --repository-url
                    https://test.pypi.org/legacy/ dist/strictdoc-*.tar.gz
    """
    run_invoke_cmd(context, command)


@task
def release_pyinstaller(context):
    context[VENV_FOLDER] = VenvFolderType.RELEASE_PYINSTALLER
    setup_development_deps(context)

    path_to_pyi_dist = "/tmp/strictdoc"

    # The --additional-hooks-dir is a workaround against the following error
    # that is produced by pybibtex:
    # """
    # pkg_resources.DistributionNotFound: The 'six' distribution was not found
    # and is required by the application.
    # """
    # Solution found here:
    # https://stackoverflow.com/a/64473931/598057
    command = f"""
        pip install pyinstaller &&
        pyinstaller
            --clean
            --name strictdoc
            --noconfirm
            --additional-hooks-dir developer/pyinstaller_hooks
            --distpath {path_to_pyi_dist}
            --add-data strictdoc/export/html/templates:templates/html
            --add-data strictdoc/export/rst/templates:templates/rst
            --add-data strictdoc/export/html/_static:_static
            --add-data strictdoc/export/html/_static_extra:_static_extra
            strictdoc/cli/main.py
    """
    run_invoke_cmd(context, command)


@task
def watch(context, sdocs_path="developer/sandbox"):
    paths_to_watch = "."
    strictdoc_command = f"""
        python strictdoc/cli/main.py
            export
            {sdocs_path}
            --output-dir {sdocs_path}/output
            --experimental-enable-file-traceability
    """
    run_invoke_cmd(
        context,
        f"""
        {strictdoc_command} &&
        watchmedo shell-command
        --patterns="*.py;*.sdoc;*.html;*.css;*.js"
        --recursive
        --ignore-pattern='output/;tests/integration'
        --command='{strictdoc_command}'
        --drop
        {paths_to_watch}
        """,
    )


@task
def run(context, command):
    run_invoke_cmd(
        context,
        f"""
        {command}
        """,
    )
