import os
import traceback
from functools import partial
from typing import Optional

from textx import metamodel_from_str, TextXSemanticError
from textx.scoping.tools import get_location

from strictdoc.backend.dsl.document_reference import DocumentReference
from strictdoc.backend.dsl.error_handling import StrictDocSemanticError
from strictdoc.backend.dsl.grammar import STRICTDOC_GRAMMAR
from strictdoc.backend.dsl.models.config_special_field import ConfigSpecialField
from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.reference import Reference
from strictdoc.backend.dsl.models.requirement import (
    Requirement,
    CompositeRequirement,
    RequirementComment,
)
from strictdoc.backend.dsl.models.section import Section, FreeText
from strictdoc.backend.dsl.models.special_field import SpecialField

DOCUMENT_MODELS = [
    DocumentConfig,
    ConfigSpecialField,
    Document,
    RequirementComment,
    Section,
    Requirement,
    CompositeRequirement,
    # Body,
    SpecialField,
    Reference,
    FreeText,
]


def document_config_obj_processor(document_config, parse_context):
    parse_context.document_config = document_config


def section_obj_processor(section):
    section.parent.ng_sections.append(section)


# During parsing, it is often the case that the node's parents do not have their
# levels resolved yet. We go up the parent chain and resolve all of the parents
# manually.
def resolve_parents(node):
    parents_to_resolve_level = []
    cursor = node.parent
    while cursor.ng_level is None:
        parents_to_resolve_level.append(cursor)
        cursor = cursor.parent
    for parent_idx, parent in enumerate(reversed(parents_to_resolve_level)):
        parent.ng_level = cursor.ng_level + parent_idx + 1


def composite_requirement_obj_processor(composite_requirement, parse_context):
    composite_requirement.ng_document_reference = (
        parse_context.document_reference
    )

    if isinstance(composite_requirement.parent, Section):
        if not composite_requirement.parent.ng_level:
            resolve_parents(composite_requirement)
        assert composite_requirement.parent.level
        composite_requirement.ng_level = composite_requirement.parent.level + 1

        composite_requirement.parent.ng_sections.append(composite_requirement)
    elif isinstance(composite_requirement.parent, CompositeRequirement):
        if not composite_requirement.parent.ng_level:
            resolve_parents(composite_requirement)
        assert composite_requirement.parent.ng_level
        composite_requirement.ng_level = (
            composite_requirement.parent.ng_level + 1
        )
    elif isinstance(composite_requirement.parent, Document):
        composite_requirement.ng_level = 1
    else:
        raise NotImplementedError


def requirement_obj_processor(requirement, parse_context):
    # Validation
    special_fields = requirement.special_fields
    if special_fields:
        document_config = parse_context.document_config
        if not document_config:
            raise StrictDocSemanticError.missing_special_fields(
                special_fields,
                **get_location(requirement),
            )
        config_special_fields = document_config.special_fields
        if not config_special_fields:
            raise StrictDocSemanticError.missing_special_fields(
                special_fields,
                **get_location(requirement),
            )

        special_field_set = set()
        for special_field in special_fields:
            if (
                special_field.field_name
                not in document_config.special_fields_set
            ):
                raise StrictDocSemanticError.field_is_missing_in_doc_config(
                    special_field.field_name,
                    special_field.field_value,
                    **get_location(requirement),
                )
            special_field_set.add(special_field.field_name)

        for required_special_field in document_config.special_fields_required:
            if required_special_field not in special_field_set:
                raise StrictDocSemanticError.requirement_missing_required_field(
                    required_special_field, **get_location(requirement)
                )

    else:
        document_config = parse_context.document_config
        if document_config:
            if len(document_config.special_fields_required) > 0:
                raise StrictDocSemanticError.requirement_missing_special_fields(
                    document_config.special_fields_required,
                    **get_location(requirement),
                )

    requirement.ng_document_reference = parse_context.document_reference

    if isinstance(requirement.parent, Section):
        assert requirement.parent.level
        requirement.ng_level = requirement.parent.level + 1
    elif isinstance(requirement.parent, CompositeRequirement):
        if not requirement.parent.ng_level:
            resolve_parents(requirement)
        requirement.ng_level = requirement.parent.ng_level + 1
    elif isinstance(requirement.parent, Document):
        requirement.ng_level = 1
    else:
        raise NotImplementedError


def freetext_obj_processor(free_text):
    if isinstance(free_text.parent, Section):
        assert free_text.parent.level
        free_text.ng_level = free_text.parent.level + 1
    elif isinstance(free_text.parent, CompositeRequirement):
        if not free_text.parent.ng_level:
            resolve_parents(free_text)
        free_text.ng_level = free_text.parent.ng_level + 1
    elif isinstance(free_text.parent, Document):
        free_text.ng_level = 1
    else:
        raise NotImplementedError


class ParseContext:
    def __init__(self):
        self.document_reference: DocumentReference = DocumentReference()
        self.document_config: Optional[DocumentConfig] = None


class SDReader:
    def __init__(self):
        self.meta_model = metamodel_from_str(
            STRICTDOC_GRAMMAR, classes=DOCUMENT_MODELS, use_regexp_group=True
        )

    def read(self, input, file_path=None):
        parse_context = ParseContext()

        document_config_processor = partial(
            document_config_obj_processor, parse_context=parse_context
        )

        requirement_processor = partial(
            requirement_obj_processor, parse_context=parse_context
        )
        composite_requirement_processor = partial(
            composite_requirement_obj_processor, parse_context=parse_context
        )

        obj_processors = {
            "DocumentConfig": document_config_processor,
            "Section": section_obj_processor,
            "CompositeRequirement": composite_requirement_processor,
            "Requirement": requirement_processor,
            "FreeText": freetext_obj_processor,
        }

        self.meta_model.register_obj_processors(obj_processors)

        document = self.meta_model.model_from_str(input, file_name=file_path)
        parse_context.document_reference.set_document(document)

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        document._tx_parser = None
        document._tx_attrs = None
        document._tx_metamodel = None
        document._tx_peg_rule = None

        return document

    def read_from_file(self, file_path):
        with open(file_path, "r") as file:
            sdoc_content = file.read()

        try:
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc
        except NotImplementedError as exc:
            traceback.print_exc()
            exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())
            exit(1)
        except Exception as exc:
            print(
                "error: could not parse file: {}.\n{}: {}".format(
                    file_path, exc.__class__.__name__, exc
                )
            )
            # TODO: when --debug is provided
            # traceback.print_exc()
            exit(1)
