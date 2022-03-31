import os
import re

import invoke
from invoke import task


def run_invoke_cmd(context, cmd) -> invoke.runners.Result:
    def one_line_command(string):
        return re.sub("\\s+", " ", string).strip()

    one_line_cmd = one_line_command(cmd)
    return context.run(
        one_line_cmd, env=None, hide=False, warn=False, pty=False, echo=True
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
                export docs/strictdoc.sdoc
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
                export docs
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
            cp -v output/sphinx/rst/strictdoc.rst docs/sphinx/source/ &&
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
def test_integration(context, focus=None, debug=False):
    cwd = os.getcwd()

    strictdoc_exec = f'python \\"{cwd}/strictdoc/cli/main.py\\"'

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
def export_pip_requirements(context):
    run_invoke_cmd(
        context,
        "poetry export --dev --without-hashes --format requirements.txt > requirements.txt",
    )


# Support generation of Poetry managed setup.py file #761
# https://github.com/python-poetry/poetry/issues/761#issuecomment-689491920
@task
def install_local(context):
    run_invoke_cmd(
        context,
        (
            """
        poetry build
        """
        ),
    )
    run_invoke_cmd(
        context,
        (
            """
        tar -xvf dist/*.tar.gz --wildcards --no-anchored '*/setup.py' --strip=1
        """
        ),
    )
    run_invoke_cmd(
        context,
        (
            """
        pip install -e .
        """
        ),
    )


@task
def lint_black_diff(context):
    command = """
        black . --color 2>&1
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
def lint_mypy(_):
    pass


#     (
#         context,
#         """
#         mypy strictdoc/
#             --show-error-codes
#             --disable-error-code=arg-type
#             --disable-error-code=assignment
#             --disable-error-code=attr-defined
#             --disable-error-code=no-redef
#             --disable-error-code=operator
#             --disable-error-code=var-annotated
#             --disable-error-code=union-attr
#             --enable-error-code=misc
#         """,
#     )


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
