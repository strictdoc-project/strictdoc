# mypy: disable-error-code="arg-type,attr-defined,no-any-return,no-redef,no-untyped-call,no-untyped-def,union-attr"
import copy
import os
import re
from mimetypes import guess_type
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Form, UploadFile
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
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.document_view import ViewElement
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import (
    ExportCommandConfig,
    ServerCommandConfig,
)
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.analyzers.document_stats import DocumentTreeStats
from strictdoc.core.analyzers.document_uid_analyzer import DocumentUIDAnalyzer
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.query_engine.query_object import Query, QueryObject
from strictdoc.core.query_engine.query_reader import QueryReader
from strictdoc.core.transforms.constants import NodeCreationOrder
from strictdoc.core.transforms.delete_requirement import (
    DeleteRequirementCommand,
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
from strictdoc.core.transforms.update_grammar_element import (
    UpdateGrammarElementCommand,
)
from strictdoc.core.transforms.update_included_document import (
    UpdateIncludedDocumentTransform,
)
from strictdoc.core.transforms.update_requirement import (
    CreateNodeInfo,
    CreateOrUpdateNodeCommand,
    CreateOrUpdateNodeResult,
    UpdateNodeInfo,
)
from strictdoc.core.transforms.validation_error import (
    MultipleValidationErrorAsList,
)
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.form_objects.document_config_form_object import (
    DocumentConfigFormObject,
)
from strictdoc.export.html.form_objects.grammar_element_form_object import (
    GrammarElementFormObject,
)
from strictdoc.export.html.form_objects.grammar_form_object import (
    GrammarFormObject,
)
from strictdoc.export.html.form_objects.included_document_form_object import (
    IncludedDocumentFormObject,
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
from strictdoc.export.html.generators.document_pdf import (
    DocumentHTML2PDFGenerator,
)
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)
from strictdoc.export.html.generators.view_objects.nestor_view_object import (
    NestorViewObject,
)
from strictdoc.export.html.generators.view_objects.project_tree_view_object import (
    ProjectTreeViewObject,
)
from strictdoc.export.html.generators.view_objects.search_screen_view_object import (
    SearchScreenViewObject,
)
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import HTMLTemplates, JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html2pdf.pdf_print_driver import PDFPrintDriver
from strictdoc.export.json.json_generator import JSONGenerator
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.file_system import get_etag
from strictdoc.helpers.mid import MID
from strictdoc.helpers.parallelizer import NullParallelizer
from strictdoc.helpers.path_filter import PathFilter
from strictdoc.helpers.paths import SDocRelativePath
from strictdoc.helpers.string import (
    create_safe_acronym,
    is_safe_alphanumeric_string,
)
from strictdoc.helpers.timing import measure_performance
from strictdoc.server.error_object import ErrorObject

HTTP_STATUS_PRECONDITION_FAILED = 412
HTTP_STATUS_GATEWAY_TIMEOUT = 504


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
        generate_bundle_document=False,
        no_parallelization=False,
        enable_mathjax=False,
        included_documents=True,
        filter_requirements=None,
        filter_sections=None,
        reqif_profile=project_config.reqif_profile,
        reqif_multiline_is_xhtml=False,
        reqif_enable_mid=False,
        view=None,
        chromedriver=None,
        free_text_to_text=False,
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
        project_config=project_config,
        export_output_html_root=project_config.export_output_html_root,
    )

    def env() -> JinjaEnvironment:
        return html_templates.jinja_environment()

    router = APIRouter()

    @router.get("/")
    def get_root(request: Request):
        return get_incoming_request(request, "index.html")

    @router.get("/ping")
    def get_ping():
        return f"StrictDoc v{__version__}"

    @router.get("/actions/show_full_requirement", response_class=Response)
    def requirement__show_full(reference_mid: str):
        requirement: SDocNode = (
            export_action.traceability_index.get_node_by_mid(MID(reference_mid))
        )
        link_renderer = LinkRenderer(
            root_path=requirement.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=requirement.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=requirement.document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=requirement.document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = env().render_template_as_markup(
            "actions/"
            "node/"
            "show_full_node/"
            "stream_show_full_requirement.jinja",
            view_object=view_object,
            requirement=requirement,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/show_full_section", response_class=Response)
    def section__show_full(reference_mid: str):
        section: SDocSection = export_action.traceability_index.get_node_by_mid(
            MID(reference_mid)
        )
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=section.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        current_view: ViewElement = section.document.view.get_current_view(
            project_config.view
        )
        output = env().render_template_as_markup(
            "actions/"
            "node/"
            "show_full_node/"
            "stream_show_full_section.jinja",
            renderer=markup_renderer,
            section=section,
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            document=section.document,
            document_type=DocumentType.document(),
            project_config=project_config,
            current_view=current_view,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_section", response_class=Response)
    def get_new_section(
        reference_mid: str, whereto: str, context_document_mid: str
    ):
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        assert (
            isinstance(reference_mid, str) and len(reference_mid) > 0
        ), reference_mid

        section_form_object = SectionFormObject.create_new(
            context_document_mid=context_document_mid
        )
        reference_node: Union[SDocDocument, SDocSection] = (
            export_action.traceability_index.get_node_by_mid(MID(reference_mid))
        )
        document = (
            reference_node
            if isinstance(reference_node, SDocDocument)
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

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        output = env().render_template_as_markup(
            "actions/document/create_section/stream_new_section.jinja.html",
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
    async def create_section(request: Request):
        request_form_data: FormData = await request.form()
        request_dict: Dict[str, str] = dict(request_form_data)
        section_mid: str = request_dict["section_mid"]
        reference_mid: str = request_dict["reference_mid"]
        context_document_mid: str = request_dict["context_document_mid"]
        whereto: str = request_dict["whereto"]

        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        form_object: SectionFormObject = SectionFormObject.create_from_request(
            section_mid=section_mid,
            request_form_data=request_form_data,
        )
        reference_node: Union[SDocDocument, SDocSection] = (
            export_action.traceability_index.get_node_by_mid(MID(reference_mid))
        )
        document = (
            reference_node
            if isinstance(reference_node, SDocDocument)
            else reference_node.document
        )

        context_document = export_action.traceability_index.get_node_by_mid(
            MID(context_document_mid)
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
            link_renderer = LinkRenderer(
                root_path=context_document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup=document.config.get_markup(),
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
                context_document=context_document,
            )
            output = env().render_template_as_markup(
                "actions/document/create_section/stream_new_section.jinja.html",
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

        section: SDocSection = create_command.get_created_section()

        # Saving new content to .SDoc file.
        SDWriter(project_config).write_to_file(section.document)

        # Update the index because other documents might reference this
        # document's sections. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        link_renderer = LinkRenderer(
            root_path=context_document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=context_document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=context_document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )

        # Rendering back the Turbo template.
        output = env().render_template_as_markup(
            "actions/document/create_section/stream_created_section.jinja.html",
            view_object=view_object,
        )

        output += env().render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=view_object,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/edit_section", response_class=Response)
    def get_edit_section(node_id: str, context_document_mid: str):
        section: SDocSection = export_action.traceability_index.get_node_by_mid(
            MID(node_id)
        )
        form_object = SectionFormObject.create_from_section(
            section=section, context_document_mid=context_document_mid
        )
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=section.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        output = env().render_template_as_markup(
            "actions/document/edit_section/stream_edit_section.jinja.html",
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
            is_new_section=False,
            section_mid=section.reserved_mid,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/actions/document/update_section", response_class=Response)
    async def put_update_section(request: Request):
        request_form_data: FormData = await request.form()
        request_dict = dict(request_form_data)
        section_mid = request_dict["section_mid"]
        context_document_mid = request_dict["context_document_mid"]
        section: SDocSection = export_action.traceability_index.get_node_by_mid(
            MID(section_mid)
        )

        assert (
            isinstance(section_mid, str) and len(section_mid) > 0
        ), f"{section_mid}"

        form_object: SectionFormObject = SectionFormObject.create_from_request(
            section_mid=section_mid,
            request_form_data=request_form_data,
        )
        assert isinstance(section_mid, str)

        try:
            update_command = UpdateSectionCommand(
                form_object=form_object,
                section=section,
                traceability_index=export_action.traceability_index,
            )
            update_command.perform()
        except MultipleValidationError as validation_error:
            for error_key, errors in validation_error.errors.items():
                for error in errors:
                    form_object.add_error(error_key, error)
            link_renderer = LinkRenderer(
                root_path=section.document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup=section.document.config.get_markup(),
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
                context_document=section.document,
            )
            output = env().render_template_as_markup(
                "actions/document/edit_section/stream_edit_section.jinja.html",
                renderer=markup_renderer,
                link_renderer=link_renderer,
                form_object=form_object,
                target_node_mid=section.reserved_mid,
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
        SDWriter(project_config).write_to_file(section.document)

        # Update the index because other documents might reference this
        # document's sections. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        context_document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(
                MID(context_document_mid)
            )
        )

        # Rendering back the Turbo template.
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=section.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=context_document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = env().render_template_as_markup(
            "actions/document/edit_section/stream_updated_section.jinja.html",
            node=section,
            view_object=view_object,
        )
        output += env().render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=view_object,
        )
        return HTMLResponse(
            content=output,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/cancel_new_section", response_class=Response)
    def cancel_new_section(section_mid: str):
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "create_section/"
            "stream_cancel_new_section.jinja.html",
            section_mid=section_mid,
        )
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
        section: SDocSection = export_action.traceability_index.get_node_by_mid(
            MID(section_mid)
        )
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=section.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        view_object: DocumentScreenViewObject = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=section.document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = env().render_template_as_markup(
            "actions/document/edit_section/stream_updated_section.jinja.html",
            view_object=view_object,
            node=section,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_requirement", response_class=Response)
    def get_new_requirement(
        reference_mid: str,
        whereto: str,
        element_type: str,
        context_document_mid: str,
    ):
        assert isinstance(reference_mid, str), reference_mid
        assert isinstance(whereto, str), whereto
        assert isinstance(element_type, str), element_type
        assert isinstance(context_document_mid, str), context_document_mid

        assert NodeCreationOrder.is_valid(whereto), whereto

        context_document = export_action.traceability_index.get_node_by_mid(
            MID(context_document_mid)
        )

        reference_node = export_action.traceability_index.get_node_by_mid(
            MID(reference_mid)
        )

        # Which document becomes the new requirement's parent is based on
        # whether the reference node is a root node of an included document or not.
        document: SDocDocument
        if isinstance(reference_node, SDocDocument):
            if whereto == "child":
                document = reference_node
            else:
                document = context_document
        else:
            document = reference_node.document

        next_uid: Optional[str] = None
        if element_type != "TEXT":
            document_tree_stats: DocumentTreeStats = (
                DocumentUIDAnalyzer.analyze_document_tree(
                    export_action.traceability_index
                )
            )
            next_uid = document_tree_stats.get_next_requirement_uid(
                reference_node.get_requirement_prefix()
            )
        form_object = RequirementFormObject.create_new(
            document=document,
            context_document_mid=context_document_mid,
            next_uid=next_uid,
            element_type=element_type,
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

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_new_requirement.jinja.html",
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

    @router.get("/actions/document/clone_requirement", response_class=Response)
    def get_clone_requirement(reference_mid: str, context_document_mid: str):
        assert isinstance(reference_mid, str), reference_mid

        reference_node = export_action.traceability_index.get_node_by_mid(
            MID(reference_mid)
        )
        reference_requirement: SDocNode = assert_cast(reference_node, SDocNode)
        document = (
            reference_node
            if isinstance(reference_node, SDocDocument)
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
        form_object: RequirementFormObject = (
            RequirementFormObject.clone_from_requirement(
                requirement=reference_requirement,
                context_document_mid=context_document_mid,
                clone_uid=next_uid,
            )
        )

        target_node_mid = reference_mid

        whereto = NodeCreationOrder.AFTER
        replace_action = "after"

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_new_requirement.jinja.html",
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
        context_document_mid: str = request_dict["context_document_mid"]
        reference_mid: str = request_dict["reference_mid"]
        whereto: str = request_dict["whereto"]
        basic_free_text: bool = request_dict["basic_free_text"] == "true"
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        context_document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(
                MID(context_document_mid)
            )
        )

        form_object: RequirementFormObject = (
            RequirementFormObject.create_from_request(
                is_new=True,
                requirement_mid=requirement_mid,
                request_form_data=request_form_data,
                document=document,
                exiting_requirement_uid=None,
                basic_free_text=basic_free_text,
            )
        )
        form_object.validate(
            traceability_index=export_action.traceability_index,
            context_document=document,
            config=project_config,
        )

        if not form_object.any_errors():
            command = CreateOrUpdateNodeCommand(
                form_object=form_object,
                node_info=CreateNodeInfo(
                    whereto=whereto,
                    requirement_mid=requirement_mid,
                    reference_mid=reference_mid,
                ),
                context_document=context_document,
                traceability_index=export_action.traceability_index,
                project_config=project_config,
            )
            command.perform()

        if form_object.any_errors():
            link_renderer = LinkRenderer(
                root_path=document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup=document.config.get_markup(),
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
                context_document=document,
            )
            output = env().render_template_as_markup(
                "actions/"
                "document/"
                "create_requirement/"
                "stream_new_requirement.jinja.html",
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

        # Saving new content to .SDoc files.
        SDWriter(project_config).write_to_file(document)
        if document != context_document:
            SDWriter(project_config).write_to_file(context_document)

        # Exporting the updated document to HTML. Note that this happens after
        # the traceability index last update marker has been updated. This way
        # the generated HTML file is newer than the traceability index.
        html_generator.export_single_document_with_performance(
            document=document,
            traceability_index=export_action.traceability_index,
            specific_documents=(DocumentType.DOCUMENT,),
        )

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )

        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=context_document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )

        output = view_object.render_updated_screen(env())

        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/edit_requirement", response_class=Response)
    def get_edit_requirement(node_id: str, context_document_mid: str):
        requirement: SDocNode = (
            export_action.traceability_index.get_node_by_mid(MID(node_id))
        )
        form_object: RequirementFormObject = (
            RequirementFormObject.create_from_requirement(
                requirement=requirement,
                context_document_mid=context_document_mid,
            )
        )
        document = requirement.document
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "edit_requirement/"
            "stream_edit_requirement.jinja.html",
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

    @router.get(
        "/reset_uid",
        response_class=Response,
    )
    def reset_uid(reference_mid: str):
        document_tree_stats: DocumentTreeStats = (
            DocumentUIDAnalyzer.analyze_document_tree(
                export_action.traceability_index
            )
        )
        reference_node = export_action.traceability_index.get_node_by_mid_weak(
            MID(reference_mid)
        )
        if isinstance(reference_node, SDocNode):
            next_uid: str = document_tree_stats.get_next_requirement_uid(
                reference_node.get_requirement_prefix()
            )
        elif isinstance(reference_node, SDocSection):
            document_acronym = create_safe_acronym(
                reference_node.document.title
            )
            next_uid: str = document_tree_stats.get_auto_section_uid(
                document_acronym, reference_node
            )
        elif reference_node is None:
            raise NotImplementedError(reference_node)
        else:
            raise NotImplementedError

        uid_form_field: RequirementFormField = RequirementFormField(
            field_mid=MID.create(),
            field_name="UID",
            field_type=RequirementFormFieldType.SINGLELINE,
            field_value=next_uid,
        )
        output = env().render_template_as_markup(
            "components/form/row/row_uid_with_reset/stream.jinja",
            next_uid=next_uid,
            reference_mid=reference_mid,
            uid_form_field=uid_form_field,
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
        requirement: SDocNode = (
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
                is_new=False,
                requirement_mid=requirement_mid,
                request_form_data=request_form_data,
                document=document,
                exiting_requirement_uid=requirement.reserved_uid,
                basic_free_text=requirement.basic_free_text,
            )
        )
        context_document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(
                MID(form_object.context_document_mid)
            )
        )

        form_object.validate(
            traceability_index=export_action.traceability_index,
            context_document=document,
            config=project_config,
        )

        update_requirement_command_result_or_none: Optional[
            CreateOrUpdateNodeResult
        ] = None
        if not form_object.any_errors():
            update_command = CreateOrUpdateNodeCommand(
                form_object=form_object,
                node_info=UpdateNodeInfo(node_to_update=requirement),
                context_document=context_document,
                traceability_index=export_action.traceability_index,
                project_config=project_config,
            )

            update_requirement_command_result_or_none = update_command.perform()

        if form_object.any_errors():
            link_renderer = LinkRenderer(
                root_path=document.meta.get_root_path_prefix(),
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                markup=document.config.get_markup(),
                traceability_index=export_action.traceability_index,
                link_renderer=link_renderer,
                html_templates=html_generator.html_templates,
                config=project_config,
                context_document=document,
            )
            output = env().render_template_as_markup(
                "actions/"
                "document/"
                "edit_requirement/"
                "stream_edit_requirement.jinja.html",
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

        update_requirement_command_result: CreateOrUpdateNodeResult = (
            assert_cast(
                update_requirement_command_result_or_none,
                CreateOrUpdateNodeResult,
            )
        )

        # Saving new content to .SDoc files.
        SDWriter(project_config).write_to_file(document)

        # Exporting the updated document to HTML. Note that this happens after
        # the traceability index last update marker has been updated. This way
        # the generated HTML file is newer than the traceability index.
        html_generator.export_single_document_with_performance(
            document=document,
            traceability_index=export_action.traceability_index,
            specific_documents=(DocumentType.DOCUMENT,),
        )

        link_renderer: LinkRenderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer: MarkupRenderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )

        return HTMLResponse(
            content=view_object.render_updated_nodes_and_toc(
                update_requirement_command_result.this_document_requirements_to_update,
                env(),
            ),
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_new_requirement", response_class=Response
    )
    def cancel_new_requirement(requirement_mid: str):
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_cancel_new_requirement.jinja.html",
            requirement_mid=requirement_mid,
        )
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
        requirement: SDocNode = (
            export_action.traceability_index.get_node_by_mid(
                MID(requirement_mid)
            )
        )
        document = requirement.document
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        return HTMLResponse(
            content=view_object.render_updated_nodes_and_toc(
                [requirement], env()
            ),
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.delete(
        "/actions/document/delete_section",
        response_class=Response,
    )
    def delete_section(
        node_id: str, context_document_mid: str, confirmed: bool = False
    ):
        section: SDocSection = assert_cast(
            export_action.traceability_index.get_node_by_mid(MID(node_id)),
            SDocSection,
        )
        assert (
            isinstance(context_document_mid, str)
            and len(context_document_mid) > 0
        ), context_document_mid
        if not confirmed:
            errors: List[str]
            try:
                delete_command = DeleteSectionCommand(
                    section=section,
                    traceability_index=export_action.traceability_index,
                )
                delete_command.validate()
                errors = []
            except MultipleValidationErrorAsList as error_:
                errors = error_.errors
            output = env().render_template_as_markup(
                "actions/document/delete_section/"
                "stream_confirm_delete_section.jinja",
                section_mid=node_id,
                context_document_mid=context_document_mid,
                errors=errors,
            )
            return HTMLResponse(
                content=output,
                status_code=200 if len(errors) == 0 else 422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )
        try:
            delete_command = DeleteSectionCommand(
                section=section,
                traceability_index=export_action.traceability_index,
            )
            delete_command.perform()
        except MultipleValidationErrorAsList as error_:
            errors = error_.errors
            output = env().render_template_as_markup(
                "actions/document/delete_section/"
                "stream_confirm_delete_section.jinja",
                section_mid=node_id,
                context_document_mid=context_document_mid,
                errors=errors,
            )
            return HTMLResponse(
                content=output,
                status_code=200 if len(errors) == 0 else 422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        context_document: SDocDocument = assert_cast(
            export_action.traceability_index.get_node_by_mid(
                MID(context_document_mid)
            ),
            SDocDocument,
        )

        # Saving new content to .SDoc file.
        SDWriter(project_config).write_to_file(section.document)

        # Rendering back the Turbo template.
        link_renderer = LinkRenderer(
            root_path=section.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=section.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=section.document,
        )
        view_object: DocumentScreenViewObject = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=context_document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = env().render_template_as_markup(
            "actions/document/delete_section/stream_delete_section.jinja.html",
            view_object=view_object,
        )
        output += env().render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=view_object,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.delete(
        "/actions/document/delete_requirement",
        response_class=Response,
    )
    def delete_requirement(
        node_id: str, context_document_mid: str, confirmed: bool = False
    ):
        requirement: SDocNode = (
            export_action.traceability_index.get_node_by_mid(MID(node_id))
        )
        if not confirmed:
            errors: List[str]
            try:
                delete_command = DeleteRequirementCommand(
                    requirement=requirement,
                    traceability_index=export_action.traceability_index,
                )
                delete_command.validate()
                errors = []
            except MultipleValidationErrorAsList as error_:
                errors = error_.errors

            output = env().render_template_as_markup(
                "actions/document/delete_requirement/"
                "stream_confirm_delete_requirement.jinja",
                requirement_mid=node_id,
                context_document_mid=context_document_mid,
                errors=errors,
            )
            return HTMLResponse(
                content=output,
                status_code=200 if len(errors) == 0 else 422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        try:
            delete_command = DeleteRequirementCommand(
                requirement=requirement,
                traceability_index=export_action.traceability_index,
            )
            delete_command.perform()
        except MultipleValidationError:
            return HTMLResponse(
                content="",
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Saving new content to .SDoc file.
        SDWriter(project_config).write_to_file(requirement.document)

        context_document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(
                MID(context_document_mid)
            )
        )

        # Rendering back the Turbo template.
        link_renderer = LinkRenderer(
            root_path=requirement.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=requirement.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=requirement.document,
        )
        view_object: DocumentScreenViewObject = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=context_document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = env().render_template_as_markup(
            "actions/document/delete_requirement/"
            "stream_delete_requirement.jinja.html",
            view_object=view_object,
        )

        output += env().render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=view_object,
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
            target_node, SDocNode
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

        # Saving new content to .SDoc file.
        SDWriter(project_config).write_to_file(moved_node.document)

        # Update the index because other documents might reference this
        # document's sections. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        link_renderer = LinkRenderer(
            root_path=moved_node.document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=moved_node.document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=moved_node.document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=moved_node.document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        return HTMLResponse(
            content=view_object.render_update_document_content_with_moved_node(
                env(), moved_node
            ),
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    # Generic routes
    @router.get("/actions/project_index/new_document", response_class=Response)
    def get_new_document():
        output = env().render_template_as_markup(
            "actions/project_index/stream_new_document.jinja.html",
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

        if project_config.include_doc_paths is not None:
            path_filter_includes = PathFilter(
                project_config.include_doc_paths, positive_or_negative=True
            )
            if not path_filter_includes.match(document_path):
                error_object.add_error(
                    "document_path",
                    (
                        "Document path is not a valid path according to "
                        "the project config's setting 'include_doc_paths': "
                        f"{project_config.include_doc_paths}."
                    ),
                )
        if project_config.exclude_doc_paths is not None:
            path_filter_excludes = PathFilter(
                project_config.exclude_doc_paths, positive_or_negative=False
            )
            if path_filter_excludes.match(document_path):
                error_object.add_error(
                    "document_path",
                    (
                        "Document path is not a valid path according to "
                        "the project config's setting 'exclude_doc_paths': "
                        f"{project_config.exclude_doc_paths}."
                    ),
                )

        if error_object.any_errors():
            output = env().render_template_as_markup(
                "actions/project_index/stream_new_document.jinja.html",
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

        if not document_path.endswith(".sdoc"):
            document_path = document_path + ".sdoc"

        assert isinstance(project_config.input_paths, list)
        full_input_path = os.path.abspath(project_config.input_paths[0])
        file_tree_mount_folder = os.path.basename(
            os.path.dirname(full_input_path)
        )
        doc_full_path = os.path.join(full_input_path, document_path)
        doc_full_path_dir = os.path.dirname(doc_full_path)
        document_file_name = os.path.basename(doc_full_path)
        input_doc_dir_rel_path = os.path.dirname(document_path)
        input_doc_assets_dir_rel_path = (
            "/".join(
                (
                    file_tree_mount_folder,
                    input_doc_dir_rel_path,
                    "_assets",
                )
            )
            if len(input_doc_dir_rel_path) > 0
            else "/".join((file_tree_mount_folder, "_assets"))
        )

        Path(doc_full_path_dir).mkdir(parents=True, exist_ok=True)
        document = SDocDocument(
            mid=None,
            title=document_title,
            config=None,
            view=None,
            grammar=DocumentGrammar.create_default(parent=None),
            free_texts=[],
            section_contents=[],
        )
        # FIXME: Fill in the document meta correctly.
        document.meta = DocumentMeta(
            level=0,
            file_tree_mount_folder=None,
            document_filename=document_file_name,
            document_filename_base=None,
            input_doc_full_path=doc_full_path,
            input_doc_rel_path=SDocRelativePath(document_path),
            input_doc_dir_rel_path=SDocRelativePath(input_doc_dir_rel_path),
            input_doc_assets_dir_rel_path=SDocRelativePath(
                input_doc_assets_dir_rel_path
            ),
            output_document_dir_full_path=None,
            output_document_dir_rel_path=SDocRelativePath("FIXME"),
        )

        SDWriter(project_config).write_to_file(document)

        export_action.build_index()
        export_action.export()

        view_object = ProjectTreeViewObject(
            traceability_index=export_action.traceability_index,
            project_config=project_config,
        )
        output = env().render_template_as_markup(
            "actions/project_index/stream_create_document.jinja.html",
            view_object=view_object,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/new_comment", response_class=Response)
    def document__add_comment(
        requirement_mid: str,
        document_mid: str,
        context_document_mid: str,
        element_type: str,
    ):
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        # The data of the form object is ignored. What matters is the comment
        # form data.
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "add_requirement_comment/"
            "stream_add_requirement_comment.jinja.html",
            requirement_mid=requirement_mid,
            form_object=RequirementFormObject(
                is_new=False,
                element_type=element_type,
                requirement_mid=requirement_mid,
                document_mid=document.reserved_mid,
                context_document_mid=context_document_mid,
                fields=[],
                reference_fields=[],
                exiting_requirement_uid=None,
                grammar=grammar,
                relation_types=[],
                basic_free_text=False,
            ),
            field=RequirementFormField(
                field_mid=MID.create(),
                field_name="COMMENT",
                field_type=RequirementFormFieldType.MULTILINE,
                field_value="",
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
    def document__add_relation(
        requirement_mid: str,
        document_mid: str,
        context_document_mid: str,
        element_type: str,
    ):
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar

        element: GrammarElement = grammar.elements_by_type[element_type]
        grammar_element_relations = element.get_relation_types()

        # The data of the form object is ignored. What matters is the relation
        # form data.
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "add_requirement_relation/"
            "stream_add_requirement_relation.jinja.html",
            requirement_mid=requirement_mid,
            form_object=RequirementFormObject(
                is_new=False,
                element_type=element_type,
                requirement_mid=requirement_mid,
                document_mid=document_mid,
                context_document_mid=context_document_mid,
                fields=[],
                reference_fields=[],
                exiting_requirement_uid=None,
                grammar=grammar,
                relation_types=grammar_element_relations,
                basic_free_text=False,
            ),
            field=RequirementReferenceFormField(
                field_mid=MID.create(),
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
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        form_object = DocumentConfigFormObject.create_from_document(
            document=document
        )

        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "edit_document_config/"
            "stream_edit_document_config.jinja.html",
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

    @router.get(
        "/actions/document/edit_included_document", response_class=Response
    )
    def document__edit_included_document(
        document_mid: str, context_document_mid: str
    ):
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        form_object = IncludedDocumentFormObject.create_from_document(
            document=document,
            context_document_mid=context_document_mid,
            jinja_environment=env(),
        )
        return HTMLResponse(
            content=form_object.render_edit_form(),
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
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
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
            )
            update_command.perform()
        except MultipleValidationError as validation_error:
            for error_key, errors in validation_error.errors.items():
                for error in errors:
                    form_object.add_error(error_key, error)
            html_output = env().render_template_as_markup(
                "actions/"
                "document/"
                "edit_document_config/"
                "stream_edit_document_config.jinja.html",
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
        SDWriter(project_config).write_to_file(document)

        # Update the index because other documents might be referenced by this
        # document's free text. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        html_output = env().render_template_as_markup(
            "actions/"
            "document/"
            "edit_document_config/"
            "stream_save_document_config.jinja.html",
            view_object=view_object,
        )
        return HTMLResponse(
            content=html_output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/actions/document/save_included_document", response_class=Response
    )
    async def document__save_included_document(request: Request):
        request_form_data: FormData = await request.form()
        request_dict: Dict[str, str] = dict(request_form_data)
        document_mid: str = request_dict["document_mid"]
        context_document_mid: str = request_dict["context_document_mid"]
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        context_document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(
                MID(context_document_mid)
            )
        )
        form_object: IncludedDocumentFormObject = (
            IncludedDocumentFormObject.create_from_request(
                request_form_data=request_form_data, jinja_environment=env()
            )
        )
        try:
            update_command = UpdateIncludedDocumentTransform(
                form_object=form_object,
                document=document,
                traceability_index=export_action.traceability_index,
            )
            update_command.perform()
        except MultipleValidationError as validation_error:
            for error_key, errors in validation_error.errors.items():
                for error in errors:
                    form_object.add_error(error_key, error)
            return HTMLResponse(
                content=form_object.render_edit_form(),
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Re-generate the document's SDOC.
        SDWriter(project_config).write_to_file(document)

        # Update the index because other documents might be referenced by this
        # document's free text. These documents will be regenerated on demand,
        # when they are opened next time.
        export_action.traceability_index.update_last_updated()

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=context_document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        return HTMLResponse(
            content=view_object.render_updated_nodes_and_toc(
                nodes=[document], jinja_environment=env()
            ),
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/actions/document/cancel_edit_config", response_class=Response)
    def document__cancel_edit_config(document_mid: str):
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = env().render_template_as_markup(
            "actions/"
            "document/"
            "edit_document_config/"
            "stream_cancel_edit_document_config.jinja.html",
            view_object=view_object,
            document=document,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_edit_included_document",
        response_class=Response,
    )
    def document__cancel_edit_included_document(document_mid: str):
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = env().render_template_as_markup(
            "actions/document/edit_section/stream_updated_section.jinja.html",
            view_object=view_object,
            document=document,
            node=document,
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
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        form_object: GrammarFormObject = GrammarFormObject.create_from_document(
            document=document,
            project_config=project_config,
            jinja_environment=env(),
        )
        return HTMLResponse(
            content=form_object.render(),
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
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        form_object: GrammarFormObject = GrammarFormObject.create_from_request(
            document_mid=document_mid,
            request_form_data=request_form_data,
            project_config=project_config,
            jinja_environment=env(),
        )
        if not form_object.validate():
            return HTMLResponse(
                content=form_object.render(),
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
            output = form_object.render_close_form()
            return HTMLResponse(
                content=output,
                status_code=200,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Re-generate the document's SDOC.
        SDWriter(project_config).write_to_file(document)

        # Re-generate the document.
        html_generator.export_single_document(
            document=document,
            traceability_index=export_action.traceability_index,
        )

        # Re-generate the document tree.
        html_generator.export_project_tree_screen(
            traceability_index=export_action.traceability_index,
        )

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = (
            form_object.render_close_form()
            + env().render_template_as_markup(
                "actions/"
                "document/"
                "_shared/"
                "stream_refresh_document.jinja.html",
                view_object=view_object,
            )
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/add_grammar_element", response_class=Response
    )
    def document__add_grammar_element(document_mid: str):
        form_object: GrammarFormObject = GrammarFormObject(
            document_mid=document_mid,
            fields=[],  # Not used in this limited partial template.
            project_config=project_config,
            jinja_environment=env(),
            imported_grammar_file=None,
        )
        return HTMLResponse(
            content=form_object.render_row_with_new_grammar_element(),
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/edit_grammar_element", response_class=Response
    )
    def document__edit_grammar_element(document_mid: str, element_mid: str):
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        form_object: GrammarElementFormObject = (
            GrammarElementFormObject.create_from_document(
                document=document,
                element_mid=element_mid,
                project_config=project_config,
                jinja_environment=env(),
            )
        )

        return HTMLResponse(
            content=form_object.render(),
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/actions/document/save_grammar_element", response_class=Response
    )
    async def document__save_grammar_element(request: Request):
        request_form_data: FormData = await request.form()
        request_dict: Dict[str, str] = dict(request_form_data)
        document_mid: str = request_dict["document_mid"]
        document: SDocDocument = (
            export_action.traceability_index.get_node_by_mid(MID(document_mid))
        )
        form_object: GrammarElementFormObject = (
            GrammarElementFormObject.create_from_request(
                document=document,
                request_form_data=request_form_data,
                project_config=project_config,
                jinja_environment=env(),
            )
        )
        if not form_object.validate():
            return HTMLResponse(
                content=form_object.render_after_validation(),
                status_code=422,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Update the document with new grammar.
        update_grammar_action = UpdateGrammarElementCommand(
            form_object=form_object,
            document=document,
            traceability_index=export_action.traceability_index,
        )
        grammar_changed = update_grammar_action.perform()

        # If the grammar has not changed, do nothing and save the edit form.
        if not grammar_changed:
            output = form_object.render_close_form()
            return HTMLResponse(
                content=output,
                status_code=200,
                headers={
                    "Content-Type": "text/vnd.turbo-stream.html",
                },
            )

        # Re-generate the document's SDOC.
        SDWriter(project_config).write_to_file(document)

        # Re-generate the document.
        html_generator.export_single_document(
            document=document,
            traceability_index=export_action.traceability_index,
        )

        # Re-generate the document tree.
        html_generator.export_project_tree_screen(
            traceability_index=export_action.traceability_index,
        )

        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            markup=document.config.get_markup(),
            traceability_index=export_action.traceability_index,
            link_renderer=link_renderer,
            html_templates=html_generator.html_templates,
            config=project_config,
            context_document=document,
        )
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.document(),
            document=document,
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            standalone=False,
        )
        output = (
            form_object.render_close_form()
            + env().render_template_as_markup(
                "actions/"
                "document/"
                "_shared/"
                "stream_refresh_document.jinja.html",
                view_object=view_object,
            )
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
        form_object: GrammarElementFormObject = GrammarElementFormObject(
            document_mid=document_mid,
            element_mid="NOT_RELEVANT",
            element_name="NOT_RELEVANT",
            fields=[],  # Not used in this limited partial template.
            relations=[],  # Not used in this limited partial template.
            project_config=project_config,
            jinja_environment=env(),
        )
        return HTMLResponse(
            content=form_object.render_row_with_new_field(),
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/add_grammar_relation", response_class=Response
    )
    def document__add_grammar_relation(document_mid: str):
        form_object = GrammarElementFormObject(
            document_mid=document_mid,
            element_mid="NOT_RELEVANT",
            element_name="NOT_RELEVANT",
            fields=[],  # Not used in this limited partial template.
            relations=[],  # Not used in this limited partial template.
            project_config=project_config,
            jinja_environment=env(),
        )
        return HTMLResponse(
            content=form_object.render_row_with_new_relation(),
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
        output = env().render_template_as_markup(
            "actions/project_index/import_reqif_document/"
            "stream_form_import_reqif_document.jinja.html",
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

        documents: Optional[List[SDocDocument]] = None
        try:
            reqif_bundle = ReqIFParser.parse_from_string(contents)
            converter: P01_ReqIFToSDocConverter = P01_ReqIFToSDocConverter()
            documents: List[SDocDocument] = converter.convert_reqif_bundle(
                reqif_bundle,
                enable_mid=project_config.reqif_enable_mid,
                import_markup=project_config.reqif_import_markup,
            )
        except ReqIFXMLParsingError as exception:
            error_object.add_error(
                "reqif_file", "Cannot parse ReqIF file: " + str(exception)
            )
        except Exception as exception:
            error_object.add_error("reqif_file", str(exception))

        if error_object.any_errors():
            output = env().render_template_as_markup(
                "actions/project_index/import_reqif_document/"
                "stream_form_import_reqif_document.jinja.html",
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
        assert isinstance(project_config.input_paths, list)
        for document in documents:
            document_title = re.sub(r"[^A-Za-z0-9-]", "_", document.title)
            document_path = f"{document_title}.sdoc"

            full_input_path = os.path.abspath(project_config.input_paths[0])
            doc_full_path = os.path.join(full_input_path, document_path)
            doc_full_path_dir = os.path.dirname(doc_full_path)
            Path(doc_full_path_dir).mkdir(parents=True, exist_ok=True)

            file_tree_mount_folder = os.path.basename(
                os.path.dirname(full_input_path)
            )

            input_doc_assets_dir_rel_path = "/".join(
                (file_tree_mount_folder, "_assets")
            )

            # FIXME: Fill in the meta information correctly.
            document.meta = DocumentMeta(
                level=0,
                file_tree_mount_folder=None,
                document_filename=document_path,
                document_filename_base=None,
                input_doc_full_path=doc_full_path,
                input_doc_rel_path=SDocRelativePath(document_path),
                input_doc_dir_rel_path=SDocRelativePath(""),
                input_doc_assets_dir_rel_path=SDocRelativePath(
                    input_doc_assets_dir_rel_path
                ),
                output_document_dir_full_path=None,
                output_document_dir_rel_path=SDocRelativePath("FIXME"),
            )

            SDWriter(project_config).write_to_file(document)

        export_action.build_index()
        export_action.export()

        view_object = ProjectTreeViewObject(
            traceability_index=export_action.traceability_index,
            project_config=project_config,
        )
        output = env().render_template_as_markup(
            "actions/project_index/import_reqif_document/"
            "stream_refresh_with_imported_reqif_document.jinja.html",
            view_object=view_object,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/export_html2pdf/{document_mid}", response_class=Response)
    def get_export_html2pdf(document_mid: str):  # noqa: ARG001
        if not project_config.is_activated_html2pdf():
            return Response(
                content="The HTML2PDF feature is not activated in the project config.",
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )

        document = export_action.traceability_index.get_node_by_mid(
            MID(document_mid)
        )

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        markup_renderer = MarkupRenderer.create(
            "RST",
            export_action.traceability_index,
            link_renderer,
            html_templates,
            project_config,
            document,
        )

        pdf_project_config = copy.deepcopy(project_config)
        pdf_project_config.is_running_on_server = False

        with measure_performance("Generating printable HTML document"):
            document_content = DocumentHTML2PDFGenerator.export(
                pdf_project_config,
                document,
                export_action.traceability_index,
                markup_renderer,
                link_renderer,
                standalone=False,
                html_templates=html_templates,
            )

        path_to_output_html = os.path.join(
            server_config.output_path, "html", "_temp.html"
        )
        path_to_output_pdf = os.path.join(
            server_config.output_path, "html", "_temp.pdf"
        )
        pdf_print_driver = PDFPrintDriver()
        with open(path_to_output_html, mode="w", encoding="utf8") as temp_file_:
            temp_file_.write(document_content)

            try:
                pdf_print_driver.get_pdf_from_html(
                    project_config,
                    f"{path_to_output_html},{path_to_output_pdf}",
                )
            except TimeoutError:
                return Response(
                    content="HTML2PDF timeout error.",
                    status_code=HTTP_STATUS_GATEWAY_TIMEOUT,
                )

            return FileResponse(
                path=path_to_output_pdf,
                status_code=200,
                headers={
                    "Content-Disposition": 'attachment; filename="document.pdf"',
                },
                media_type="application/octet-stream",
            )

    @router.get(
        "/reqif/export_document/{document_mid}", response_class=Response
    )
    def get_reqif_export_document(document_mid: str):  # noqa: ARG001
        # TODO: Export single document, not the whole tree.
        return get_reqif_export_tree()

    @router.get("/reqif/export_tree", response_class=Response)
    def get_reqif_export_tree():
        reqif_bundle = P01_SDocToReqIFObjectConverter.convert_document_tree(
            document_tree=export_action.traceability_index.document_tree,
            multiline_is_xhtml=project_config.reqif_multiline_is_xhtml,
            enable_mid=project_config.reqif_enable_mid,
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

    @router.get("/search", response_class=Response)
    def get_search(q: Optional[str] = None):
        if not project_config.is_activated_search():
            return Response(
                content="The Search feature is not activated in the project config.",
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )
        search_results = []
        error = None
        node_query = None

        if q is not None and len(q) > 0:
            try:
                query: Query = QueryReader.read(q)
                node_query = QueryObject(
                    query, export_action.traceability_index
                )
            except:
                error = "error: Cannot parse query."

        if node_query is not None:
            result = []
            try:
                for document in (
                    export_action.traceability_index.document_tree.document_list
                ):
                    document_iterator = (
                        export_action.traceability_index.get_document_iterator(
                            document
                        )
                    )
                    for node in document_iterator.all_content(
                        print_fragments=False, print_fragments_from_files=False
                    ):
                        if node_query.evaluate(node):
                            result.append(node)
                search_results = result
            except (AttributeError, NameError, TypeError) as attribute_error_:
                error = attribute_error_.args[0]

        view_object = SearchScreenViewObject(
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            templates=html_templates,
            search_results=search_results,
            search_value=q if q is not None else "",
            error=error,
        )
        output = view_object.render_screen(html_templates.jinja_environment())

        return Response(
            content=output,
            status_code=200,
        )

    @router.get("/nestor", response_class=Response)
    def get_nestor():
        output_json_root = os.path.join(project_config.output_dir, "html")
        Path(output_json_root).mkdir(parents=True, exist_ok=True)
        JSONGenerator().export_tree(
            export_action.traceability_index, project_config, output_json_root
        )
        path_to_json = os.path.join("index.json")
        view_object = NestorViewObject(
            traceability_index=export_action.traceability_index,
            project_config=project_config,
            templates=html_templates,
            path_to_json=path_to_json,
        )
        output = view_object.render_screen(html_templates.jinja_environment())

        return Response(
            content=output,
            status_code=200,
        )

    @router.get("/{full_path:path}", response_class=Response)
    def get_incoming_request(request: Request, full_path: str):
        # FIXME: This seems to be quite un-sanitized.
        _, file_extension = os.path.splitext(full_path)
        if file_extension == ".html":
            return get_document(request, full_path)
        else:
            return get_asset(request, full_path)

    def get_document(request: Request, url_to_document: str):
        document_relative_path: SDocRelativePath = SDocRelativePath.from_url(
            url_to_document
        )
        full_path_to_document = os.path.join(
            server_config.output_path,
            "html",
            document_relative_path.relative_path,
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
            if document_relative_path.relative_path.startswith("_source_files"):
                # FIXME: We could be more specific here and only generate the
                # requested file.
                html_generator.export_source_coverage_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif document_relative_path.relative_path == "index.html":
                html_generator.export_project_tree_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif (
                document_relative_path.relative_path
                == "traceability_matrix.html"
            ):
                if not project_config.is_activated_requirements_coverage():
                    return Response(
                        content="The Requirements Coverage feature is not activated in the project config.",
                        status_code=HTTP_STATUS_PRECONDITION_FAILED,
                    )
                html_generator.export_requirements_coverage_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif document_relative_path.relative_path == "source_coverage.html":
                if not project_config.is_activated_requirements_to_source_traceability():
                    return Response(
                        content="The Requirements to Source Files feature is not activated in the project config.",
                        status_code=HTTP_STATUS_PRECONDITION_FAILED,
                    )
                html_generator.export_source_coverage_screen(
                    traceability_index=export_action.traceability_index,
                )
            elif (
                document_relative_path.relative_path
                == "project_statistics.html"
            ):
                if not project_config.is_activated_project_statistics():
                    return Response(
                        content="The Project Statistics feature is not activated in the project config.",
                        status_code=HTTP_STATUS_PRECONDITION_FAILED,
                    )
                html_generator.export_project_statistics(
                    traceability_index=export_action.traceability_index,
                )
            else:
                if document_relative_path.relative_path.endswith("-TABLE.html"):
                    base_document_url = (
                        document_relative_path.relative_path.replace(
                            "-TABLE", ""
                        )
                    )
                    document_type_to_generate = DocumentType.TABLE
                elif document_relative_path.relative_path.endswith(
                    "-DEEP-TRACE.html"
                ):
                    base_document_url = (
                        document_relative_path.relative_path.replace(
                            "-DEEP-TRACE", ""
                        )
                    )
                    document_type_to_generate = DocumentType.DEEPTRACE
                elif document_relative_path.relative_path.endswith(
                    "-TRACE.html"
                ):
                    base_document_url = (
                        document_relative_path.relative_path.replace(
                            "-TRACE", ""
                        )
                    )
                    document_type_to_generate = DocumentType.TRACE
                elif document_relative_path.relative_path.endswith("-PDF.html"):
                    if not project_config.is_activated_html2pdf():
                        return Response(
                            content="The HTML2PDF feature is not activated in the project config.",
                            status_code=HTTP_STATUS_PRECONDITION_FAILED,
                        )
                    base_document_url = (
                        document_relative_path.relative_path.replace("-PDF", "")
                    )
                    document_type_to_generate = DocumentType.PDF
                elif document_relative_path.relative_path.endswith(
                    ".standalone.html"
                ):
                    if not project_config.is_activated_standalone_document():
                        return Response(
                            content="The Standalone Document feature is not activated in the project config.",
                            status_code=HTTP_STATUS_PRECONDITION_FAILED,
                        )
                    base_document_url = (
                        document_relative_path.relative_path.replace(
                            ".standalone", ""
                        )
                    )
                    document_type_to_generate = DocumentType.DOCUMENT
                else:
                    # Either this is a normal document, or the path is broken.
                    base_document_url = document_relative_path.relative_path
                    document_type_to_generate = DocumentType.DOCUMENT
                document = export_action.traceability_index.document_tree.map_docs_by_rel_paths.get(
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
