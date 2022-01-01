from reqif.reqif_bundle import ReqIFBundle


class AbstractReqIFStage2Parser:
    def parse_reqif(self, reqif_bundle: ReqIFBundle):
        raise NotImplementedError
