import os
import re
from mimetypes import guess_type
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Form, UploadFile
from jinja2 import Environment
from reqif.models.error_handling import ReqIFXMLParsingError
from reqif.parser import ReqIFParser
from reqif.unparser import ReqIFUnparser
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from strictdoc import __version__
from strictdoc.backend.reqif.p01_sdoc.reqif_to_sdoc_converter import (
    P01_ReqIFToSDocConverter,
)
from strictdoc.backend.reqif.p01_sdoc.sdoc_to_reqif_converter import (
    P01_SDocToReqIFObjectConverter,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import (
    ExportCommandConfig,
    ServerCommandConfig,
)
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.analyzers.document_stats import DocumentTreeStats
from strictdoc.core.analyzers.document_uid_analyzer import DocumentUIDAnalyzer
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.transforms.constants import NodeCreationOrder
from strictdoc.core.transforms.create_requirement import (
    CreateRequirementTransform,
)
from strictdoc.core.transforms.delete_section import DeleteSectionCommand
from strictdoc.core.transforms.section import (
    CreateSectionCommand,
    UpdateSectionCommand,
)
from strictdoc.core.transforms.update_document_config import (
    MultipleValidationError,
    UpdateDocumentConfigTransform,
)
from strictdoc.core.transforms.update_grammar import UpdateGrammarCommand
from strictdoc.core.transforms.update_requirement import (
    UpdateRequirementResult,
    UpdateRequirementTransform,
)
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.form_objects.document_config_form_object import (
    DocumentConfigFormObject,
)
from strictdoc.export.html.form_objects.document_grammar_form_object import (
    DocumentGrammarFormObject,
    GrammarFormField,
    GrammarFormRelation,
)
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormField,
    RequirementFormFieldType,
    RequirementFormObject,
    RequirementReferenceFormField,
)
from strictdoc.export.html.form_objects.section_form_object import (
    SectionFormObject,
)
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.file_system import get_etag
from strictdoc.helpers.mid import MID
from strictdoc.helpers.parallelizer import NullParallelizer
from strictdoc.helpers.string import (
    is_safe_alphanumeric_string,
    sanitize_html_form_field,
)
from strictdoc.server.error_object import ErrorObject


def create_main_router(
    server_config: ServerCommandConfig, project_config: ProjectConfig
) -> APIRouter:
    parallelizer = NullParallelizer()

    # FIXME: Remove this unused export config.
    _export_config = ExportCommandConfig(
        input_paths=[server_config.get_full_input_path()],
        output_dir=server_config.output_path,
        config_path=None,
        project_title=project_config.project_title,
        formats=["html"],
        fields=None,
        no_parallelization=False,
        enable_mathjax=False,
        reqif_profile=project_config.reqif_profile,
        experimental_enable_file_traceability=False,
    )
    project_config.integrate_export_config(_export_config)
    project_config.is_running_on_server = True

    export_action = ExportAction(
        project_config=project_config,
        parallelizer=parallelizer,
    )
    export_action.build_index()

    is_small_project = export_action.traceability_index.is_small_project()
    html_templates = HTMLTemplates.create(
        project_config=project_config,
        enable_caching=not is_small_project,
        strictdoc_last_update=export_action.traceability_index.strictdoc_last_update,
    )

    html_generator = HTMLGenerator(project_config, html_templates)
    html_generator.export_assets(
        traceability_index=export_action.traceability_index,
    )

    def env() -> Environment:
        return html_templates.jinja_environment()

    router = APIRouter()

    @router.get("/")
    def get_root(request: Request):
        return get_incoming_request(request, "index.html")

    @router.get("/ping")
    def get_ping():
        return f"StrictDoc v{__version__}"

    @router.get(
        "/actions/deep_trace/show_full_requirement", response_class=Response
    )
    def requirement__show_full(reference_mid: str):
        requirement: Requirement = (
            export_action.traceability_index.get_node_by_mid(MID(reference_mid))
        )
        template = env().get_template(
            "actions/"
            "deep_trace/"
            "show_full_requirement/"
            "stream_show_full_requirement.jinja"
        )
        link_renderer = LinkRenderer(
            root_path=requirement.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=requirement.document,
        )
        output = template.render(
            renderer=markup_renderer,
            requirement=requirement,
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            document=requirement.document,
            document_type=DocumentType.document(),
            project_config=project_config,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_section", response_class=Response)
    def get_new_section(reference_mid: str, whereto: str):
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        assert (
            isinstance(reference_mid, str) and len(reference_mid) > 0
        ), reference_mid

        section_form_object = SectionFormObject.create_new()
        reference_node: Union[
            Document, Section
        ] = export_action.traceability_index.get_node_by_mid(MID(reference_mid))
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

        template = env().get_template(
            "actions/document/create_section/stream_new_section.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
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
        section_uid: str = Form(""),
        section_mid: str = Form(""),
        reference_mid: str = Form(""),
        whereto: str = Form(""),
        section_title: str = Form(""),
        section_content: str = Form(""),
    ):
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        assert isinstance(section_uid, str), section_uid
        assert (
            isinstance(section_mid, str) and len(section_mid) > 0
        ), section_mid
        assert (
            isinstance(reference_mid, str) and len(reference_mid) > 0
        ), reference_mid

        section_uid: str = sanitize_html_form_field(
            section_uid, multiline=False
        )
        section_title: str = sanitize_html_form_field(
            section_title, multiline=False
        )
        section_content: str = sanitize_html_form_field(
            section_content, multiline=True
        )

        reference_node: Union[
            Document, Section
        ] = export_action.traceability_index.get_node_by_mid(MID(reference_mid))
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        form_object = SectionFormObject(
            section_uid=section_uid,
            section_mid=section_mid,
            section_title=section_title,
            section_statement=section_content,
        )

        try:
            create_command = CreateSectionCommand(
                form_object=form_object,
                whereto=whereto,
                reference_mid=reference_mid,
                traceability_index=export_action.traceability_index,
                config=project_config,
            )
            create_command.perform()
        except MultipleValidationError as validation_error:
            for error_key, errors in validation_error.errors.items():
                for error in errors:
                    form_object.add_error(error_key, error)
            template = env().get_template(
                "actions/document/create_section/stream_new_section.jinja.html"
            )
            link_renderer = LinkRenderer(
                root_path=document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
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

        section: Section = create_command.get_created_section()

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(section.document)
        document_meta = section.document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Update the index because other documents might reference this
        # document's sections. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        # Rendering back the Turbo template.
        template = env().get_template(
            "actions/document/create_section/stream_created_section.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
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
            project_config=project_config,
            standalone=False,
        )

        toc_template = env().get_template(
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
        section: Section = export_action.traceability_index.get_node_by_mid(
            MID(section_id)
        )
        form_object = SectionFormObject.create_from_section(section=section)
        template = env().get_template(
            "actions/document/edit_section/stream_edit_section.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        output = template.render(
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
            is_new_section=False,
            section_mid=section.mid,
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
        section_uid: str = Form(""),
        section_mid: str = Form(""),
        section_title: Optional[str] = Form(""),
        section_content: Optional[str] = Form(""),
    ):
        assert isinstance(section_mid, str)

        section_uid = sanitize_html_form_field(section_uid, multiline=False)
        section_title = sanitize_html_form_field(section_title, multiline=False)
        section_content = sanitize_html_form_field(
            section_content, multiline=True
        )
        section: Section = export_action.traceability_index.get_node_by_mid(
            MID(section_mid)
        )

        form_object = SectionFormObject(
            section_uid=section_uid,
            section_mid=section_mid,
            section_title=section_title,
            section_statement=section_content,
        )

        try:
            update_command = UpdateSectionCommand(
                form_object=form_object,
                section=section,
                traceability_index=export_action.traceability_index,
                config=project_config,
            )
            update_command.perform()
        except MultipleValidationError as validation_error:
            for error_key, errors in validation_error.errors.items():
                for error in errors:
                    form_object.add_error(error_key, error)
            template = env().get_template(
                "actions/document/edit_section/stream_edit_section.jinja.html"
            )
            link_renderer = LinkRenderer(
                root_path=section.document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
                context_document=section.document,
            )
            output = template.render(
                renderer=markup_renderer,
                link_renderer=link_renderer,
                form_object=form_object,
                target_node_mid=section.mid,
                document_type=DocumentType.document(),
                is_new_section=False,
                replace_action="replace",
                reference_mid="NOT_RELEVANT",
                whereto="NOT_RELEVANT",
                standalone=False,
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(section.document)
        document_meta = section.document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Update the index because other documents might reference this
        # document's sections. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        # Rendering back the Turbo template.
        template = env().get_template(
            "actions/document/edit_section/stream_updated_section.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        output = template.render(
            renderer=markup_renderer,
            link_renderer=link_renderer,
            section=section,
            document=section.document,
            document_type=DocumentType.document(),
            project_config=project_config,
            standalone=False,
            traceability_index=export_action.traceability_index,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            section.document
        )
        toc_template = env().get_template(
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
        template = env().get_template(
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
        section: Section = export_action.traceability_index.get_node_by_mid(
            MID(section_mid)
        )
        template = env().get_template(
            "actions/document/edit_section/stream_updated_section.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        output = template.render(
            renderer=markup_renderer,
            link_renderer=link_renderer,
            section=section,
            document=section.document,
            document_type=DocumentType.document(),
            project_config=project_config,
            standalone=False,
            traceability_index=export_action.traceability_index,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_requirement", response_class=Response)
    def get_new_requirement(reference_mid: str, whereto: str):
        assert isinstance(reference_mid, str), reference_mid
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        reference_node = export_action.traceability_index.get_node_by_mid(
            MID(reference_mid)
        )
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        document_tree_stats: DocumentTreeStats = (
            DocumentUIDAnalyzer.analyze_document_tree(
                export_action.traceability_index
            )
        )
        next_uid: str = document_tree_stats.get_next_requirement_uid(
            reference_node.get_requirement_prefix()
        )
        form_object = RequirementFormObject.create_new(
            document=document, next_uid=next_uid
        )

        target_node_mid = reference_mid

        if whereto == NodeCreationOrder.CHILD:
            replace_action = "after"
        elif whereto == NodeCreationOrder.BEFORE:
            replace_action = "before"
        elif whereto == NodeCreationOrder.AFTER:
            replace_action = "after"
        else:
            raise NotImplementedError

        template = env().get_template(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_new_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
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
        document_mid: str = request_dict["document_mid"]
        reference_mid: str = request_dict["reference_mid"]
        whereto: str = request_dict["whereto"]

        document: Document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )
        form_object = RequirementFormObject.create_from_request(
            requirement_mid=requirement_mid,
            request_form_data=request_form_data,
            document=document,
            exiting_requirement_uid=None,
        )

        form_object.validate(
            traceability_index=export_action.traceability_index,
            context_document=document,
            config=project_config,
        )

        if form_object.any_errors():
            template = env().get_template(
                "actions/"
                "document/"
                "create_requirement/"
                "stream_new_requirement.jinja.html"
            )
            link_renderer = LinkRenderer(
                root_path=document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
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
                standalone=False,
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        transform = CreateRequirementTransform(
            form_object=form_object,
            whereto=whereto,
            requirement_mid=requirement_mid,
            reference_mid=reference_mid,
            traceability_index=export_action.traceability_index,
        )
        transform.perform()

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
        template = env().get_template(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_created_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
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
            project_config=project_config,
            standalone=False,
        )

        toc_template = env().get_template(
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
            export_action.traceability_index.get_node_by_mid(
                MID(requirement_id)
            )
        )
        form_object: RequirementFormObject = (
            RequirementFormObject.create_from_requirement(
                requirement=requirement
            )
        )
        document = requirement.document
        template = env().get_template(
            "actions/"
            "document/"
            "edit_requirement/"
            "stream_edit_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
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
    async def document__update_requirement(request: Request):
        request_form_data: FormData = await request.form()
        request_dict = dict(request_form_data)
        requirement_mid = request_dict["requirement_mid"]
        requirement: Requirement = (
            export_action.traceability_index.get_node_by_mid(
                MID(requirement_mid)
            )
        )
        document = requirement.document

        assert (
            isinstance(requirement_mid, str) and len(requirement_mid) > 0
        ), f"{requirement_mid}"

        form_object: RequirementFormObject = (
            RequirementFormObject.create_from_request(
                requirement_mid=requirement_mid,
                request_form_data=request_form_data,
                document=document,
                exiting_requirement_uid=requirement.reserved_uid,
            )
        )

        form_object.validate(
            traceability_index=export_action.traceability_index,
            context_document=document,
            config=project_config,
        )

        if form_object.any_errors():
            template = env().get_template(
                "actions/"
                "document/"
                "edit_requirement/"
                "stream_edit_requirement.jinja.html"
            )
            link_renderer = LinkRenderer(
                root_path=document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
                context_document=document,
            )
            output = template.render(
                is_new_requirement=False,
                renderer=markup_renderer,
                requirement=requirement,
                document_type=DocumentType.document(),
                standalone=False,
                form_object=form_object,
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        update_command = UpdateRequirementTransform(
            form_object=form_object,
            requirement=requirement,
            traceability_index=export_action.traceability_index,
        )
        result: UpdateRequirementResult = update_command.perform()

        # Saving new content to .SDoc files.
        document.ng_needs_generation = True
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        # Those with @ng_needs_generation == True will be regenerated.
        export_action.export()

        iterator: DocumentCachingIterator = (
            export_action.traceability_index.get_document_iterator(document)
        )
        link_renderer: LinkRenderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer: MarkupRenderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )

        output = ""
        for requirement in result.this_document_requirements_to_update:
            template = env().get_template(
                "actions/document/edit_requirement/"
                "stream_update_requirement.jinja.html"
            )
            output += template.render(
                requirement=requirement,
                renderer=markup_renderer,
                document=document,
                document_iterator=iterator,
                document_type=DocumentType.document(),
                link_renderer=link_renderer,
                traceability_index=export_action.traceability_index,
                project_config=project_config,
                standalone=False,
            )

        toc_template = env().get_template(
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
        template = env().get_template(
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
        requirement: Requirement = (
            export_action.traceability_index.get_node_by_mid(
                MID(requirement_mid)
            )
        )
        document = requirement.document
        template = env().get_template(
            "actions/"
            "document/"
            "edit_requirement/"
            "stream_update_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
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
            project_config=project_config,
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
    def delete_section(section_mid: str, confirmed: bool = False):
        if not confirmed:
            template = env().get_template(
                "actions/document/delete_section/"
                "stream_confirm_delete_section.jinja"
            )
            output = template.render(section_mid=section_mid)
            return HTMLResponse(
                content=output,
                status_code=200,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )
        section: Section = assert_cast(
            export_action.traceability_index.get_node_by_mid(MID(section_mid)),
            Section,
        )
        try:
            delete_command = DeleteSectionCommand(
                section=section,
                traceability_index=export_action.traceability_index,
            )
            delete_command.perform()
        except MultipleValidationError:
            # FIXME
            output = ""
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

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
        template = env().get_template(
            "actions/document/delete_section/stream_delete_section.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
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
            project_config=project_config,
            standalone=False,
        )
        toc_template = env().get_template(
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
        "/actions/document/delete_requirement/{requirement_mid}",
        response_class=Response,
    )
    def delete_requirement(requirement_mid: str, confirmed: bool = False):
        if not confirmed:
            template = env().get_template(
                "actions/document/delete_requirement/"
                "stream_confirm_delete_requirement.jinja"
            )
            output = template.render(requirement_mid=requirement_mid)
            return HTMLResponse(
                content=output,
                status_code=200,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        requirement: Requirement = (
            export_action.traceability_index.get_node_by_mid(
                MID(requirement_mid)
            )
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
        template = env().get_template(
            "actions/document/delete_requirement/"
            "stream_delete_requirement.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=requirement.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=requirement.document,
        )
        iterator = export_action.traceability_index.get_document_iterator(
            requirement.document
        )
        output = template.render(
            renderer=markup_renderer,
            document=requirement.document,
            document_iterator=iterator,
            traceability_index=export_action.traceability_index,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            project_config=project_config,
            standalone=False,
        )

        toc_template = env().get_template(
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

    @router.post("/actions/document/move_node", response_class=Response)
    async def move_node(request: Request):
        request_form_data: FormData = await request.form()
        request_dict: Dict[str, str] = dict(request_form_data)
        moved_node_mid: str = request_dict["moved_node_mid"]
        target_mid: str = request_dict["target_mid"]
        whereto: str = request_dict["whereto"]

        assert export_action.traceability_index is not None

        moved_node = export_action.traceability_index.get_node_by_mid(
            MID(moved_node_mid)
        )
        target_node = export_action.traceability_index.get_node_by_mid(
            MID(target_mid)
        )
        current_parent_node = moved_node.parent

        # Currently UI allows a child-like drag-and-drop on a requirement node.
        # In that case, we make it add a node **after** the target requirement
        # node (not as its child because that's not possible).
        if whereto == NodeCreationOrder.CHILD and isinstance(
            target_node, Requirement
        ):
            whereto = NodeCreationOrder.AFTER

        if whereto == NodeCreationOrder.CHILD:
            # Disconnect the moved_node from its parent.
            current_parent_node.section_contents.remove(moved_node)
            # Append to the end of child list.
            target_node.section_contents.append(moved_node)
            moved_node.parent = target_node
        elif whereto == NodeCreationOrder.BEFORE:
            # Disconnect the moved_node from its parent.
            current_parent_node.section_contents.remove(moved_node)
            # Append before.
            insert_to_idx = target_node.parent.section_contents.index(
                target_node
            )
            target_node.parent.section_contents.insert(
                insert_to_idx, moved_node
            )
            moved_node.parent = target_node.parent
        elif whereto == NodeCreationOrder.AFTER:
            # Disconnect the moved_node from its parent.
            current_parent_node.section_contents.remove(moved_node)
            # Append after.
            insert_to_idx = target_node.parent.section_contents.index(
                target_node
            )
            target_node.parent.section_contents.insert(
                insert_to_idx + 1, moved_node
            )
            moved_node.parent = target_node.parent
        else:
            raise NotImplementedError

        # Now we have to update all ng_levels for the moved node because they
        # now depend on the level of the new parent node (target node).
        iterator = export_action.traceability_index.get_document_iterator(
            moved_node.document
        )
        moved_node.ng_level = moved_node.parent.ng_level + 1
        for node in iterator.specific_node_with_normal_levels(moved_node):
            node.ng_level = node.parent.ng_level + 1

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(moved_node.document)
        document_meta = moved_node.document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Update the index because other documents might reference this
        # document's sections. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        # Rendering back the Turbo template.
        template = env().get_template(
            "actions/document/move_node/stream_update_document_content.jinja"
        )
        link_renderer = LinkRenderer(
            root_path=moved_node.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=moved_node.document,
        )
        output = template.render(
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document=moved_node.document,
            document_iterator=iterator,
            document_type=DocumentType.document(),
            project_config=project_config,
            traceability_index=export_action.traceability_index,
            standalone=False,
        )
        toc_template = env().get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            last_moved_node_id=moved_node.mid,
        )
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    # Generic routes
    @router.get("/actions/project_index/new_document", response_class=Response)
    def get_new_document():
        template = env().get_template(
            "actions/project_index/stream_new_document.jinja.html"
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
        "/actions/project_index/create_document", response_class=Response
    )
    def document_tree__create_document(
        document_title: str = Form(""),
        document_path: str = Form(""),
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
        else:
            document_path = document_path.strip()
            if not is_safe_alphanumeric_string(document_path):
                error_object.add_error(
                    "document_path",
                    (
                        "Document path must be relative and only contain "
                        "slashes, alphanumeric characters, "
                        "and underscore symbols."
                    ),
                )
            if not document_path.endswith(".sdoc"):
                error_object.add_error(
                    "document_path",
                    (
                        "Document path must end with a file name. "
                        "The file name must have the .sdoc extension."
                    ),
                )

        if error_object.any_errors():
            template = env().get_template(
                "actions/project_index/stream_new_document.jinja.html"
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

        assert isinstance(project_config.export_input_paths, list)
        full_input_path = os.path.abspath(project_config.export_input_paths[0])
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

        template = env().get_template(
            "actions/project_index/stream_create_document.jinja.html"
        )
        document_tree_iterator = DocumentTreeIterator(
            export_action.traceability_index.document_tree
        )

        output = template.render(
            project_config=project_config,
            document_tree=export_action.traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
            traceability_index=export_action.traceability_index,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_comment", response_class=Response)
    def document__add_comment(requirement_mid: str):
        requirement: Requirement = (
            export_action.traceability_index.get_node_by_mid(
                MID(requirement_mid)
            )
        )
        document: Document = requirement.document
        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        template = env().get_template(
            "actions/"
            "document/"
            "add_requirement_comment/"
            "stream_add_requirement_comment.jinja.html"
        )
        output = template.render(
            requirement_mid=requirement_mid,
            form_object=RequirementFormObject(
                requirement_mid=requirement_mid,
                document_mid=document.mid.get_string_value(),
                fields=[],
                reference_fields=[],
                exiting_requirement_uid=None,
                grammar=grammar,
                relation_types=[],
            ),
            field=RequirementFormField(
                field_mid=MID.create().get_string_value(),
                field_name="COMMENT",
                field_type=RequirementFormFieldType.MULTILINE,
                field_unescaped_value="",
                field_escaped_value="",
            ),
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_relation", response_class=Response)
    def document__add_relation(requirement_mid: str, document_mid: str):
        document: Document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )
        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type["REQUIREMENT"]

        grammar_element_relations = element.get_relation_types()

        template = env().get_template(
            "actions/"
            "document/"
            "add_requirement_relation/"
            "stream_add_requirement_relation.jinja.html"
        )
        output = template.render(
            requirement_mid=requirement_mid,
            form_object=RequirementFormObject(
                requirement_mid=requirement_mid,
                document_mid=document_mid,
                fields=[],
                reference_fields=[],
                exiting_requirement_uid=None,
                grammar=grammar,
                relation_types=grammar_element_relations,
            ),
            field=RequirementReferenceFormField(
                field_mid=MID.create().value,
                field_type=RequirementReferenceFormField.FieldType.PARENT,
                field_value="",
                field_role="",
            ),
            relation_types=grammar_element_relations,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/edit_config", response_class=Response)
    def document__edit_config(document_mid: str):
        document: Document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )
        form_object = DocumentConfigFormObject.create_from_document(
            document=document
        )

        template = env().get_template(
            "actions/"
            "document/"
            "edit_document_config/"
            "stream_edit_document_config.jinja.html"
        )
        output = template.render(
            form_object=form_object,
            document=document,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/actions/document/save_config", response_class=Response)
    async def document__save_edit_config(request: Request):
        request_form_data: FormData = await request.form()
        request_dict: Dict[str, str] = dict(request_form_data)
        document_mid: str = request_dict["document_mid"]
        document: Document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )
        form_object: DocumentConfigFormObject = (
            DocumentConfigFormObject.create_from_request(
                document_mid=document_mid,
                request_form_data=request_form_data,
            )
        )
        try:
            update_command = UpdateDocumentConfigTransform(
                form_object=form_object,
                document=document,
                traceability_index=export_action.traceability_index,
                config=project_config,
            )
            update_command.perform()
        except MultipleValidationError as validation_error:
            for error_key, errors in validation_error.errors.items():
                for error in errors:
                    form_object.add_error(error_key, error)
            template = env().get_template(
                "actions/"
                "document/"
                "edit_document_config/"
                "stream_edit_document_config.jinja.html"
            )
            html_output: str = template.render(
                form_object=form_object,
                document=document,
            )
            return HTMLResponse(
                content=html_output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Re-generate the document's SDOC.
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Update the index because other documents might be referenced by this
        # document's free text. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        template = env().get_template(
            "actions/"
            "document/"
            "edit_document_config/"
            "stream_save_document_config.jinja.html"
        )
        html_output = template.render(
            document=document,
            renderer=markup_renderer,
            document_type=DocumentType.document(),
            standalone=False,
            project_config=project_config,
        )
        return HTMLResponse(
            content=html_output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/cancel_edit_config", response_class=Response)
    def document__cancel_edit_config(document_mid: str):
        document: Document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        template = env().get_template(
            "actions/"
            "document/"
            "edit_document_config/"
            "stream_cancel_edit_document_config.jinja.html"
        )
        output = template.render(
            document=document,
            project_config=project_config,
            renderer=markup_renderer,
            document_type=DocumentType.document(),
            standalone=False,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/edit_grammar", response_class=Response)
    def document__edit_grammar(document_mid: str):
        document: Document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )
        form_object = DocumentGrammarFormObject.create_from_document(
            document=document
        )
        template = env().get_template(
            "actions/"
            "document/"
            "edit_document_grammar/"
            "stream_edit_document_grammar.jinja.html"
        )
        output = template.render(
            form_object=form_object,
            document=document,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/actions/document/save_grammar", response_class=Response)
    async def document__save_grammar(request: Request):
        request_form_data: FormData = await request.form()
        request_dict: Dict[str, str] = dict(request_form_data)
        document_mid: str = request_dict["document_mid"]
        document: Document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )
        form_object: DocumentGrammarFormObject = (
            DocumentGrammarFormObject.create_from_request(
                document_mid=document_mid,
                request_form_data=request_form_data,
            )
        )
        if not form_object.validate():
            print(form_object.fields)  # noqa: T201
            template = env().get_template(
                "actions/"
                "document/"
                "edit_document_grammar/"
                "stream_edit_document_grammar.jinja.html"
            )
            output = template.render(
                form_object=form_object, project_config=project_config
            )
            return HTMLResponse(
                content=output,
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Update the document with new grammar.
        update_grammar_action = UpdateGrammarCommand(
            form_object=form_object,
            document=document,
            traceability_index=export_action.traceability_index,
        )
        grammar_changed = update_grammar_action.perform()

        # If the grammar has not changed, do nothing and save the edit form.
        if not grammar_changed:
            link_renderer = LinkRenderer(
                root_path=document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
                context_document=document,
            )
            template = env().get_template(
                "actions/"
                "document/"
                "edit_document_grammar/"
                "stream_save_document_grammar.jinja.html"
            )
            output = template.render(
                document=document,
                renderer=markup_renderer,
                document_type=DocumentType.document(),
            )
            return HTMLResponse(
                content=output,
                status_code=200,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Re-generate the document's SDOC.
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-generate the document.
        html_generator.export_single_document(
            document=document,
            traceability_index=export_action.traceability_index,
        )

        # Re-generate the document tree.
        html_generator.export_project_tree_screen(
            traceability_index=export_action.traceability_index,
        )

        template = env().get_template(
            "actions/"
            "document/"
            "edit_document_grammar/"
            "stream_save_document_grammar.jinja.html"
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        output = template.render(
            document=document,
            renderer=markup_renderer,
            document_type=DocumentType.document(),
        )
        document_iterator = export_action.traceability_index.document_iterators[
            document
        ]
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        template = env().get_template(
            "actions/"
            "document/"
            "_shared/"
            "stream_refresh_document.jinja.html"
        )
        output += template.render(
            document=document,
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document_type=DocumentType.document(),
            document_iterator=document_iterator,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            standalone=False,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/add_grammar_field", response_class=Response)
    def document__add_grammar_field(document_mid: str):
        template = env().get_template(
            "actions/"
            "document/"
            "edit_document_grammar/"
            "stream_add_grammar_field.jinja.html"
        )
        output = template.render(
            form_object=DocumentGrammarFormObject(
                document_mid=document_mid,
                fields=[],  # Not used in this limited partial template.
                relations=[],  # Not used in this limited partial template.
            ),
            field=GrammarFormField(
                field_mid=MID.create().value,
                field_name="",
                field_required=False,
                reserved=False,
            ),
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/add_grammar_relation", response_class=Response
    )
    def document__add_grammar_relation(document_mid: str):
        template = env().get_template(
            "actions/"
            "document/"
            "edit_document_grammar/"
            "stream_add_grammar_relation.jinja.html"
        )
        output = template.render(
            form_object=DocumentGrammarFormObject(
                document_mid=document_mid,
                fields=[],  # Not used in this limited partial template.
                relations=[],  # Not used in this limited partial template.
            ),
            relation=GrammarFormRelation(
                relation_mid=MID.create().value,
                relation_type="Parent",
                relation_role="",
            ),
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/project_index/import_reqif_document_form",
        response_class=Response,
    )
    def get_import_reqif_document_form():
        template = env().get_template(
            "actions/project_index/import_reqif_document/"
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
        "/actions/project_index/import_document_reqif", response_class=Response
    )
    async def import_document_reqif(reqif_file: UploadFile):
        contents = reqif_file.file.read().decode()

        error_object = ErrorObject()
        assert isinstance(contents, str)

        documents: Optional[List[Document]] = None
        try:
            reqif_bundle = ReqIFParser.parse_from_string(contents)
            converter: P01_ReqIFToSDocConverter = P01_ReqIFToSDocConverter()
            documents: List[Document] = converter.convert_reqif_bundle(
                reqif_bundle
            )
        except ReqIFXMLParsingError as exception:
            error_object.add_error(
                "reqif_file", "Cannot parse ReqIF file: " + str(exception)
            )
        except Exception as exception:
            error_object.add_error("reqif_file", str(exception))

        if error_object.any_errors():
            template = env().get_template(
                "actions/project_index/import_reqif_document/"
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
        assert isinstance(project_config.export_input_paths, list)
        for document in documents:
            document_title = re.sub(r"[^A-Za-z0-9-]", "_", document.title)
            document_path = f"{document_title}.sdoc"

            full_input_path = os.path.abspath(
                project_config.export_input_paths[0]
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

        template = env().get_template(
            "actions/project_index/import_reqif_document/"
            "stream_refresh_with_imported_reqif_document.jinja.html"
        )
        document_tree_iterator = DocumentTreeIterator(
            export_action.traceability_index.document_tree
        )

        output = template.render(
            project_config=project_config,
            document_tree=export_action.traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
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
        return get_reqif_export_tree()

    @router.get("/reqif/export_tree", response_class=Response)
    def get_reqif_export_tree():
        reqif_bundle = P01_SDocToReqIFObjectConverter.convert_document_tree(
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
    def get_incoming_request(request: Request, full_path: str):
        # FIXME: This seems to be quite un-sanitized.
        _, file_extension = os.path.splitext(full_path)
        if file_extension == ".html":
            return get_document(request, full_path)
        if file_extension in (
            ".css",
            ".js",
            ".svg",
            ".ico",
            ".png",
            ".gif",
            ".jpg",
            ".jpeg",
        ):
            return get_asset(request, full_path)

        return HTMLResponse(content="Not Found", status_code=404)

    def get_document(request: Request, url_to_document: str):
        full_path_to_document = os.path.join(
            server_config.output_path, "html", url_to_document
        )
        must_generate_document = False

        path_to_file_exists = os.path.isfile(full_path_to_document)
        if not path_to_file_exists:
            must_generate_document = True
        else:
            output_file_mtime = get_file_modification_time(
                full_path_to_document
            )
            if (
                export_action.traceability_index.index_last_updated
                > output_file_mtime
            ):
                must_generate_document = True

        if not must_generate_document:
            if "if-none-match" in request.headers:
                header_etag = request.headers["if-none-match"]
                # FIXME: We have copied the Etag calculation procedure from
                # Starlette's server code. One day this copy may diverge if
                # Starlette decides to implement something else.
                # In that case, the risk is that the 200/304 caching will stop
                # working but such a risk seems acceptable.
                # FIXME: Known issue: Safari does not send If-Modified-Since,
                # so we never reach this branch with Safari. Googling reveals
                # that Safari's behavior is special, and none of the suggested
                # fixes worked and/or seemed portable.
                file_etag = get_etag(full_path_to_document)
                if header_etag == file_etag:
                    return Response(status_code=304)

        else:
            if url_to_document.startswith("_source_files"):
                # FIXME: We could be more specific here and only generate the
                # requested file.
                html_generator.export_source_coverage_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif url_to_document == "index.html":
                html_generator.export_project_tree_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif url_to_document == "requirements_coverage.html":
                html_generator.export_requirements_coverage_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif url_to_document == "source_coverage.html":
                html_generator.export_source_coverage_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif url_to_document == "project_statistics.html":
                html_generator.export_project_statistics(
                    traceability_index=export_action.traceability_index,
                )
            else:
                if url_to_document.endswith("-TABLE.html"):
                    base_document_url = url_to_document.replace("-TABLE", "")
                    document_type_to_generate = DocumentType.TABLE
                elif url_to_document.endswith("-DEEP-TRACE.html"):
                    base_document_url = url_to_document.replace(
                        "-DEEP-TRACE", ""
                    )
                    document_type_to_generate = DocumentType.DEEPTRACE
                elif url_to_document.endswith("-TRACE.html"):
                    base_document_url = url_to_document.replace("-TRACE", "")
                    document_type_to_generate = DocumentType.TRACE
                elif url_to_document.endswith("-PDF.html"):
                    base_document_url = url_to_document.replace("-PDF", "")
                    document_type_to_generate = DocumentType.PDF
                elif url_to_document.endswith(".standalone.html"):
                    base_document_url = url_to_document.replace(
                        ".standalone", ""
                    )
                    document_type_to_generate = DocumentType.DOCUMENT
                else:
                    # Either this is a normal document, or the path is broken.
                    base_document_url = url_to_document
                    document_type_to_generate = DocumentType.DOCUMENT
                document = export_action.traceability_index.document_tree.map_docs_by_rel_paths.get(  # noqa: E501
                    base_document_url
                )
                if document is None:
                    return HTMLResponse(
                        content=f"Not Found: {url_to_document}", status_code=404
                    )
                document.ng_needs_generation = True
                html_generator.export_single_document_with_performance(
                    document=document,
                    traceability_index=export_action.traceability_index,
                    specific_documents=(document_type_to_generate,),
                )
        return FileResponse(
            full_path_to_document,
            media_type="text/html",
            headers={
                # We don't want the documents to be cached on the server without
                # revalidation.
                # The no-cache request directive asks caches to validate the
                # response with the origin server before reuse.
                # no-cache allows clients to request the most up-to-date
                # response even if the cache has a fresh response.
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
                "Cache-Control": "no-cache"
            },
        )

    def get_asset(request: Request, url_to_asset: str):
        project_output_path = project_config.export_output_html_root

        static_file = os.path.join(project_output_path, url_to_asset)
        content_type, _ = guess_type(static_file)

        if not os.path.isfile(static_file):
            return Response(
                content=f"File not found: {url_to_asset}",
                status_code=404,
                media_type=content_type,
            )

        if "if-none-match" in request.headers:
            header_etag = request.headers["if-none-match"]
            # FIXME: We have copied the Etag calculation procedure from
            # Starlette's server code. One day this copy may diverge if
            # Starlette decides to implement something else.
            # In that case, the risk is that the 200/304 caching will stop
            # working but such a risk seems acceptable.
            file_etag = get_etag(static_file)
            if header_etag == file_etag:
                return Response(status_code=304)

        response = FileResponse(static_file, media_type=content_type)
        return response

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
