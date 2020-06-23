import re

from collections import OrderedDict

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from strictdoc.backend.rst.rst_parser_shared_state import RSTParserSharedState


class DocumentMetadata:
    def __init__(self):
        self.fields = []

    def has_field(self, field, type):
        for registered_field in self.fields:
            if registered_field['name'] == field and registered_field['type'] == type:
                return True
        else:
            return False

    def __str__(self):
        return 'DocumentMetadata (fields: {})'.format(self.fields)


class DocumentMetadataNode(nodes.General, nodes.Element):
    metadata = None

    def __init__(self, metadata):
        assert metadata
        super(DocumentMetadataNode, self).__init__()
        self.metadata = metadata

    def get_metadata(self):
        return self.metadata


class DocumentMetadataDirective(Directive):
    has_content = True

    option_spec = {
        "fields": directives.unchanged_required
    }

    def run(self):
        meta_information = OrderedDict()

        if not self.options:
            raise RuntimeError("problem with options")

        assert 'fields' in self.options.keys()

        fields_raw = self.options.get("fields", '')
        fields_components = fields_raw.split('\n')

        pattern = re.compile("^\s+|\s*,\s*|\s+$")

        document_metadata = DocumentMetadata()
        for fields_component in fields_components:
            assert fields_component[0:2] == '- '
            fields_component = fields_component[2:]

            key_value_pairs = [x for x in pattern.split(fields_component) if x]

            field_dict = {}

            for key_value_pair in key_value_pairs:
                key_value_components = key_value_pair.split('=')
                assert len(key_value_components) == 2

                field_dict[key_value_components[0]] = key_value_components[1]

            document_metadata.fields.append(field_dict)

        container = DocumentMetadataNode(document_metadata)

        # HACK HACK HACK
        for field in document_metadata.fields:
            RSTParserSharedState.categories_spec[field['name']] = directives.unchanged_required

        return [container]
