import inspect
import os
import re

import invoke
from invoke import task

# FIXME
if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec


def one_line_command(string):
    return re.sub("\\s+", " ", string).strip()


def run_invoke_cmd(context, cmd) -> invoke.runners.Result:
    return context.run(
        one_line_command(cmd),
        env=None,
        hide=False,
        warn=False,
        pty=False,
        echo=True,
    )


@task()
def clean(context):
    command = """
        rm -rf src/ ;
        rm -rf bindings/python/tree_sitter_strictdoc/_binding.abi3.so ;
        pip uninstall tree_sitter tree_sitter_python -y
    """
    run_invoke_cmd(context, command)


@task()
def generate(context):
    command = """
        tree-sitter generate
    """
    run_invoke_cmd(context, command)


@task()
def install(context):
    command = """
        pip install -e .
    """
    run_invoke_cmd(context, command)


@task()
def test(context, clear=False, focus=None):
    if clear:
        clean(context)

    generate(context)

    if clear:
        install(context)

    focus_argument = f"-k {focus}" if focus else ""
    command = f"""
        PYTHONPATH=bindings/python
        pytest bindings/python/tests
            {focus_argument}
            --capture=no
            --show-capture=all
            --verbose
    """
    run_invoke_cmd(context, command)
