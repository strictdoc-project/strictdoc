# mypy: disable-error-code="arg-type,no-untyped-def,union-attr"
from typing import Dict, Optional

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.traceability_matrix_view_object import (
    TraceabilityMatrixViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class TraceabilityMatrixHTMLGenerator:
    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ):
        assert isinstance(html_templates, HTMLTemplates)

        known_relations: Dict[str, Dict[Optional[str], bool]] = {
            "Parent": {},
            "Child": {},
            "File": {},
        }

        discovered_relation_types = set()

        document_: SDocDocument
        for document_ in traceability_index.document_tree.document_list:
            assert document_.grammar is not None
            document_grammar: DocumentGrammar = document_.grammar
            for grammar_element_ in document_grammar.elements:
                for relation_ in grammar_element_.relations:
                    discovered_relation_types.add(relation_.relation_type)

                    bucket = known_relations[relation_.relation_type]

                    if relation_.relation_role not in bucket:
                        bucket[relation_.relation_role] = True

        for relation_type_ in list(known_relations.keys()):
            if relation_type_ not in discovered_relation_types:
                del known_relations[relation_type_]

        """
        Validate that all config-provided relation tuples are actually present
        in the existing documents.
        A typical config entry may look like this:
        [
            ("Parent", None),
            ("Parent", "Refines"),
            ("Parent", "REQUIREMENT_FOR"),
            ("File", None)
        ]
        """
        config_relation_tuples = (
            project_config.traceability_matrix_relation_columns
            if project_config.traceability_matrix_relation_columns is not None
            else []
        )
        for config_relation_tuple_ in config_relation_tuples:
            assert config_relation_tuple_[0] in known_relations
            bucket = known_relations[config_relation_tuple_[0]]
            assert config_relation_tuple_[1] in bucket

        """
        After the config values have been validated, merge both the
        config-provided list of relation tuples with the list that was
        discovered from the existing documents.
        """
        known_relations_list = list(config_relation_tuples)
        for relation_type_, bucket_ in known_relations.items():
            for relation_role_, _ in bucket_.items():
                relation_tuple = (relation_type_, relation_role_)
                if relation_tuple not in known_relations_list:
                    known_relations_list.append(relation_tuple)

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        markup_renderer = MarkupRenderer.create(
            "RST",
            traceability_index,
            link_renderer,
            html_templates,
            project_config,
            None,
        )

        view_object = TraceabilityMatrixViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            known_relations_list=known_relations_list,
        )
        return view_object.render_screen(html_templates.jinja_environment())
