"""
Per-user cache directory for downloads that do not belong to one project,
such as the ChromeDriver used by HTML2PDF.
"""

import os
import sys


def get_user_cache_dir() -> str:
    """
    Return the per-user StrictDoc cache directory (not created here):

    - Windows: %LOCALAPPDATA%/strictdoc/cache
    - macOS: ~/Library/Caches/strictdoc
    - Linux and others: $XDG_CACHE_HOME/strictdoc or ~/.cache/strictdoc
    """
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(
            os.path.expanduser("~"), "AppData", "Local"
        )
        return os.path.join(base, "strictdoc", "cache")
    if sys.platform == "darwin":
        return os.path.join(
            os.path.expanduser("~"), "Library", "Caches", "strictdoc"
        )
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(
        os.path.expanduser("~"), ".cache"
    )
    return os.path.join(base, "strictdoc")
