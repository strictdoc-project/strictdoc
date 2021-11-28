from xml.etree import ElementTree as etree

from strictdoc.imports.reqif.stage1.models.reqif_header import ReqIFHeader
from strictdoc.imports.reqif.stage1.parsers.header_parser import (
    ReqIFHeaderParser,
)


def test_01_title():
    spec_type_string = """
  <THE-HEADER>
    <REQ-IF-HEADER IDENTIFIER="rmf-d59519b5-79a2-4309-8fcb-923f57cc795c">
      <CREATION-TIME>2015-12-14T02:04:51.763+01:00</CREATION-TIME>
      <REQ-IF-TOOL-ID>fmStudio (http://formalmind.com/studio)</REQ-IF-TOOL-ID>
      <REQ-IF-VERSION>1.0</REQ-IF-VERSION>
      <SOURCE-TOOL-ID>subset026-writer</SOURCE-TOOL-ID>
      <TITLE>Subset026</TITLE>
    </REQ-IF-HEADER>
  </THE-HEADER>
    """
    xml_header = etree.fromstring(spec_type_string)

    header = ReqIFHeaderParser.parse(xml_header)
    assert isinstance(header, ReqIFHeader)
    assert header.title == "Subset026"
