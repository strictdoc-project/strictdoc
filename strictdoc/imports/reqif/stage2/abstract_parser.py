from strictdoc.imports.reqif.stage1.models.reqif_bundle import ReqIFBundle


class AbstractReqIFStage2Parser:
    def parse_reqif(self, reqif_bundle: ReqIFBundle):
        raise NotImplementedError
