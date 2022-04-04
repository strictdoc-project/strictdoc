import os
import platform
import re
from enum import Enum

import invoke
from invoke import task


def get_venv_command(postfix):
    venv_path = os.path.join(os.getcwd(), f".venv-{postfix}")
    venv_command_activate = (
        f". {venv_path}/bin/activate"
        if platform.system() != "Windows"
        else rf"{venv_path}\Scripts\activate"
    )
    venv_command = f"python -m venv {venv_path} && {venv_command_activate}"
    # Cannot make this work on Windows/PowerShell.
    # TODO: Fix this at some point and make the Windows CI to be identical to
    # Linux/macOS CI.
    if platform.system() == "Windows":
        venv_command = "true"
    return venv_command


VENV_FOLDER = "VENV_FOLDER"


# To prevent all tasks from building to the same virtual environment.
class VenvFolderType(str, Enum):
    RELEASE_DEFAULT = "default"
    RELEASE_LOCAL = "release-local"
    RELEASE_PYPI = "release-pypi"
    RELEASE_PYPI_TEST = "release-pypi-test"


def run_invoke_cmd(context, cmd) -> invoke.runners.Result:
    def one_line_command(string):
        return re.sub("\\s+", " ", string).strip()

    postfix = (
        context[VENV_FOLDER]
        if VENV_FOLDER in context
        else VenvFolderType.RELEASE_DEFAULT
    )

    with context.prefix(get_venv_command(postfix)):
        return context.run(
            one_line_command(cmd),
            env=None,
            hide=False,
            warn=False,
            pty=False,
            echo=True,
        )


@task
def clean(context):
    find_command = """
        find
            tests
            -type f \\(
                -name '*.script'
            \\)
            -or -type d \\(
                -name '*.dSYM' -or
                -name 'sandbox' -or
                -name 'Output' -or
                -name 'output'
            \\)
            -not -path "**Expected**"
            -not -path "**Input**"
        """
    find_result = run_invoke_cmd(context, find_command)
    find_result_stdout = find_result.stdout.strip()
    echo_command = f"""echo {find_result_stdout} | xargs rm -rfv"""
    run_invoke_cmd(context, echo_command)


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


@task(clean)
def test_integration(context, focus=None, debug=False, external_sdoc=None):
    cwd = os.getcwd()

    strictdoc_exec = f'python \\"{cwd}/strictdoc/cli/main.py\\"'
    if external_sdoc is not None:
        strictdoc_exec = "strictdoc"

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
          strictdoc/ tasks.py
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
        flake8 strictdoc --statistics --max-line-length 80 --show-source
        """
    run_invoke_cmd(context, command)


@task
def lint_mypy(context):
    run_invoke_cmd(
        context,
        """
        mypy strictdoc/
            --show-error-codes
            --disable-error-code=arg-type
            --disable-error-code=assignment
            --disable-error-code=attr-defined
            --disable-error-code=import
            --disable-error-code=no-redef
            --disable-error-code=operator
            --disable-error-code=var-annotated
            --disable-error-code=union-attr
            --enable-error-code=misc
        """,
    )


@task(
    lint_black_diff,
    lint_pylint,
    lint_flake8,
    lint_mypy,
)
def lint(_):
    pass


@task(test_unit_coverage, test_integration)
def test(_):
    pass


@task(lint, test)
def check(_):
    pass


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
        python3 tools/link_health.py docs/strictdoc.sdoc
    """
    run_invoke_cmd(context, command)


@task
def setup_development_deps(context):
    command = """
        pip install --upgrade pip setuptools &&
        pip install -r requirements.txt &&
        pip install -r requirements.development.txt
    """
    run_invoke_cmd(context, command)


@task
def release_local(context):
    context[VENV_FOLDER] = VenvFolderType.RELEASE_LOCAL
    command = """
        rm -rfv dist/ build/ && 
        python -m pip uninstall strictdoc -y &&
        python setup.py check &&
            python setup.py install
    """
    clean(context)
    setup_development_deps(context)
    run_invoke_cmd(context, command)
    test_integration(context, external_sdoc="strictdoc")


@task
def release(context, username=None, password=None):
    user_password = f"-u{username} -p{password}" if username is not None else ""

    context[VENV_FOLDER] = VenvFolderType.RELEASE_PYPI
    command = f"""
        rm -rfv dist/ &&
        python setup.py check &&
            python setup.py sdist --verbose &&
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
        python setup.py check &&
            python setup.py sdist --verbose &&
            twine upload --repository-url https://test.pypi.org/legacy/ dist/strictdoc-*.tar.gz
    """
    run_invoke_cmd(context, command)
