from strictdoc import __version__
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


def test_01_static_url_has_strictdoc_version():
    link_renderer = LinkRenderer(root_path="", static_path="_static")

    assert (
        link_renderer.render_static_url("base.css")
        == f"_static/base.css?v={__version__}"
    )
    assert (
        link_renderer.render_static_url_with_prefix("turbo.min.js")
        == f"/_static/turbo.min.js?v={__version__}"
    )
