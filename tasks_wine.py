# Invoke is broken on Python 3.11
# https://github.com/pyinvoke/invoke/issues/833#issuecomment-1293148106
import inspect
import os
import platform
import re
from enum import Enum

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
    venv_command = f"""python -m venv {venv_path} &&
            {venv_command_activate}
    """
    if reset_path:
        venv_command += f'&& export PATH="{venv_path}/bin:/usr/bin:/bin"'

    # TODO: Doing VER>NUL & could be eliminated.
    if platform.system() == "Windows":
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
        # FIXME: pip3 uninstall strictdoc -y" is here because I don't know how
        # to make pip install only the dependencies from the pyproject.toml but
        # not the project itself.
        if VENV_DEPS_CHECK_PASSED not in context:
            result = context.run(
                one_line_command(
                    """
                    pip3 install toml &&
                    python check_environment.py &&
                    pip3 uninstall strictdoc -y
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
def setup_development_deps(context):
    run_invoke_cmd(context, COMMAND_SETUP_DEPS)


@task
def release_pyinstaller(context):
    context[VENV_FOLDER] = VenvFolderType.RELEASE_PYINSTALLER
    setup_development_deps(context)

    path_to_pyi_dist = "Z:\\tmp\\strictdoc_windows"

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
        pip install pyinstaller &&
        pyinstaller
            --clean
            --name strictdoc
            --noconfirm
            --additional-hooks-dir developer\\pyinstaller_hooks
            --distpath {path_to_pyi_dist}
            --hidden-import strictdoc.server.app
            --add-data strictdoc\\export\\html\\templates;templates\\html
            --add-data strictdoc\\export\\rst\\templates;templates\\rst
            --add-data strictdoc\\export\\html\\_static;_static
            --add-data strictdoc\\export\\html\\_static_extra;_static_extra
            strictdoc\\cli\\main.py
       """
    run_invoke_cmd(context, command)
