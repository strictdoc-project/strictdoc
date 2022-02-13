import os
import re

import invoke
from invoke import task


def oneline_command(string):
    return re.sub("\\s+", " ", string).strip()


def run_invoke_cmd(context, cmd) -> invoke.runners.Result:
    return context.run(
        cmd, env=None, hide=False, warn=False, pty=False, echo=True
    )


@task
def clean(context):
    find_command = oneline_command(
        """
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
    )

    find_result = run_invoke_cmd(context, find_command)
    find_result_stdout = find_result.stdout.strip()
    echo_command = oneline_command(
        f"""echo {find_result_stdout} | xargs rm -rfv"""
    )
    run_invoke_cmd(context, echo_command)


@task
def sphinx(context):
    run_invoke_cmd(
        context,
        oneline_command(
            """
            python3 strictdoc/cli/main.py
                export docs
                    --formats=html,rst
                    --output-dir output/sphinx
                    --project-title "StrictDoc"
            """
        ),
    )

    run_invoke_cmd(
        context,
        oneline_command(
            """
            cp -v output/sphinx/rst/strictdoc.rst docs/sphinx/source/ &&
            mkdir -p docs/strictdoc-html/strictdoc-html &&
            cp -rv output/sphinx/html/* docs/strictdoc-html/strictdoc-html
            """
        ),
    )

    run_invoke_cmd(
        context,
        oneline_command(
            """
            cd docs/sphinx &&
                make html latexpdf &&
                open build/latex/strictdoc.pdf
            """
        ),
    )


@task
def test_unit(context):
    run_invoke_cmd(
        context,
        oneline_command(
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
        oneline_command(
            """
        coverage report --sort=cover
        """
        ),
    )


@task(test_unit)
def test_coverage_report(context):
    run_invoke_cmd(
        context,
        oneline_command(
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

    command = oneline_command(
        """
        lit
        --param STRICTDOC_EXEC="{strictdoc_exec}"
        -v
        {debug_opts}
        {focus_or_none}
        {cwd}/tests/integration
        """
    ).format(
        strictdoc_exec=strictdoc_exec,
        cwd=cwd,
        debug_opts=debug_opts,
        focus_or_none=focus_or_none,
    )

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
        oneline_command(
            """
        poetry build
        """
        ),
    )
    run_invoke_cmd(
        context,
        oneline_command(
            """
        tar -xvf dist/*.tar.gz --wildcards --no-anchored '*/setup.py' --strip=1
        """
        ),
    )
    run_invoke_cmd(
        context,
        oneline_command(
            """
        pip install -e .
        """
        ),
    )


@task
def lint_black_diff(context):
    command = oneline_command(
        """
        black . --color 2>&1
        """
    )
    result = run_invoke_cmd(context, command)

    # black always exits with 0, so we handle the output.
    if "reformatted" in result.stdout:
        print("invoke: black found issues")
        result.exited = 1
        raise invoke.exceptions.UnexpectedExit(result)


@task
def lint_pylint(context):
    command = oneline_command(
        """
        pylint
          --rcfile=.pylint.ini
          --disable=c-extension-no-member
          strictdoc/ tasks.py
        """  # pylint: disable=line-too-long
    )
    try:
        run_invoke_cmd(context, command)
    except invoke.exceptions.UnexpectedExit as exc:
        # pylink doesn't show an error message when exit code != 0, so we do.
        print(f"invoke: pylint exited with error code {exc.result.exited}")
        raise exc


@task
def lint_flake8(context):
    command = oneline_command(
        """
        flake8 strictdoc --statistics --max-line-length 80 --show-source
        """
    )
    run_invoke_cmd(context, command)


@task
def lint_mypy(_):
    oneline_command(
        """
        mypy strictdoc/
            --show-error-codes
            --disable-error-code=arg-type
            --disable-error-code=assignment
            --disable-error-code=attr-defined
            --disable-error-code=no-redef
            --disable-error-code=operator
            --disable-error-code=var-annotated
            --disable-error-code=union-attr
            --enable-error-code=misc
        """
    )


@task(
    lint_black_diff,
    lint_pylint,
    lint_flake8,
    lint_mypy,
)
def lint(_):
    pass


@task(test_unit, test_integration)
def test(_):
    pass


@task(lint, test)
def check(_):
    pass


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(context, github_token):
    command = oneline_command(
        f"""
        github_changelog_generator
        --token {github_token}
        --user strictdoc-project
        --project strictdoc
        """
    )
    run_invoke_cmd(context, command)


@task
def dump_grammar(context, output_file):
    command = oneline_command(
        f"""
            python3 strictdoc/cli/main.py dump-grammar {output_file}
        """
    )
    run_invoke_cmd(context, command)
