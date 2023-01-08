import os
import re
import uuid
from mimetypes import guess_type
from pathlib import Path
from typing import Optional, List, Union, Dict

from fastapi import Form, APIRouter, UploadFile
from reqif.models.error_handling import ReqIFXMLParsingError
from reqif.parser import ReqIFParser
from reqif.unparser import ReqIFUnparser
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from strictdoc import __version__, STRICTDOC_ROOT_PATH
from strictdoc.backend.reqif.export.sdoc_to_reqif_converter import (
    SDocToReqIFObjectConverter,
)
from strictdoc.backend.reqif.import_.reqif_to_sdoc_converter import (
    ReqIFToSDocConverter,
)
from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.free_text import FreeTextContainer, FreeText
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import (
    ServerCommandConfig,
    ExportCommandConfig,
)
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.form_objects.document_form_object import (
    ExistingDocumentFreeTextObject,
)
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
)
from strictdoc.export.html.form_objects.section_form_object import (
    SectionFormObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.parallelizer import NullParallelizer
from strictdoc.helpers.string import sanitize_html_form_field
from strictdoc.server.error_object import ErrorObject


class NodeCreationOrder:
    BEFORE = "before"
    CHILD = "child"
    AFTER = "after"

    @staticmethod
    def is_valid(order):
        return order in (
            NodeCreationOrder.BEFORE,
            NodeCreationOrder.CHILD,
            NodeCreationOrder.AFTER,
        )


def create_main_router(config: ServerCommandConfig) -> APIRouter:
    env = HTMLTemplates.jinja_environment

    parallelizer = NullParallelizer()

    export_config = ExportCommandConfig(
        strictdoc_root_path=STRICTDOC_ROOT_PATH,
        input_paths=[config.input_path],
        output_dir=config.output_path,
        project_title="PROJECT_TITLE",
        formats=["html"],
        fields=None,
        no_parallelization=False,
        enable_mathjax=False,
        experimental_enable_file_traceability=False,
    )
    export_config.is_running_on_server = True
    export_action = ExportAction(
        config=export_config, parallelizer=parallelizer
    )
    export_action.build_index()
    export_action.export()

    router = APIRouter()

    @router.get("/")
    def get_root():
        return get_incoming_request("index.html")

    @router.get("/ping")
    def get_ping():
        return f"StrictDoc v{__version__}"

    @router.get("/actions/document/new_section", response_class=Response)
    def get_new_section(reference_mid: str, whereto: str):
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        assert (
            isinstance(reference_mid, str) and len(reference_mid) > 0
        ), reference_mid

        section_form_object = SectionFormObject(
            section_mid=uuid.uuid4().hex,
            section_title=None,
            section_statement=None,
        )
        reference_node: Union[
            Document, Section
        ] = export_action.traceability_index.get_node_by_id(reference_mid)
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        target_node_mid = reference_mid

        if whereto == "child":
            replace_action = "after"
        elif whereto == "before":
            replace_action = "before"
        elif whereto == "after":
            replace_action = "after"
        else:
            raise NotImplementedError

        template = env.get_template(
            "actions/document/create_section/stream_new_section.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            form_object=section_form_object,
            reference_mid=reference_mid,
            target_node_mid=target_node_mid,
            document_type=DocumentType.document(),
            is_new_section=True,
            replace_action=replace_action,
            whereto=whereto,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/actions/document/create_section", response_class=Response)
    def create_section(
        section_mid: str = Form(None),
        section_title: Optional[str] = Form(None),
        section_content: Optional[str] = Form(None),
        reference_mid: str = Form(None),
        whereto: str = Form(None),
    ):
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        assert (
            isinstance(section_mid, str) and len(section_mid) > 0
        ), section_mid
        assert (
            isinstance(reference_mid, str) and len(reference_mid) > 0
        ), reference_mid

        section_title = sanitize_html_form_field(section_title, multiline=False)
        section_content = sanitize_html_form_field(
            section_content, multiline=True
        )

        reference_node: Union[
            Document, Section
        ] = export_action.traceability_index.get_node_by_id(reference_mid)
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        form_object = SectionFormObject(
            section_mid=section_mid,
            section_title=section_title,
            section_statement=section_content,
        )

        if section_title is None or len(section_title) == 0:
            form_object.add_error(
                "section_title", "Section title must not be empty."
            )
        if section_content is not None and len(section_content) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter.write_with_validation(section_content)
            if parsed_html is None:
                form_object.add_error("section_statement", rst_error)

        if form_object.any_errors():
            template = env.get_template(
                "actions/document/create_section/stream_new_section.jinja.html"
            )
            link_renderer = LinkRenderer(export_action.config.output_html_root)
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                context_document=document,
            )
            output = template.render(
                renderer=markup_renderer,
                form_object=form_object,
                reference_mid=reference_mid,
                target_node_mid=form_object.section_mid,
                document_type=DocumentType.document(),
                is_new_section=True,
                replace_action="replace",
                whereto=whereto,
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        if whereto == NodeCreationOrder.CHILD:
            parent = reference_node
            insert_to_idx = len(parent.section_contents)
        elif whereto == NodeCreationOrder.BEFORE:
            assert isinstance(reference_node, (Requirement, Section))
            parent = reference_node.parent
            insert_to_idx = parent.section_contents.index(reference_node)
        elif whereto == NodeCreationOrder.AFTER:
            assert isinstance(reference_node, (Requirement, Section))
            parent = reference_node.parent
            insert_to_idx = parent.section_contents.index(reference_node) + 1
        else:
            raise NotImplementedError

        section = Section(
            parent=parent,
            uid=None,
            level=None,
            title=None,
            free_texts=[],
            section_contents=[],
        )
        section.node_id = section_mid
        section.ng_document_reference = DocumentReference()
        section.ng_document_reference.set_document(document)
        assert parent.ng_level is not None, parent
        section.ng_level = parent.ng_level + 1
        export_action.traceability_index._map_id_to_node[
            section.node_id
        ] = section
        parent.section_contents.insert(insert_to_idx, section)

        # Updating section title.
        if section_title is not None and len(section_title) > 0:
            section.title = section_title

        # Updating section content.
        if section_content is not None and len(section_content) > 0:
            free_text_container: FreeTextContainer = SDFreeTextReader.read(
                section_content
            )
            if len(section.free_texts) > 0:
                free_text: FreeText = section.free_texts[0]
                free_text.parts = free_text_container.parts
            else:
                free_text = FreeText(section, free_text_container.parts)
                section.free_texts.append(free_text)
        else:
            section.free_texts = []

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(section.document)
        document_meta = section.document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        export_action.export()

        # Rendering back the Turbo template.
        template = env.get_template(
            "actions/document/create_section/stream_created_section.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            traceability_index=export_action.traceability_index,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            config=export_action.config,
        )

        toc_template = env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/edit_section/{section_id}", response_class=Response
    )
    def get_edit_section(section_id: str):
        section: Section = export_action.traceability_index.get_node_by_id(
            section_id
        )
        form_object = SectionFormObject.create_from_section(section=section)
        template = env.get_template(
            "actions/document/edit_section/stream_edit_section.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=section.document,
        )
        output = template.render(
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
            is_new_section=False,
            section_mid=section.node_id,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/actions/document/update_section", response_class=Response)
    def put_update_section(
        section_mid: str = Form(None),
        section_title: Optional[str] = Form(None),
        section_content: Optional[str] = Form(None),
    ):
        assert isinstance(section_mid, str)

        section_title = sanitize_html_form_field(section_title, multiline=False)
        section_content = sanitize_html_form_field(
            section_content, multiline=True
        )

        form_object = SectionFormObject(
            section_mid=section_mid,
            section_title=section_title,
            section_statement=section_content,
        )

        if section_title is None or len(section_title) == 0:
            form_object.add_error(
                "section_title", "Section title must not be empty."
            )

        if section_content is not None and len(section_content) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter.write_with_validation(section_content)
            if parsed_html is None:
                form_object.add_error("section_statement", rst_error)

        section: Section = export_action.traceability_index.get_node_by_id(
            section_mid
        )

        if form_object.any_errors():
            template = env.get_template(
                "actions/document/edit_section/stream_edit_section.jinja.html"
            )
            link_renderer = LinkRenderer(export_action.config.output_html_root)
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                context_document=section.document,
            )
            output = template.render(
                renderer=markup_renderer,
                link_renderer=link_renderer,
                form_object=form_object,
                target_node_mid=section.node_id,
                document_type=DocumentType.document(),
                is_new_section=False,
                replace_action="replace",
                reference_mid="NOT_RELEVANT",
                whereto="NOT_RELEVANT",
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Updating section title.
        if section_title is not None and len(section_title) > 0:
            section.title = section_title
        else:
            assert "Should not reach here", section_title

        # Updating section content.
        if section_content is not None and len(section_content) > 0:
            free_text_container: FreeTextContainer = SDFreeTextReader.read(
                section_content
            )
            if len(section.free_texts) > 0:
                free_text: FreeText = section.free_texts[0]
                free_text.parts = free_text_container.parts
            else:
                free_text = FreeText(section, free_text_container.parts)
                section.free_texts.append(free_text)
        else:
            section.free_texts = []

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(section.document)
        document_meta = section.document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        export_action.export()

        # Rendering back the Turbo template.
        template = env.get_template(
            "actions/document/edit_section/stream_updated_section.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=section.parent,
        )
        output = template.render(
            renderer=markup_renderer,
            link_renderer=link_renderer,
            section=section,
            document_type=DocumentType.document(),
            config=export_action.config,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            section.document
        )
        toc_template = env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/cancel_new_section", response_class=Response)
    def cancel_new_section(section_mid: str):
        template = env.get_template(
            "actions/"
            "document/"
            "create_section/"
            "stream_cancel_new_section.jinja.html"
        )
        output = template.render(section_mid=section_mid)
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_edit_section", response_class=Response
    )
    def cancel_edit_section(section_mid: str):
        section: Section = export_action.traceability_index.get_node_by_id(
            section_mid
        )
        template = env.get_template(
            "actions/document/edit_section/stream_updated_section.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=section.parent,
        )
        output = template.render(
            renderer=markup_renderer,
            link_renderer=link_renderer,
            section=section,
            document_type=DocumentType.document(),
            config=export_action.config,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/fragments/document/{document_id}", response_class=Response)
    def get_edit_document_freetext(document_id: str):
        document = export_action.traceability_index.get_node_by_id(document_id)
        form_object = ExistingDocumentFreeTextObject.create_from_document(
            document=document,
        )
        template = env.get_template(
            "actions/"
            "document/"
            "document_freetext/"
            "stream_edit_document_freetext.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
        )
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_edit_freetext", response_class=Response
    )
    def cancel_edit_document_freetext(document_mid: str):
        assert (
            isinstance(document_mid, str) and len(document_mid) > 0
        ), document_mid
        document: Document = export_action.traceability_index.get_node_by_id(
            document_mid
        )
        template = env.get_template(
            "actions/document/document_freetext/"
            "stream_cancel_edit_freetext.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_type=DocumentType.document(),
            config=export_action.config,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/fragments/document/{document_id}", response_class=Response)
    def put_update_document_freetext(
        document_id: str,
        document_freetext: Optional[str] = Form(None),
    ):
        assert isinstance(document_id, str)

        document_freetext = sanitize_html_form_field(
            document_freetext, multiline=True
        )

        form_object = ExistingDocumentFreeTextObject(
            document_mid=document_id, document_free_text=document_freetext
        )
        document: Document = export_action.traceability_index.get_node_by_id(
            document_id
        )

        free_text_container: Optional[FreeTextContainer] = None
        if document_freetext is not None and len(document_freetext) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter.write_with_validation(document_freetext)
            if parsed_html is None:
                form_object.add_error("document_freetext", rst_error)

            free_text_container = SDFreeTextReader.read(document_freetext)

        if form_object.any_errors():
            template = env.get_template(
                "actions/"
                "document/"
                "document_freetext/"
                "stream_edit_document_freetext.jinja.html"
            )
            link_renderer = LinkRenderer(export_action.config.output_html_root)
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                context_document=document,
            )
            output = template.render(
                renderer=markup_renderer,
                form_object=form_object,
                document_type=DocumentType.document(),
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Updating section content.
        if free_text_container is not None:
            if len(document.free_texts) > 0:
                free_text: FreeText = document.free_texts[0]
                free_text.parts = free_text_container.parts
            else:
                free_text = FreeText(document, free_text_container.parts)
                document.free_texts.append(free_text)
        else:
            document.free_texts = []

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        export_action.export()

        # Rendering back the Turbo template.
        template = env.get_template(
            "actions/document/document_freetext/"
            "stream_updated_document_freetext.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_type=DocumentType.document(),
            config=export_action.config,
        )
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_requirement", response_class=Response)
    def get_new_requirement(reference_mid: str, whereto: str):
        assert isinstance(reference_mid, str), reference_mid
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        reference_node = export_action.traceability_index.get_node_by_id(
            reference_mid
        )
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        form_object = RequirementFormObject.create_new(document=document)
        target_node_mid = reference_mid

        if whereto == NodeCreationOrder.CHILD:
            replace_action = "after"
        elif whereto == NodeCreationOrder.BEFORE:
            replace_action = "before"
        elif whereto == NodeCreationOrder.AFTER:
            replace_action = "after"
        else:
            raise NotImplementedError

        template = env.get_template(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_new_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            is_new_requirement=True,
            renderer=markup_renderer,
            form_object=form_object,
            reference_mid=reference_mid,
            target_node_mid=target_node_mid,
            document_type=DocumentType.document(),
            whereto=whereto,
            replace_action=replace_action,
        )

        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/actions/document/create_requirement", response_class=Response
    )
    async def create_requirement(request: Request):
        request_form_data: FormData = await request.form()
        request_dict: Dict[str, str] = dict(request_form_data)
        requirement_mid: str = request_dict["requirement_mid"]
        reference_mid: str = request_dict["reference_mid"]
        whereto: str = request_dict["whereto"]

        reference_node: Union[
            Document, Section
        ] = export_action.traceability_index.get_node_by_id(reference_mid)
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )
        form_object = RequirementFormObject.create_from_request(
            requirement_mid=requirement_mid,
            request_dict=request_dict,
            document=document,
        )
        if whereto == NodeCreationOrder.CHILD:
            parent = reference_node
            insert_to_idx = len(parent.section_contents)
        elif whereto == NodeCreationOrder.BEFORE:
            parent = reference_node.parent
            insert_to_idx = parent.section_contents.index(reference_node)
        elif whereto == NodeCreationOrder.AFTER:
            parent = reference_node.parent
            insert_to_idx = parent.section_contents.index(reference_node) + 1
        else:
            raise NotImplementedError

        form_object.validate()

        if form_object.any_errors():
            template = env.get_template(
                "actions/"
                "document/"
                "create_requirement/"
                "stream_new_requirement.jinja.html"
            )
            link_renderer = LinkRenderer(export_action.config.output_html_root)
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                context_document=document,
            )

            output = template.render(
                is_new_requirement=True,
                renderer=markup_renderer,
                form_object=form_object,
                reference_mid=reference_mid,
                target_node_mid=requirement_mid,
                document_type=DocumentType.document(),
                whereto=whereto,
                replace_action="replace",
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        requirement = SDocObjectFactory.create_requirement(parent=parent)

        for form_field_name, form_field in form_object.fields.items():
            requirement.set_field_value(form_field_name, form_field.field_value)

        requirement.node_id = requirement_mid
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(document)
        requirement.ng_level = parent.ng_level + 1
        export_action.traceability_index._map_id_to_node[
            requirement.node_id
        ] = requirement

        parent.section_contents.insert(insert_to_idx, requirement)

        export_action.traceability_index.mut_add_uid_to_a_requirement(
            requirement=requirement
        )

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        export_action.export()

        # Rendering back the Turbo template.
        template = env.get_template(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_created_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            traceability_index=export_action.traceability_index,
            config=export_action.config,
        )

        toc_template = env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )

        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/edit_requirement/{requirement_id}",
        response_class=Response,
    )
    def get_edit_requirement(requirement_id: str):
        requirement: Requirement = (
            export_action.traceability_index.get_node_by_id(requirement_id)
        )
        form_object = RequirementFormObject.create_from_requirement(
            requirement=requirement
        )
        document = requirement.document
        template = env.get_template(
            "actions/"
            "document/"
            "edit_requirement/"
            "stream_edit_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            is_new_requirement=False,
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/actions/document/update_requirement")
    async def post_update_requirement(request: Request):
        request_form_data: FormData = await request.form()
        request_dict = dict(request_form_data)
        requirement_mid = request_dict["requirement_mid"]
        requirement = export_action.traceability_index.get_node_by_id(
            requirement_mid
        )
        document = requirement.document

        assert (
            isinstance(requirement_mid, str) and len(requirement_mid) > 0
        ), f"{requirement_mid}"

        form_object = RequirementFormObject.create_from_request(
            requirement_mid=requirement_mid,
            request_dict=request_dict,
            document=document,
        )

        form_object.validate()

        if form_object.any_errors():
            template = env.get_template(
                "actions/"
                "document/"
                "edit_requirement/"
                "stream_edit_requirement.jinja.html"
            )
            link_renderer = LinkRenderer(export_action.config.output_html_root)
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                context_document=document,
            )
            output = template.render(
                is_new_requirement=False,
                renderer=markup_renderer,
                requirement=requirement,
                document_type=DocumentType.document(),
                form_object=form_object,
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        existing_uid = requirement.uid
        # FIXME: Leave only one method based on set_field_value().
        for form_field_name, form_field in form_object.fields.items():
            requirement.set_field_value(form_field_name, form_field.field_value)

        export_action.traceability_index.mut_rename_uid_to_a_requirement(
            requirement=requirement, old_uid=existing_uid
        )

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        export_action.export()

        # Rendering back the Turbo template.
        template = env.get_template(
            "actions/"
            "document/"
            "edit_requirement/"
            "stream_update_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            requirement=requirement,
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            traceability_index=export_action.traceability_index,
            config=export_action.config,
        )

        toc_template = env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )

        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_new_requirement", response_class=Response
    )
    def cancel_new_requirement(requirement_mid: str):
        template = env.get_template(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_cancel_new_requirement.jinja.html"
        )
        output = template.render(requirement_mid=requirement_mid)
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_edit_requirement", response_class=Response
    )
    def cancel_edit_requirement(requirement_mid: str):
        assert (
            isinstance(requirement_mid, str) and len(requirement_mid) > 0
        ), f"{requirement_mid}"
        requirement = export_action.traceability_index.get_node_by_id(
            requirement_mid
        )
        document = requirement.document
        template = env.get_template(
            "actions/"
            "document/"
            "edit_requirement/"
            "stream_update_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            requirement=requirement,
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            traceability_index=export_action.traceability_index,
            config=export_action.config,
        )
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.delete(
        "/actions/document/delete_section/{section_mid}",
        response_class=Response,
    )
    def delete_section(section_mid: str):
        section: Section = export_action.traceability_index.get_node_by_id(
            section_mid
        )

        section_parent: Union[Section, Document] = section.parent
        section_parent.section_contents.remove(section)

        section.parent = None

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(section.document)
        document_meta = section.document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        export_action.export()

        # Rendering back the Turbo template.
        template = env.get_template(
            "actions/document/delete_section/stream_delete_section.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=section.document,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            section.document
        )
        output = template.render(
            renderer=markup_renderer,
            document=section.document,
            document_iterator=iterator,
            traceability_index=export_action.traceability_index,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            config=export_action.config,
        )
        toc_template = env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.delete(
        "/actions/document/delete_section/{section_mid}",
        response_class=Response,
    )
    def delete_requirement(requirement_mid: str):
        requirement: Requirement = (
            export_action.traceability_index.get_node_by_id(requirement_mid)
        )

        requirement_parent: Union[Section, Document] = requirement.parent
        requirement_parent.section_contents.remove(requirement)

        requirement.parent = None

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(requirement.document)
        document_meta = requirement.document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        export_action.export()

        # Rendering back the Turbo template.
        template = env.get_template(
            "actions/document/delete_section/stream_delete_section.jinja.html"
        )
        link_renderer = LinkRenderer(export_action.config.output_html_root)
        output = template.render(requirement=requirement)

        toc_template = env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        iterator = export_action.traceability_index.get_document_iterator(
            requirement.document
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    # Generic routes
    @router.get("/actions/document_tree/new_document", response_class=Response)
    def get_new_document():
        template = env.get_template(
            "actions/document_tree/stream_new_document.jinja.html"
        )
        output = template.render(
            error_object=ErrorObject(),
            document_title="",
            document_path="",
        )
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/actions/document_tree/create_document", response_class=Response
    )
    def create_document(
        document_title: str = Form(None),
        document_path: str = Form(None),
    ):
        error_object = ErrorObject()
        if document_title is None or len(document_title) == 0:
            error_object.add_error(
                "document_title", "Document title must not be empty."
            )
        if document_path is None or len(document_path) == 0:
            error_object.add_error(
                "document_path", "Document path must not be empty."
            )

        if error_object.any_errors():
            template = env.get_template(
                "actions/document_tree/stream_new_document.jinja.html"
            )
            output = template.render(
                error_object=error_object,
                document_title=document_title
                if document_title is not None
                else "",
                document_path=document_path
                if document_path is not None
                else "",
            )
            return HTMLResponse(
                content=output,
                status_code=200,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        full_input_path = os.path.abspath(export_action.config.input_paths[0])
        doc_full_path = os.path.join(full_input_path, document_path)
        doc_full_path_dir = os.path.dirname(doc_full_path)

        Path(doc_full_path_dir).mkdir(parents=True, exist_ok=True)
        document = Document(
            title=document_title,
            config=None,
            grammar=DocumentGrammar.create_default(parent=None),
            free_texts=[],
            section_contents=[],
        )
        document.meta = DocumentMeta(
            level=0,
            file_tree_mount_folder=None,
            document_filename_base=None,
            input_doc_full_path=doc_full_path,
            input_doc_dir_rel_path=document_path,
            output_document_dir_full_path=None,
            output_document_dir_rel_path=None,
        )

        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        export_action.build_index()
        export_action.export()

        template = env.get_template(
            "actions/document_tree/stream_create_document.jinja.html"
        )
        document_tree_iterator = DocumentTreeIterator(
            export_action.traceability_index.document_tree
        )

        output = template.render(
            config=export_action.config,
            document_tree=export_action.traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
            static_path="_static",
            traceability_index=export_action.traceability_index,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document_tree/import_reqif_document_form",
        response_class=Response,
    )
    def get_import_reqif_document_form():
        template = env.get_template(
            "actions/document_tree/import_reqif_document/"
            "stream_form_import_reqif_document.jinja.html"
        )
        output = template.render(
            error_object=ErrorObject(),
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/actions/document_tree/import_document_reqif", response_class=Response
    )
    async def import_document_reqif(reqif_file: UploadFile):
        contents = reqif_file.file.read().decode()

        error_object = ErrorObject()
        assert isinstance(contents, str)

        documents: Optional[List[Document]] = None
        try:
            reqif_bundle = ReqIFParser.parse_from_string(contents)
            stage2_parser: ReqIFToSDocConverter = ReqIFToSDocConverter()
            documents: List[Document] = stage2_parser.convert_reqif_bundle(
                reqif_bundle
            )
        except ReqIFXMLParsingError as exception:
            error_object.add_error(
                "reqif_file", "Cannot parse ReqIF file: " + str(exception)
            )
        except Exception as exception:
            error_object.add_error("reqif_file", str(exception))

        if error_object.any_errors():
            template = env.get_template(
                "actions/document_tree/import_reqif_document/"
                "stream_form_import_reqif_document.jinja.html"
            )
            output = template.render(
                error_object=error_object,
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )
        assert documents is not None
        for document in documents:
            document_title = re.sub(r"[^A-Za-z0-9-]", "_", document.title)
            document_path = f"{document_title}.sdoc"

            full_input_path = os.path.abspath(
                export_action.config.input_paths[0]
            )
            doc_full_path = os.path.join(full_input_path, document_path)
            doc_full_path_dir = os.path.dirname(doc_full_path)
            Path(doc_full_path_dir).mkdir(parents=True, exist_ok=True)

            document.meta = DocumentMeta(
                level=0,
                file_tree_mount_folder=None,
                document_filename_base=None,
                input_doc_full_path=doc_full_path,
                input_doc_dir_rel_path=document_path,
                output_document_dir_full_path=None,
                output_document_dir_rel_path=None,
            )

            document_content = SDWriter().write(document)
            document_meta = document.meta
            with open(
                document_meta.input_doc_full_path, "w", encoding="utf8"
            ) as output_file:
                output_file.write(document_content)

        export_action.build_index()
        export_action.export()

        template = env.get_template(
            "actions/document_tree/import_reqif_document/"
            "stream_refresh_with_imported_reqif_document.jinja.html"
        )
        document_tree_iterator = DocumentTreeIterator(
            export_action.traceability_index.document_tree
        )

        output = template.render(
            config=export_action.config,
            document_tree=export_action.traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
            static_path="_static",
            traceability_index=export_action.traceability_index,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/reqif/export_document/{document_mid}", response_class=Response
    )
    def get_reqif_export_document(document_mid: str):
        # TODO: Export single document, not the whole tree.
        # document: Document = (
        #     export_action.traceability_index.get_node_by_id(document_mid)
        # )
        return get_reqif_export_tree()

    @router.get("/reqif/export_tree", response_class=Response)
    def get_reqif_export_tree():
        reqif_bundle = SDocToReqIFObjectConverter.convert_document_tree(
            document_tree=export_action.traceability_index.document_tree
        )
        reqif_content: str = ReqIFUnparser.unparse(reqif_bundle)
        return Response(
            content=reqif_content,
            status_code=200,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": 'attachment; filename="export.reqif"',
            },
        )

    @router.get("/{full_path:path}", response_class=Response)
    def get_incoming_request(full_path: str):
        if full_path.endswith(".html"):
            return get_document(full_path)
        if full_path.endswith(".css") or full_path.endswith(".js"):
            return get_asset(full_path)
        if full_path.endswith(".ico"):
            return get_asset_binary(full_path)

        return HTMLResponse(content="Not Found", status_code=404)

    def get_document(url_to_document: str):
        full_path_to_document = os.path.join(
            config.output_path, "html", url_to_document
        )
        assert os.path.isfile(full_path_to_document), f"{full_path_to_document}"
        with open(full_path_to_document, encoding="utf8") as sample_sdoc:
            content = sample_sdoc.read()
        return HTMLResponse(content=content)

    def get_asset(url_to_asset: str):
        static_path = os.path.join(STRICTDOC_ROOT_PATH, "strictdoc/export/html")
        static_file = os.path.join(static_path, url_to_asset)
        content_type, _ = guess_type(static_file)

        if not os.path.isfile(static_file):
            return Response(
                content=f"File not found: {url_to_asset}",
                status_code=404,
                media_type=content_type,
            )
        with open(static_file, encoding="utf8") as f:
            content = f.read()
        return Response(content, media_type=content_type)

    def get_asset_binary(url_to_asset: str):
        static_path = os.path.join(STRICTDOC_ROOT_PATH, "strictdoc/export/html")

        static_file = os.path.join(static_path, url_to_asset)
        content_type, _ = guess_type(static_file)

        if not os.path.isfile(static_file):
            return Response(
                content=f"File not found: {url_to_asset}",
                status_code=404,
                media_type=content_type,
            )

        with open(static_file, "rb") as f:
            content = f.read()
        return Response(content, media_type=content_type)

    # Websockets solution based on:
    # https://fastapi.tiangolo.com/advanced/websockets/
    class ConnectionManager:
        def __init__(self):
            self.active_connections: List[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            self.active_connections.remove(websocket)

        @staticmethod
        async def send_personal_message(message: str, websocket: WebSocket):
            await websocket.send_text(message)

        async def broadcast(self, message: str):
            for connection in self.active_connections:
                await connection.send_text(message)

    manager = ConnectionManager()

    @router.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: int):
        await manager.connect(websocket)
        try:
            while True:
                _ = await websocket.receive_text()
                # Do nothing for now.
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(
                f"Websocket: Client #{client_id} disconnected"
            )

    return router
