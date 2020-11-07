import traceback

from textx import metamodel_from_str

from strictdoc.backend.dsl.grammar import STRICTDOC_GRAMMAR
from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.reference import Reference
from strictdoc.backend.dsl.models.requirement import (
    Requirement, CompositeRequirement, RequirementComment, Body
)
from strictdoc.backend.dsl.models.section import Section, FreeText

DOCUMENT_MODELS = [
    Document,
    RequirementComment,
    Section,
    Requirement,
    CompositeRequirement,
    # Body,
    Reference,
    FreeText
]


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


def composite_requirement_obj_processor(composite_requirement):
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
        composite_requirement.ng_level = composite_requirement.parent.ng_level + 1
    elif isinstance(composite_requirement.parent, Document):
        composite_requirement.ng_level = 1
    else:
        raise NotImplementedError


def requirement_obj_processor(requirement):
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

class SDReader:
    def __init__(self):
        self.meta_model = metamodel_from_str(STRICTDOC_GRAMMAR,
                                             classes=DOCUMENT_MODELS,
                                             use_regexp_group=True)
        obj_processors = {
            'Section': section_obj_processor,
            'CompositeRequirement': composite_requirement_obj_processor,
            'Requirement': requirement_obj_processor,
            'FreeText': freetext_obj_processor
        }

        self.meta_model.register_obj_processors(obj_processors)

    def read(self, input):
        document = self.meta_model.model_from_str(input)
        return document

    def read_from_file(self, file_path):
        with open(file_path, 'r') as file:
            sdoc_content = file.read()

        try:
            sdoc = self.read(sdoc_content)
            return sdoc
        except NotImplementedError as exc:
            traceback.print_exc()
            exit(1)
        except Exception as exc:
            print("error: could not parse file: {}.\n{}: {}".format(file_path, exc.__class__.__name__,  exc))
            traceback.print_exc()
            exit(1)
