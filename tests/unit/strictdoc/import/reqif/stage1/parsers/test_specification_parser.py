from xml.etree import ElementTree as etree

from strictdoc.imports.reqif.stage1.models.reqif_spec_hierarchy import (
    ReqIFSpecHierarchy,
)
from strictdoc.imports.reqif.stage1.parsers.specification_parser import (
    ReqIFSpecificationParser,
)


def test_01_nominal_case():
    specification_string = """
<SPECIFICATION IDENTIFIER="TEST_SPECIFICATION_ID" LAST-CHANGE="2021-10-14T10:11:59.495+02:00" LONG-NAME="Specification Document">
  <VALUES/>
  <TYPE>
    <SPECIFICATION-TYPE-REF>_Z5pghizGEey_QIvU1w5Ozg</SPECIFICATION-TYPE-REF>
  </TYPE>
  <CHILDREN>
    <SPEC-HIERARCHY IDENTIFIER="TEST_SPEC_HIERARCHY" LAST-CHANGE="2021-10-15T09:21:00.153+02:00">
      <OBJECT>
        <SPEC-OBJECT-REF>TEST_OBJECT_REF</SPEC-OBJECT-REF>
      </OBJECT>
    </SPEC-HIERARCHY>
  </CHILDREN>
</SPECIFICATION>
    """

    specification_xml = etree.fromstring(specification_string)
    specification = ReqIFSpecificationParser.parse(specification_xml)
    assert specification.identifier == "TEST_SPECIFICATION_ID"
    assert specification.long_name == "Specification Document"
    assert len(specification.children) == 1

    spec_hierarchy_1 = specification.children[0]
    assert spec_hierarchy_1.identifier == "TEST_SPEC_HIERARCHY"
    assert isinstance(spec_hierarchy_1, ReqIFSpecHierarchy)
    assert spec_hierarchy_1.spec_object == "TEST_OBJECT_REF"
