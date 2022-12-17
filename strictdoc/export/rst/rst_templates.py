import os.path
import sys

from jinja2 import Environment, PackageLoader, StrictUndefined, FileSystemLoader


def _get_package_loader():
    if getattr(sys, "frozen", False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        bundle_dir = sys._MEIPASS  # pylint: disable=protected-access
        return FileSystemLoader(os.path.join(bundle_dir, "templates/rst"))
    return PackageLoader("strictdoc", "export/rst/templates")


class RSTTemplates:
    jinja_environment = Environment(
        loader=_get_package_loader(),
        undefined=StrictUndefined,
    )
    # TODO: Check if this line is still needed (might be some older workaround).
    jinja_environment.globals.update(isinstance=isinstance)
    jinja_environment.trim_blocks = False
    jinja_environment.lstrip_blocks = False
    jinja_environment.strip_trailing_newlines = False
