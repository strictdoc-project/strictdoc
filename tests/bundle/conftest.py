"""
Pytest fixtures for verifying a frozen (PyInstaller) StrictDoc bundle.

Select the executable under test with ONE of:
  STRICTDOC_BUNDLE=/path/to/strictdoc[.exe]     (the bundle, the normal case)
  STRICTDOC_EXEC="python -m strictdoc.cli.main" (baseline: classify failures
                                                 as bundle-specific vs upstream)
"""
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FEATURES = REPO_ROOT / "tests" / "integration" / "features"
IS_WINDOWS = sys.platform == "win32"


def _strictdoc_cmd():
    bundle = os.environ.get("STRICTDOC_BUNDLE")
    if bundle:
        p = Path(bundle).resolve()
        assert p.is_file(), f"STRICTDOC_BUNDLE does not exist: {p}"
        return [str(p)], p
    exec_ = os.environ.get("STRICTDOC_EXEC")
    if exec_:
        return shlex.split(exec_, posix=not IS_WINDOWS), None
    pytest.exit("Set STRICTDOC_BUNDLE (or STRICTDOC_EXEC for a baseline run).", 2)


def clean_env(extra=None):
    """
    Environment for running the bundle like an end user would: no venv,
    no `html2pdf4doc`/`python` console scripts leaking in from PATH.
    """
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("PYTHON", "VIRTUAL_ENV", "UV_", "CONDA"))}
    keep = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        e = Path(entry)
        if (e.parent / "pyvenv.cfg").exists():
            continue  # a venv's bin/Scripts dir
        if shutil.which("html2pdf4doc", path=entry):
            continue
        keep.append(entry)
    env["PATH"] = os.pathsep.join(keep)
    if os.environ.get("STRICTDOC_EXEC"):
        # Baseline (non-frozen) mode needs its interpreter's imports to work.
        env["PYTHONPATH"] = str(REPO_ROOT)
        env["PATH"] = os.environ.get("PATH", "")
    if extra:
        env.update(extra)
    return env


class StrictDoc:
    def __init__(self, cmd, bundle_path):
        self.cmd = cmd
        self.bundle_path = bundle_path
        self.is_bundle = bundle_path is not None

    def run(self, *args, cwd=None, timeout=600, check=True, env_extra=None,
            env=None):
        full = [*self.cmd, *map(str, args)]
        proc = subprocess.run(
            full, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
            env=env if env is not None else clean_env(env_extra),
        )
        out = proc.stdout + proc.stderr
        if check and proc.returncode != 0:
            raise AssertionError(
                f"exit {proc.returncode}: {' '.join(full)}\n--- output (tail) ---\n"
                + out[-6000:]
            )
        return proc.returncode, out

    def popen(self, *args, cwd=None, env_extra=None, log_path=None):
        log = open(log_path, "w") if log_path else subprocess.DEVNULL
        return subprocess.Popen(
            [*self.cmd, *map(str, args)], cwd=cwd, stdout=log,
            stderr=subprocess.STDOUT, env=clean_env(env_extra),
        )


@pytest.fixture(scope="session")
def sd():
    cmd, bundle = _strictdoc_cmd()
    return StrictDoc(cmd, bundle)


@pytest.fixture(scope="session")
def results_dir():
    d = Path(os.environ.get("BUNDLE_TEST_RESULTS",
                            REPO_ROOT / "build" / "bundle_test_results"))
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def work(tmp_path):
    return tmp_path


def copy_fixture(rel, dst):
    src = FEATURES / rel
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "*.itest", "Output", "test_pdf.py"))
    return Path(dst)


def tree_digest(root):
    """Name+size+mtime digest of every file in the bundle directory."""
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if p.is_file():
            st = p.stat()
            h.update(f"{p.relative_to(root)}|{st.st_size}|{st.st_mtime_ns}\n".encode())
    return h.hexdigest()


@pytest.fixture(scope="session", autouse=True)
def bundle_dir_guard(sd, results_dir):
    """BT-BND-01: the bundle directory must not be written to by any test."""
    if not sd.is_bundle:
        yield
        return
    root = sd.bundle_path.parent
    before = tree_digest(root)
    yield
    after = tree_digest(root)
    (results_dir / "bundle_dir_guard.json").write_text(
        json.dumps({"bundle_dir": str(root), "before": before, "after": after,
                    "unchanged": before == after}, indent=2))
    assert before == after, f"bundle directory was modified during tests: {root}"


def have_chrome():
    if os.environ.get("BUNDLE_TEST_SKIP_PDF") == "1":
        return False
    cands = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"]
    if any(shutil.which(c) for c in cands):
        return True
    for p in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]:
        if os.path.exists(p):
            return True
    return False


def free_port():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def pdf_text(path):
    """Text of a PDF via pdftotext (poppler) or pypdf as a fallback."""
    if shutil.which("pdftotext"):
        return subprocess.run(["pdftotext", "-layout", str(path), "-"],
                              capture_output=True, text=True).stdout
    from pypdf import PdfReader
    return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)


def pdf_pages(path):
    from pypdf import PdfReader
    return len(PdfReader(str(path)).pages)


tempfile.tempdir = os.environ.get("BUNDLE_TEST_TMP") or None
