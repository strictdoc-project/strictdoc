def drop_textx_meta(textx_object):
    textx_object._tx_parser = None
    textx_object._tx_attrs = None
    textx_object._tx_metamodel = None
    textx_object._tx_peg_rule = None
    textx_object._tx_model_params = None
