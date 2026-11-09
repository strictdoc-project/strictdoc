import json
from types import SimpleNamespace

from markupsafe import Markup

from strictdoc.export.html.generators.relation_previews import (
    SOURCE_PREVIEW_MAX_LINES,
    collect_source_relation_previews,
    document_url_for_relation_previews,
    render_relation_previews_js,
    source_relation_previews_file_path,
)
from strictdoc.features.source_file_view.view_object import SourceMarkerTuple


def test_document_url_for_relation_previews():
    assert (
        document_url_for_relation_previews(
            "docs/requirements-relation-previews.js"
        )
        == "docs/requirements.html"
    )
    assert document_url_for_relation_previews("docs/requirements.html") is None
    assert document_url_for_relation_previews("_static/app_core.js") is None


def test_render_relation_previews_js_stores_map_under_script_url():
    previews = {
        "REQ-1": Markup("<p>Shall keep &lt;tags&gt; &amp; <b>markup</b>.</p>"),
    }

    js = render_relation_previews_js(previews).decode("utf-8")

    prefix = "window.StrictDoc.relationPreviews[document.currentScript.src] = "
    assert prefix in js
    payload = js.split(prefix, 1)[1].rstrip().rstrip(";")
    assert json.loads(payload) == {
        "REQ-1": "<p>Shall keep &lt;tags&gt; &amp; <b>markup</b>.</p>",
    }


def test_render_relation_previews_js_with_no_previews_is_valid():
    js = render_relation_previews_js({}).decode("utf-8")
    assert js.endswith("= {};\n")


def marker(begin, end):
    return SimpleNamespace(ng_range_line_begin=begin, ng_range_line_end=end)


def test_collect_source_relation_previews():
    lines = [Markup(f"<span>line {number_}</span>") for number_ in range(1, 41)]
    # The generator replaces a line that starts or ends a range with a tuple
    # that keeps the highlighted line.
    lines[0] = SourceMarkerTuple(
        ng_range_line_begin=1,
        ng_range_line_end=2,
        source_line=Markup("<span>line 1</span>"),
        markers=[],
    )
    trace_info = SimpleNamespace(
        markers=[
            marker(1, 2),
            # Starts on the same line as the first range, but is longer.
            marker(1, 3),
            # Longer than the limit.
            marker(10, 40),
            # Outside of the file.
            marker(41, 41),
            marker(None, None),
        ]
    )

    previews = collect_source_relation_previews(lines, trace_info)

    assert previews == {
        "1": [
            "<span>line 1</span>",
            "<span>line 2</span>",
            "<span>line 3</span>",
        ],
        "10": [
            f"<span>line {number_}</span>"
            for number_ in range(10, 10 + SOURCE_PREVIEW_MAX_LINES)
        ],
    }
    assert all(type(line_) is str for line_ in previews["1"])


def test_source_relation_previews_file_path():
    source_file = SimpleNamespace(
        output_file_full_path="/out/html/_source_files/src/file.py.html"
    )
    assert source_relation_previews_file_path(source_file) == (
        "/out/html/_source_files/src/file.py-relation-previews.js"
    )
