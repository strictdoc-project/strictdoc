# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def,union-attr"
import html
from typing import Any, Dict, Optional, Tuple, Union

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.source_tree import SourceFile
from strictdoc.export.html.document_type import DocumentType
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.string import create_safe_title_string


class LinkRenderer:
    def __init__(self, *, root_path, static_path: str):
        assert isinstance(root_path, str)
        assert isinstance(static_path, str), static_path
        assert len(static_path) > 0, static_path

        self.root_path: str = root_path
        self.static_path: str = (
            f"{root_path}/{static_path}"
            if len(root_path) > 0
            else f"{static_path}"
        )
        self.local_anchor_cache: Dict[Any, str] = {}
        self.req_link_cache: Dict[
            Tuple[DocumentType, int],
            Dict[Union[SDocDocument, SDocNode, SDocSection, Anchor], str],
        ] = {}

    def render_url(self, url: str) -> str:
        url = html.escape(url)
        if len(self.root_path) == 0:
            return url
        return self.root_path + "/" + url

    def render_static_url(self, url: str) -> str:
        return self.static_path + "/" + url

    # This rarely used helper adds slashes to the import statements within
    # <script type="module">, for example project_index/index.jinja.
    # Otherwise, scripts are not imported correctly.
    def render_static_url_with_prefix(self, url: str) -> str:
        static_url = "/" + self.static_path + "/" + url
        return static_url

    def render_local_anchor(
        self, node: Union[Anchor, SDocNode, SDocSection, SDocDocument]
    ) -> str:
        if node in self.local_anchor_cache:
            return self.local_anchor_cache[node]
        if isinstance(node, Anchor):
            return f"{self._string_to_link(node.value)}"

        local_anchor: str
        if node.reserved_uid is not None and len(node.reserved_uid) > 0:
            # UID is unique enough.
            local_anchor = self._string_to_link(node.reserved_uid)
        else:
            # If an element as no UID, provide some uniqueness.
            unique_prefix = node.context.title_number_string
            if isinstance(node, (SDocSection, SDocDocument)):
                local_anchor = (
                    f"{unique_prefix}-{self._string_to_link(node.title)}"
                )
            elif isinstance(node, SDocNode):
                if (
                    node.reserved_title is not None
                    and len(node.reserved_title) > 0
                ):
                    local_anchor = (
                        f"{unique_prefix}-"
                        f"{self._string_to_link(node.reserved_title)}"
                    )
                else:
                    # TODO: This is not reliable
                    local_anchor = str(id(node))
            else:
                raise NotImplementedError(node)
        self.local_anchor_cache[node] = local_anchor
        return local_anchor

    def render_node_link(
        self,
        node: Union[SDocDocument, SDocNode, SDocSection, Anchor],
        context_document: Optional[SDocDocument],
        document_type: DocumentType,
        allow_local: bool = True,
    ) -> str:
        """
        Create an HTML URL for a given node.

        allow_local:     used on the DTR screen where we want to ensure that only
                         full paths are used when jumping to the DOC screen.
        """

        assert isinstance(
            node, (SDocDocument, SDocNode, SDocSection, Anchor)
        ), node

        if isinstance(node, SDocDocument):
            context_level_or_none = (
                context_document.meta.level
                if context_document is not None
                else None
            )
            document_link = node.meta.get_html_link(
                document_type,
                context_level_or_none,
            )
            return document_link + "#_TOP"

        assert isinstance(node, (SDocNode, SDocSection, Anchor)), node
        assert isinstance(document_type, DocumentType), type(document_type)
        local_link = self.render_local_anchor(node)
        including_document = node.get_including_document()
        if (
            including_document is not None
            and including_document.is_bundle_document
        ):
            return f"#{local_link}"

        if (
            allow_local
            and context_document is not None
            and node.get_document() == context_document
        ):
            return f"#{local_link}"

        # Now two cases:
        # - Context document exists and we want to take into account this
        # document's depth.
        # - Context document does not exist, such as when we are on a Search
        # screen. In this case, the level is simply zero.
        level: int = (
            context_document.meta.level if context_document is not None else 0
        )  # FIXME 0 or 1?
        link_cache_key = (document_type, level)
        if link_cache_key in self.req_link_cache:
            document_type_cache = self.req_link_cache[link_cache_key]
            if node in document_type_cache:
                return document_type_cache[node]
        else:
            self.req_link_cache[link_cache_key] = {}
        document_link = node.parent_or_including_document.meta.get_html_link(
            document_type,
            level,
        )
        requirement_link = f"{document_link}#{local_link}"
        self.req_link_cache[link_cache_key][node] = requirement_link
        return requirement_link

    def render_node_doxygen_link(
        self,
        node: Union[SDocDocument, SDocNode, SDocSection, Anchor],
    ):
        """
        Create a Doxygen link for a given node.

        allow_local:     used on the DTR screen where we want to ensure that only
                         full paths are used when jumping to the DOC screen.
        """

        assert isinstance(node, (SDocNode, SDocSection, Anchor)), node
        local_link = self.render_local_anchor(node)
        document_link = (
            node.parent_or_including_document.meta.get_html_doc_link()
        )
        requirement_link = f"{document_link}#{local_link}"
        return requirement_link

    def render_requirement_link_from_source_file(self, node, source_file):
        assert isinstance(node, SDocNode)
        assert isinstance(source_file, SourceFile)
        local_link = self.render_local_anchor(node)
        link_cache_key = (DocumentType.DOCUMENT, source_file.level)
        if link_cache_key in self.req_link_cache:
            document_type_cache = self.req_link_cache[link_cache_key]
            if node in document_type_cache:
                return document_type_cache[node]
        else:
            self.req_link_cache[link_cache_key] = {}

        document = assert_cast(node.get_document(), SDocDocument)
        document_link = document.meta.get_html_link(
            DocumentType.DOCUMENT, source_file.level + 1
        )
        requirement_link = f"{document_link}#{local_link}"
        self.req_link_cache[link_cache_key][node] = requirement_link
        return requirement_link

    @staticmethod
    def render_source_file_link(
        requirement: SDocNode, requirement_source_path: str
    ):
        assert isinstance(requirement_source_path, str), requirement_source_path

        assert requirement.ng_document_reference is not None
        document: SDocDocument = assert_cast(
            requirement.ng_document_reference.get_document(), SDocDocument
        )
        path_prefix = document.meta.get_root_path_prefix()
        source_file_link = (
            f"{path_prefix}/_source_files/{requirement_source_path}.html"
        )
        return source_file_link

    @staticmethod
    def render_source_file_link_from_root(requirement_source_path: str):
        assert isinstance(requirement_source_path, str)
        return f"_source_files/{requirement_source_path}.html"

    @staticmethod
    def render_source_file_link_from_root_2(source_file: SourceFile):
        assert isinstance(source_file, SourceFile)
        source_file_link = (
            "_source_files"
            "/"
            f"{source_file.in_doctree_source_file_rel_path_posix}.html"
        )
        return source_file_link

    @staticmethod
    def render_requirement_in_source_file_link(
        requirement: SDocNode,
        source_link: str,
        context_source_file: SourceFile,
    ):
        assert isinstance(source_link, str), source_link

        def get_root_path_prefix(level):
            assert level > 0
            return ("../" * level)[:-1]

        path_prefix = get_root_path_prefix(context_source_file.level + 1)
        source_file_link = (
            f"{path_prefix}"
            f"/_source_files"
            f"/{source_link}.html"
            f"#{requirement.reserved_uid}"
        )
        return source_file_link

    @staticmethod
    def render_requirement_in_source_file_range_link_using_id(
        req_uid: str,  # noqa: ARG004
        source_link: str,
        context_source_file: SourceFile,
        source_range,
    ):
        assert isinstance(source_link, str)
        assert isinstance(context_source_file, SourceFile)
        assert len(source_link) > 0

        def get_root_path_prefix(level):
            assert level > 0
            return ("../" * level)[:-1]

        path_prefix = get_root_path_prefix(context_source_file.level + 1)
        source_file_link = (
            f"{path_prefix}"
            f"/_source_files"
            f"/{source_link}.html"
            f"#{req_uid}"
            f"#{source_range.ng_range_line_begin}"
            f"#{source_range.ng_range_line_end}"
        )
        return source_file_link

    def render_marker_range_link(
        self,
        source_link: str,
        context_source_file: SourceFile,
        source_range,
    ):
        assert isinstance(source_link, str)
        assert isinstance(context_source_file, SourceFile)
        return self.render_requirement_in_source_file_range_link_using_id(
            # No requirement UID provided because the link is formed for a range only.
            "",
            source_link,
            context_source_file,
            source_range,
        )

    def render_requirement_in_source_file_range_link(
        self,
        requirement: SDocNode,
        source_link: str,
        context_source_file: SourceFile,
        source_range,
    ):
        assert isinstance(source_link, str)
        assert isinstance(context_source_file, SourceFile)
        return self.render_requirement_in_source_file_range_link_using_id(
            requirement.reserved_uid,
            source_link,
            context_source_file,
            source_range,
        )

    @staticmethod
    def _string_to_link(string):
        return create_safe_title_string(string)
