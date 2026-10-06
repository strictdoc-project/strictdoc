"""
BT-SRV-06: server on an Excel-converted project, with a fresh and then a
damaged compiled template cache.

Two imported spreadsheets go into one folder: 01_import_basic_e2e/input.xlsx
(a PARENT_UID column, so its grammar has a Parent relation) and the 50-row
tsrm_questionnaires.xlsx. Each becomes a document with a custom grammar, and
50 nodes make the server precompile its Jinja templates into
output/server/_cache/<version>/jinja/<hash>/. The test serves the index,
both documents, every view they link to (TABLE/TRACE/DEEP-TRACE) and their
assets; then deletes half of the compiled templates, as an interrupted first
run leaves them, and serves everything again. v0.30.1 answered 500 on every
page after that, with ModuleNotFoundError: No module named
'_jinja2_module_templates_...' and TemplateNotFound in the server log.
"""
import re
import urllib.error
import urllib.request

import pytest
from conftest import FEATURES, REPO_ROOT
from test_bundle import Server

QUESTIONNAIRE = (REPO_ROOT / "tests" / "integration" / "examples" / "python_api"
                 / "export_excel_questionnaire" / "expected" / "tsrm_questionnaires.xlsx")


def _get(base, path):
    try:
        with urllib.request.urlopen(base + "/" + path, timeout=120) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, ""


def _serve_and_fetch(sd, proj, work, label):
    s = Server(sd, proj, work)
    # Wait on a static file: with a broken template cache, "/" answers 500.
    s.base_wait = s.base + "/_static/base.css"
    _wait_for(s)
    try:
        status, index = _get(s.base, "")
        assert status == 200, (label, status)
        docs = sorted(set(re.findall(
            r'href="([^"#?]*/(?:input|tsrm_questionnaires)\.html)"', index)))
        assert len(docs) == 2, (label, docs, index[:2000])
        pages = 0
        for doc in docs:
            status, page = _get(s.base, doc)
            assert status == 200 and ("A-2" in page or "CM-020" in page), (label, doc, status)
            stem = doc.rsplit("/", 1)[-1][: -len(".html")]
            views = sorted(set(re.findall(rf"{stem}-[A-Z-]+\.html", page)))
            for view in views:
                status, _ = _get(s.base, doc.rsplit("/", 1)[0] + "/" + view)
                assert status == 200, (label, view, status)
            for asset in sorted(set(re.findall(r'_static/[^"?#]+', page))):
                status, _ = _get(s.base, asset)
                assert status == 200, (label, asset, status)
            pages += 1 + len(views)
    finally:
        log = s.stop()
    for marker in ("Traceback", "ModuleNotFoundError", "TemplateNotFound"):
        assert marker not in log, (label, log[-4000:])
    return log, pages


def _wait_for(s, timeout=180):
    import time
    t0 = time.time()
    while time.time() - t0 < timeout:
        if s.proc.poll() is not None:
            raise AssertionError("server exited:\n" + s.log.read_text()[-4000:])
        try:
            urllib.request.urlopen(s.base_wait, timeout=5)
            return
        except Exception:
            time.sleep(1)
    raise AssertionError("server did not come up:\n" + s.log.read_text()[-4000:])


@pytest.mark.smoke
def test_srv_06_excel_project_fresh_and_damaged_template_cache(sd, work):
    proj = work / "excel-project"
    sd.run("convert", FEATURES / "excel" / "import" / "01_import_basic_e2e" / "input.xlsx",
           proj, "--input-format=excel")
    sd.run("convert", QUESTIONNAIRE, proj, "--input-format=excel")
    for name in ("input", "tsrm_questionnaires"):
        assert "[GRAMMAR]" in (proj / f"{name}.sdoc").read_text(encoding="utf-8")

    log, pages = _serve_and_fetch(sd, proj, work, "fresh template cache")
    assert "Compile Jinja templates" in log, "the project is too small to precompile templates"
    assert pages >= 4, pages

    compiled = sorted((proj / "output" / "server" / "_cache").rglob("tmpl_*.py"))
    assert compiled, "no compiled templates"
    for path in compiled[1::2]:
        path.unlink()
    _serve_and_fetch(sd, proj, work, "damaged template cache")
