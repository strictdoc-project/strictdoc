from strictdoc.imports.reqif.stage1.models.reqif_header import ReqIFHeader


class ReqIFHeaderParser:
    @staticmethod
    def parse(xml_header) -> ReqIFHeader:
        assert xml_header.tag == "THE-HEADER"

        xml_reqif_header = xml_header.find("REQ-IF-HEADER")
        if not xml_reqif_header:
            raise NotImplementedError(xml_header)

        xml_title = xml_reqif_header.find("TITLE")
        title = xml_title.text

        return ReqIFHeader(title=title)
