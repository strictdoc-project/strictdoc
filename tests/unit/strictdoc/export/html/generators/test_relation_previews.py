import json

from markupsafe import Markup

from strictdoc.export.html.generators.relation_previews import (
    document_url_for_relation_previews,
    render_relation_previews_js,
)


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
