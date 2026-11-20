"""
@relation(SDOC-SRS-36, scope=file)
"""

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class SourceFileLinkRenderer(LinkRenderer):
    """
    Link renderer for a source file page.

    The page lists the nodes that trace to the file. The shared node field
    templates render their file links with render_source_file_link(). The
    base class builds that link from the depth of the node's document. On a
    source file page, the link must start from the depth of the page itself.
    """

    def render_source_file_link(  # type: ignore[override]
        self, requirement: SDocNode, requirement_source_path: str
    ) -> str:
        assert isinstance(requirement, SDocNode), requirement
        assert isinstance(requirement_source_path, str), requirement_source_path
        return self.render_url(f"_source_files/{requirement_source_path}.html")
