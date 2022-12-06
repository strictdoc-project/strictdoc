import os
import uuid
from pathlib import Path
from typing import Optional, Union

from jinja2 import Environment, PackageLoader, StrictUndefined

from strictdoc import STRICTDOC_ROOT_PATH
from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.free_text import FreeText, FreeTextContainer
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import (
    ExportCommandConfig,
    ServerCommandConfig,
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
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.parallelizer import NullParallelizer
from strictdoc.server.error_object import ErrorObject

assert os.path.isabs(STRICTDOC_ROOT_PATH), f"{STRICTDOC_ROOT_PATH}"


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


class MainController:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        undefined=StrictUndefined,
    )
    env.globals.update(isinstance=isinstance)

    def __init__(self, config: ServerCommandConfig):
        self.config: ServerCommandConfig = config

        parallelizer = NullParallelizer()

        export_config = ExportCommandConfig(
            strictdoc_root_path=STRICTDOC_ROOT_PATH,
            input_paths=[self.config.input_path],
            output_dir=self.config.output_path,
            project_title="PROJECT_TITLE",
            formats=["html"],
            fields=None,
            no_parallelization=False,
            enable_mathjax=False,
            experimental_enable_file_traceability=False,
        )
        export_config.is_running_on_server = True
        self.export_action = ExportAction(
            config=export_config, parallelizer=parallelizer
        )
        self.export_action.build_index()
        self.export_action.export()

    def get_document(self, path_to_document):
        full_path_to_document = os.path.join(
            self.config.output_path, "html", path_to_document
        )
        assert os.path.isfile(full_path_to_document), f"{full_path_to_document}"
        with open(full_path_to_document, encoding="utf8") as sample_sdoc:
            content = sample_sdoc.read()
        return content

    def get_new_section(self, *, reference_mid: str, whereto: str):
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
        ] = self.export_action.traceability_index.get_node_by_id(reference_mid)
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

        template = MainController.env.get_template(
            "actions/document/create_section/stream_new_section.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
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

        return output

    @staticmethod
    def cancel_new_section(section_mid):
        template = MainController.env.get_template(
            "actions/document/create_section/stream_cancel_new_section.jinja.html"  # noqa: E501
        )
        output = template.render(section_mid=section_mid)
        return output

    def create_new_section(
        self,
        *,
        section_mid: str,
        section_title: str,
        section_content: Optional[str],
        reference_mid: str,
        whereto: str,
    ):
        assert (
            isinstance(section_mid, str) and len(section_mid) > 0
        ), section_mid
        assert (
            isinstance(reference_mid, str) and len(reference_mid) > 0
        ), reference_mid
        reference_node: Union[
            Document, Section
        ] = self.export_action.traceability_index.get_node_by_id(reference_mid)
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
            template = MainController.env.get_template(
                "actions/document/create_section/stream_new_section.jinja.html"
            )
            link_renderer = LinkRenderer(
                self.export_action.config.output_html_root
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=self.export_action.traceability_index,
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
            return output

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
        self.export_action.traceability_index._map_id_to_node[
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
        self.export_action.export()

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/create_section/stream_created_section.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = self.export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            traceability_index=self.export_action.traceability_index,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            config=self.export_action.config,
        )

        toc_template = MainController.env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )

        return output

    def update_section(
        self,
        *,
        section_id: str,
        section_title: str,
        section_content: Optional[str],
    ):
        section: Section = self.export_action.traceability_index.get_node_by_id(
            section_id
        )

        form_object = SectionFormObject(
            section_mid=section_id,
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
            template = MainController.env.get_template(
                "actions/document/create_section/stream_new_section.jinja.html"
            )
            link_renderer = LinkRenderer(
                self.export_action.config.output_html_root
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=self.export_action.traceability_index,
                link_renderer=link_renderer,
                context_document=section.document,
            )
            output = template.render(
                renderer=markup_renderer,
                link_renderer=link_renderer,
                form_object=form_object,
                target_node_mid=section.node_id,
                document_type=DocumentType.document(),
                is_new_section=True,
                replace_action="replace",
                reference_mid="NOT_RELEVANT",
                whereto="NOT_RELEVANT",
            )
            return output

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
        self.export_action.export()

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/edit_section/stream_updated_section.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=section.parent,
        )
        output = template.render(
            renderer=markup_renderer,
            link_renderer=link_renderer,
            section=section,
            document_type=DocumentType.document(),
            config=self.export_action.config,
        )
        iterator = self.export_action.traceability_index.get_document_iterator(
            section.document
        )
        toc_template = MainController.env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )
        return output

    def cancel_edit_section(self, section_mid):
        section: Section = self.export_action.traceability_index.get_node_by_id(
            section_mid
        )
        template = MainController.env.get_template(
            "actions/document/edit_section/stream_updated_section.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=section.parent,
        )
        output = template.render(
            renderer=markup_renderer,
            link_renderer=link_renderer,
            section=section,
            document_type=DocumentType.document(),
            config=self.export_action.config,
        )
        return output

    def get_edit_section(self, section_id):
        section: Section = self.export_action.traceability_index.get_node_by_id(
            section_id
        )
        document = section.parent

        statement = (
            section.free_texts[0].get_parts_as_text()
            if len(section.free_texts) > 0
            else None
        )
        form_object = SectionFormObject(
            section_mid=section.node_id,
            section_title=section.title,
            section_statement=statement,
        )

        template = MainController.env.get_template(
            "actions/document/edit_section/stream_edit_section.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
            is_new_section=False,
            section_mid=section.node_id,
        )

        return output

    def get_edit_document_freetext(self, document_id):
        document = self.export_action.traceability_index.get_node_by_id(
            document_id
        )
        form_object = ExistingDocumentFreeTextObject.create_from_document(
            document=document,
        )
        template = MainController.env.get_template(
            "actions/document/document_freetext/stream_edit_document_freetext.jinja.html"  # noqa: E501
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
        )

        return output

    def update_document_freetext(self, document_id, document_freetext):
        assert isinstance(document_id, str)

        print(document_freetext)

        form_object = ExistingDocumentFreeTextObject(
            document_mid=document_id, document_free_text=document_freetext
        )
        document: Document = (
            self.export_action.traceability_index.get_node_by_id(document_id)
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
            template = MainController.env.get_template(
                "actions/document/document_freetext/stream_edit_document_freetext.jinja.html"  # noqa: E501
            )
            link_renderer = LinkRenderer(
                self.export_action.config.output_html_root
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=self.export_action.traceability_index,
                link_renderer=link_renderer,
                context_document=document,
            )
            output = template.render(
                renderer=markup_renderer,
                form_object=form_object,
                document_type=DocumentType.document(),
            )
            return output

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
        self.export_action.export()

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/document_freetext/"
            "stream_updated_document_freetext.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_type=DocumentType.document(),
            config=self.export_action.config,
        )

        return output

    def cancel_edit_document_freetext(self, document_id: str):
        assert (
            isinstance(document_id, str) and len(document_id) > 0
        ), document_id
        document: Document = (
            self.export_action.traceability_index.get_node_by_id(document_id)
        )

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/document_freetext/"
            "stream_cancel_edit_freetext.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_type=DocumentType.document(),
            config=self.export_action.config,
        )

        return output

    def get_new_requirement(self, *, reference_mid: str, whereto: str):
        reference_node = self.export_action.traceability_index.get_node_by_id(
            reference_mid
        )
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        form_object = RequirementFormObject(
            requirement_mid=uuid.uuid4().hex,
            requirement_title=None,
            requirement_statement=None,
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

        template = MainController.env.get_template(
            "actions/document/create_requirement/stream_new_requirement.jinja.html"  # noqa: E501
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
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

        return output

    def create_requirement(
        self,
        *,
        requirement_mid: str,
        requirement_title: str,
        requirement_statement: Optional[str],
        reference_mid: str,
        whereto: Optional[str],
    ):
        reference_node: Union[
            Document, Section
        ] = self.export_action.traceability_index.get_node_by_id(reference_mid)
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )
        form_object = RequirementFormObject(
            requirement_mid=requirement_mid,
            requirement_title=requirement_title,
            requirement_statement=requirement_statement,
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

        if requirement_statement is None or len(requirement_statement) == 0:
            form_object.add_error(
                "requirement_statement",
                "Requirement statement must not be empty.",
            )
        else:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter.write_with_validation(
                requirement_statement
            )
            if parsed_html is None:
                form_object.add_error("requirement_statement", rst_error)

        if form_object.any_errors():
            template = MainController.env.get_template(
                "actions/document/create_requirement/stream_new_requirement.jinja.html"  # noqa: E501
            )
            link_renderer = LinkRenderer(
                self.export_action.config.output_html_root
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=self.export_action.traceability_index,
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

            return output

        requirement = SDocObjectFactory.create_requirement(
            parent=parent,
            requirement_type="REQUIREMENT",
            uid=None,
            level=None,
            title=requirement_title
            if requirement_title is not None and len(requirement_title) > 0
            else None,
            statement=None,
            statement_multiline=requirement_statement
            if requirement_statement is not None
            else "",
            rationale=None,
            rationale_multiline=None,
            tags=None,
            comments=None,
        )
        requirement.node_id = requirement_mid
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(document)
        requirement.ng_level = parent.ng_level + 1
        self.export_action.traceability_index._map_id_to_node[
            requirement.node_id
        ] = requirement

        if requirement_title is not None and len(requirement_title) > 0:
            requirement.title = requirement_title

        # Updating section content.
        requirement.statement_multiline = requirement_statement

        parent.section_contents.insert(insert_to_idx, requirement)

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        self.export_action.export()

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/create_requirement/stream_created_requirement.jinja.html"  # noqa: E501
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = self.export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            traceability_index=self.export_action.traceability_index,
            config=self.export_action.config,
        )

        toc_template = MainController.env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )

        return output

    def get_edit_requirement(self, requirement_id):
        requirement: Requirement = (
            self.export_action.traceability_index.get_node_by_id(requirement_id)
        )
        form_object = RequirementFormObject.create_from_requirement(
            requirement=requirement
        )
        document = requirement.document
        template = MainController.env.get_template(
            "actions/document/edit_requirement/stream_edit_requirement.jinja.html"  # noqa: E501
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        output = template.render(
            is_new_requirement=False,
            renderer=markup_renderer,
            form_object=form_object,
            document_type=DocumentType.document(),
        )

        return output

    def update_requirement(
        self,
        *,
        requirement_mid: str,
        requirement_title: str,
        requirement_statement: Optional[str],
    ):
        assert (
            isinstance(requirement_mid, str) and len(requirement_mid) > 0
        ), f"{requirement_mid}"
        requirement = self.export_action.traceability_index.get_node_by_id(
            requirement_mid
        )
        document = requirement.document

        form_object = RequirementFormObject(
            requirement_mid=requirement_mid,
            requirement_title=requirement_title,
            requirement_statement=requirement_statement,
        )
        if requirement_statement is None or len(requirement_statement) == 0:
            form_object.add_error(
                "requirement_statement",
                "Requirement statement must not be empty.",
            )
        else:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter.write_with_validation(
                requirement_statement
            )
            if parsed_html is None:
                form_object.add_error("requirement_statement", rst_error)
        if form_object.any_errors():
            template = MainController.env.get_template(
                "actions/document/edit_requirement/stream_edit_requirement.jinja.html"  # noqa: E501
            )
            link_renderer = LinkRenderer(
                self.export_action.config.output_html_root
            )
            markup_renderer = MarkupRenderer.create(
                markup="RST",
                traceability_index=self.export_action.traceability_index,
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
            return output

        if requirement_title is not None and len(requirement_title) > 0:
            requirement.ordered_fields_lookup["TITLE"] = [
                RequirementField(
                    requirement,
                    field_name="TITLE",
                    field_value=requirement_title,
                    field_value_multiline=None,
                    field_value_references=None,
                )
            ]
            requirement.title = requirement_title
        else:
            if "TITLE" in requirement.ordered_fields_lookup:
                del requirement.ordered_fields_lookup["TITLE"]
                requirement.title = None

        requirement.statement_multiline = requirement_statement
        requirement.ordered_fields_lookup["STATEMENT"] = [
            RequirementField(
                requirement,
                field_name="STATEMENT",
                field_value=None,
                field_value_multiline=requirement_statement,
                field_value_references=None,
            )
        ]

        # Saving new content to .SDoc file.
        document_content = SDWriter().write(document)
        document_meta = document.meta
        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        # Re-exporting HTML files.
        self.export_action.export()

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/edit_requirement/stream_update_requirement.jinja.html"  # noqa: E501
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = self.export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            requirement=requirement,
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            traceability_index=self.export_action.traceability_index,
            config=self.export_action.config,
        )

        toc_template = MainController.env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )

        return output

    @staticmethod
    def cancel_new_requirement(requirement_mid):
        template = MainController.env.get_template(
            "actions/document/create_requirement/stream_cancel_new_requirement.jinja.html"  # noqa: E501
        )
        output = template.render(requirement_mid=requirement_mid)
        return output

    def cancel_edit_requirement(self, requirement_mid):
        assert (
            isinstance(requirement_mid, str) and len(requirement_mid) > 0
        ), f"{requirement_mid}"
        requirement = self.export_action.traceability_index.get_node_by_id(
            requirement_mid
        )
        document = requirement.document
        template = MainController.env.get_template(
            "actions/document/edit_requirement/stream_update_requirement.jinja.html"  # noqa: E501
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=document,
        )
        iterator = self.export_action.traceability_index.get_document_iterator(
            document
        )
        output = template.render(
            requirement=requirement,
            renderer=markup_renderer,
            document=document,
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            traceability_index=self.export_action.traceability_index,
            config=self.export_action.config,
        )
        return output

    def delete_section(self, section_mid):
        section: Section = self.export_action.traceability_index.get_node_by_id(
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
        self.export_action.export()

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/delete_section/stream_delete_section.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        markup_renderer = MarkupRenderer.create(
            markup="RST",
            traceability_index=self.export_action.traceability_index,
            link_renderer=link_renderer,
            context_document=section.document,
        )
        iterator = self.export_action.traceability_index.get_document_iterator(
            section.document
        )
        output = template.render(
            renderer=markup_renderer,
            document=section.document,
            document_iterator=iterator,
            traceability_index=self.export_action.traceability_index,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
            config=self.export_action.config,
        )

        toc_template = MainController.env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )
        return output

    def delete_requirement(self, requirement_mid):
        requirement: Requirement = (
            self.export_action.traceability_index.get_node_by_id(
                requirement_mid
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
        self.export_action.export()

        # Rendering back the Turbo template.
        template = MainController.env.get_template(
            "actions/document/delete_section/stream_delete_section.jinja.html"
        )
        link_renderer = LinkRenderer(self.export_action.config.output_html_root)
        output = template.render(requirement=requirement)

        toc_template = MainController.env.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        iterator = self.export_action.traceability_index.get_document_iterator(
            requirement.document
        )
        output += toc_template.render(
            document_iterator=iterator,
            document_type=DocumentType.document(),
            link_renderer=link_renderer,
        )
        return output

    def get_new_document(self):
        template = MainController.env.get_template(
            "actions/document_tree/stream_new_document.jinja.html"
        )
        output = template.render(
            error_object=ErrorObject(),
            document_title="",
            document_path="",
        )
        return output

    def create_document(
        self, *, document_title: Optional[str], document_path: str
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
            template = MainController.env.get_template(
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
            return output

        full_input_path = os.path.abspath(
            self.export_action.config.input_paths[0]
        )
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

        self.export_action.build_index()
        self.export_action.export()

        template = MainController.env.get_template(
            "actions/document_tree/stream_create_document.jinja.html"
        )
        document_tree_iterator = DocumentTreeIterator(
            self.export_action.traceability_index.document_tree
        )

        output = template.render(
            config=self.export_action.config,
            document_tree=self.export_action.traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
            static_path="_static",
            traceability_index=self.export_action.traceability_index,
        )
        return output
