def drop_textx_meta(textx_object):
    textx_object._tx_parser = None  # pylint: disable=protected-access
    textx_object._tx_attrs = None  # pylint: disable=protected-access
    textx_object._tx_metamodel = None  # pylint: disable=protected-access
    textx_object._tx_peg_rule = None  # pylint: disable=protected-access
    textx_object._tx_model_params = None  # pylint: disable=protected-access
