import io
import sys
from collections import defaultdict
from typing import List

from lxml import etree

from strictdoc.imports.reqif.stage1.models.reqif_bundle import ReqIFBundle
from strictdoc.imports.reqif.stage1.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
)
from strictdoc.imports.reqif.stage1.models.reqif_specification import (
    ReqIFSpecification,
)
from strictdoc.imports.reqif.stage1.parsers.data_type_parser import (
    DataTypeParser,
)
from strictdoc.imports.reqif.stage1.parsers.spec_object_parser import (
    SpecObjectParser,
)
from strictdoc.imports.reqif.stage1.parsers.spec_object_type_parser import (
    SpecObjectTypeParser,
)
from strictdoc.imports.reqif.stage1.parsers.spec_relation_parser import (
    SpecRelationParser,
)
from strictdoc.imports.reqif.stage1.parsers.specification_parser import (
    ReqIFSpecificationParser,
)


class ReqIFStage1Parser:
    @staticmethod
    def parse(input_path):
        # Import file.
        with open(input_path, "r", encoding="UTF-8") as file:
            content = file.read()
        try:
            # Parse XML.
            # https://github.com/eerohele/sublime-lxml/issues/5#issuecomment-209781719
            parsed_xml = etree.parse(io.BytesIO(bytes(content, "UTF-8")))
            parsed_xml = ReqIFStage1Parser.strip_namespace_from_xml(parsed_xml)
            xml_reqif = parsed_xml.getroot()
        except Exception as exception:
            # TODO: handle
            print(f"error: problem parsing file: {exception}")
            sys.exit(1)

        # Build ReqIF bundle.
        reqif_bundle = ReqIFStage1Parser.parse_reqif(xml_reqif)
        return reqif_bundle

    @staticmethod
    def parse_reqif(xml_reqif) -> ReqIFBundle:
        # ReqIF element naming convention: element_xyz where xyz is the name of
        # the reqif(xml) tag. Dashes are turned into underscores.
        if xml_reqif is None:
            raise NotImplementedError
        if xml_reqif.tag != "REQ-IF":
            raise NotImplementedError

        if len(xml_reqif) == 0:
            return ReqIFBundle.create_empty()

        # Getting all structural elements from the ReqIF tree.
        # TODO: The header, containing metadata about the document.
        xml_the_header = xml_reqif.find("THE-HEADER")
        if xml_the_header is None:
            return ReqIFBundle.create_empty()

        # Core content, contains req-if-content which contains all the actual
        # content.
        xml_core_content = xml_reqif.find("CORE-CONTENT")
        assert xml_core_content is not None

        # TODO: Tool extensions contains information specific to the tool used
        # to create the ReqIF file.
        # element_tool_extensions = xml_reqif.find(
        #     "TOOL-EXTENSIONS", namespace_dict
        # )

        # req-if-content contains the requirements and structure
        xml_req_if_content = xml_core_content.find("REQ-IF-CONTENT")
        assert xml_req_if_content is not None

        xml_datatypes = xml_req_if_content.find("DATATYPES")
        assert xml_datatypes is not None

        data_types = []
        data_types_lookup = {}
        for xml_data_type in list(xml_datatypes):
            data_type = DataTypeParser.parse(xml_data_type)
            data_types.append(data_type)
            data_types_lookup[data_type.identifier] = data_type

        # Spec types contains the spectypes, basically blueprints for spec
        # objects. Spec types use datatypes to define the kind of information
        # stored.
        xml_spec_types = xml_req_if_content.find("SPEC-TYPES")
        assert xml_spec_types is not None

        # spec-objects contains specobjects, which are the actual requirements.
        # every specobject must have a spec_type which defines its structure
        xml_spec_objects = xml_req_if_content.find("SPEC-OBJECTS")
        assert xml_spec_objects is not None

        # Spec-relations contains arbitrarily defined relations between spec
        # objects. These relations may be grouped into relation groups which
        # have user-defined meaning.
        xml_spec_relations = xml_req_if_content.find("SPEC-RELATIONS")
        xml_spec_relations = (
            xml_spec_relations if xml_spec_relations is not None else []
        )

        # Specifications contains one or more specification elements.
        # Each specification element contains a tree of spec-hierarchy elements
        # that represents the basic structure of the document each
        # spec-hierarchy element contains a spec-object.
        xml_specifications = xml_req_if_content.find("SPECIFICATIONS")
        assert xml_specifications is not None

        # Note: the other objects have to be present in a proper ReqIF file as
        # well, but these two are absolutely required.
        if xml_spec_types is None or xml_spec_objects is None:
            raise NotImplementedError

        spec_object_types = []
        for xml_spec_object_type_xml in list(xml_spec_types):
            if isinstance(xml_spec_object_type_xml, ReqIFSpecObjectType):
                spec_type = SpecObjectTypeParser.parse(xml_spec_object_type_xml)
                spec_object_types.append(spec_type)

        specifications: List[ReqIFSpecification] = []
        if xml_specifications is not None:
            for xml_specification in xml_specifications:
                specification = ReqIFSpecificationParser.parse(
                    xml_specification
                )
                specifications.append(specification)

        spec_relations = []
        spec_relations_parent_lookup = defaultdict(list)
        for xml_spec_relation in xml_spec_relations:
            spec_relation = SpecRelationParser.parse(xml_spec_relation)
            spec_relations.append(spec_relation)
            spec_relations_parent_lookup[spec_relation.source].append(
                spec_relation.target
            )

        spec_objects = []
        spec_objects_lookup = {}
        for xml_spec_object in xml_spec_objects:
            spec_object = SpecObjectParser.parse(xml_spec_object)
            spec_objects.append(spec_object)
            spec_objects_lookup[spec_object.identifier] = spec_object

        return ReqIFBundle(
            data_types=data_types,
            spec_objects=spec_objects,
            spec_objects_lookup=spec_objects_lookup,
            spec_relations=spec_relations,
            spec_relations_parent_lookup=spec_relations_parent_lookup,
            specifications=specifications,
        )

    @staticmethod
    def strip_namespace_from_xml(root_xml):
        for elem in root_xml.getiterator():
            # Remove a namespace URI in the element's name
            elem.tag = etree.QName(elem).localname

        # Remove unused namespace declarations
        etree.cleanup_namespaces(root_xml)
        return root_xml
