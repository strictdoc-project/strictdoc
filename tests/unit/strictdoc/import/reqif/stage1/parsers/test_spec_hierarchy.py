from xml.etree import ElementTree as etree

from strictdoc.imports.reqif.stage1.parsers.spec_hierarchy_parser import (
    ReqIFSpecHierarchyParser,
)


def test_01_nominal_case():
    specification_string = """
<SPEC-HIERARCHY IDENTIFIER="LEVEL_1" LAST-CHANGE="2015-12-14T02:04:51.856+01:00">
  <OBJECT>
    <SPEC-OBJECT-REF>TEST_OBJECT_REF_1</SPEC-OBJECT-REF>
  </OBJECT>
  <CHILDREN>
    <SPEC-HIERARCHY IDENTIFIER="LEVEL_1_1" LAST-CHANGE="2015-12-14T02:04:51.857+01:00">
      <OBJECT>
        <SPEC-OBJECT-REF>TEST_OBJECT_REF_1_1</SPEC-OBJECT-REF>
      </OBJECT>
      <CHILDREN>
        <SPEC-HIERARCHY IDENTIFIER="LEVEL_1_1_1" LAST-CHANGE="2015-12-14T02:04:52.271+01:00">
          <OBJECT>
            <SPEC-OBJECT-REF>TEST_OBJECT_REF_1_1_1</SPEC-OBJECT-REF>
          </OBJECT>
        </SPEC-HIERARCHY>
      </CHILDREN>
    </SPEC-HIERARCHY>
  </CHILDREN>
</SPEC-HIERARCHY>
    """

    specification_xml = etree.fromstring(specification_string)
    specification_1 = ReqIFSpecHierarchyParser.parse(specification_xml)
    assert specification_1.identifier == "LEVEL_1"
    assert specification_1.spec_object == "TEST_OBJECT_REF_1"
    assert specification_1.level == 1
    assert len(specification_1.children) == 1

    specification_1_1 = specification_1.children[0]
    assert specification_1_1.identifier == "LEVEL_1_1"
    assert len(specification_1_1.children) == 1
    assert specification_1_1.level == 2

    specification_1_1_1 = specification_1_1.children[0]
    assert specification_1_1_1.identifier == "LEVEL_1_1_1"
    assert len(specification_1_1_1.children) == 0
    assert specification_1_1_1.level == 3
