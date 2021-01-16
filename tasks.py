import os
import re

import invoke
from invoke import task


def oneline_command(string):
    return re.sub("\\s+", " ", string).strip()


def run_invoke_cmd(c, cmd):
    return c.run(cmd, env=None, hide=False, warn=False, pty=False, echo=True)


@task
def clean(c):
    find_command = oneline_command(
        """
        find
            .
            -type f \\(
                -name '*.script'
            \\)
            -or -type d \\(
                -name '*.dSYM' -or
                -name 'Sandbox' -or
                -name 'Output' -or
                -name 'output'
            \\)
            -not -path "**Expected**"
            -not -path "**Input**"
        """
    )

    find_result = run_invoke_cmd(c, find_command)
    find_result_stdout = find_result.stdout.strip()
    echo_command = oneline_command(
        """echo {find_result} | xargs rm -rfv""".format(
            find_result=find_result_stdout
        )
    )

    run_invoke_cmd(c, echo_command)


@task
def sphinx(c):
    run_invoke_cmd(
        c,
        oneline_command(
            """
            python3 strictdoc/cli/main.py export docs --formats=html,rst --output-dir output/sphinx
            """
        ),
    )

    run_invoke_cmd(
        c,
        oneline_command(
            """
            cp -v output/sphinx/rst/StrictDoc.rst docs/sphinx/source/ &&
            cp -rv output/sphinx/html/* docs/strictdoc-html/strictdoc-html
            """
        ),
    )

    run_invoke_cmd(
        c,
        oneline_command(
            """
            cd docs/sphinx &&
                make html latexpdf &&
                open build/latex/strictdoc.pdf
            """
        ),
    )


@task
def test_unit(c):
    command = oneline_command(
        """
        pytest --capture=no
        """
    )

    run_invoke_cmd(c, command)


@task(clean)
def test_integration(c, focus=None, debug=False):
    cwd = os.getcwd()

    strictdoc_exec = 'python \\"{cwd}/strictdoc/cli/main.py\\"'.format(cwd=cwd)

    focus_or_none = "--filter {}".format(focus) if focus else ""
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

    run_invoke_cmd(c, command)


@task
def install_local(c):
    command = oneline_command(
        """
        rm -rfv dist &&
        poetry build &&
        tar -xvf dist/*.tar.gz --wildcards --no-anchored '*/setup.py' --strip=1 &&
        pip install -e .
        """
    )
    run_invoke_cmd(c, command)


@task
def lint_black_diff(c):
    # git diff --name-only -- '*.py' | xargs black --diff --color --fast 2>&1
    command = oneline_command(
        """
        black . --diff --color 2>&1
        """
    )
    result = run_invoke_cmd(c, command)

    # black always exits with 0, so we handle the output.
    if "would be reformatted" in result.stdout:
        print("invoke: black found issues")
        result.exited = 1
        raise invoke.exceptions.UnexpectedExit(result)


@task
def lint_pylint(c):
    command = oneline_command(
        """
        poetry run pylint --rcfile=.pylint.ini strictdoc/ tasks.py
        """
    )
    try:
        run_invoke_cmd(c, command)
    except invoke.exceptions.UnexpectedExit as exc:
        # pylink doesn't show an error message when exit code != 0, so we do.
        print(
            "invoke: pylint exited with error code {}".format(exc.result.exited)
        )
        raise exc


@task(lint_pylint, lint_black_diff)
def lint(c):
    pass


@task(lint, test_unit, test_integration)
def test(c):
    pass


# Support generation of Poetry managed setup.py file #761
# https://github.com/python-poetry/poetry/issues/761#issuecomment-689491920
@task
def create_local_setup(c):
    command = oneline_command(
        """
        poetry build &&
        tar -xvf dist/*.tar.gz --wildcards --no-anchored '*/setup.py' --strip=1 &&
        pip install -e .
        """
    )
    run_invoke_cmd(c, command)


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(c, github_token):
    command = oneline_command(
        f"""
        github_changelog_generator
        --token {github_token}
        --user strictdoc-project
        --project strictdoc
        """
    )
    run_invoke_cmd(c, command)
