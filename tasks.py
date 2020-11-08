import os
import re

from invoke import task


def formatted_command(string):
    return re.sub('\\s+', ' ', string).strip()


def run_invoke_cmd(c, cmd):
    c.run(cmd,
          env=None,
          hide=False,
          warn=False,
          pty=False,
          echo=True)


@task
def clean(c):
    find_command = formatted_command("""
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
    """)

    find_result = c.run("{}".format(find_command))
    find_result_stdout = find_result.stdout.strip()

    echo_command = formatted_command(
        """echo {find_result} | xargs rm -rfv""".format(find_result=find_result_stdout)
    )

    run_invoke_cmd(c, echo_command)


@task
def sphinx(c):
    run_invoke_cmd(c, formatted_command("""
        python3 strictdoc/cli/main.py export docs --output-dir output/sphinx
    """))

    run_invoke_cmd(c, formatted_command("""
        cp -v output/sphinx/rst/StrictDoc.rst docs/sphinx/source/ &&
        cp -rv output/sphinx/html/* docs/strictdoc-html/strictdoc-html
    """))

    run_invoke_cmd(c, formatted_command("""
        cd docs/sphinx &&
            make html latexpdf &&
            open build/latex/strictdoc.pdf
    """))


@task
def test_unit(c):
    command = formatted_command("""
        pytest --capture=no
    """)

    run_invoke_cmd(c, command)


@task(clean)
def test_integration(c, focus=None, debug=False):
    cwd = os.getcwd()

    strictdoc_exec = 'python \\"{cwd}/strictdoc/cli/main.py\\"'.format(cwd=cwd)

    focus_or_none = '--filter {}'.format(focus) if focus else ''
    debug_opts = '-vv --show-all' if debug else ''

    command = formatted_command("""
        lit
        --param STRICTDOC_EXEC="{strictdoc_exec}"
        -v
        {debug_opts}    
        {focus_or_none}
        {cwd}/tests/integration
    """).format(strictdoc_exec=strictdoc_exec,
                cwd=cwd,
                debug_opts=debug_opts,
                focus_or_none=focus_or_none)

    run_invoke_cmd(c, command)


@task(test_unit, test_integration)
def test(c):
    pass
