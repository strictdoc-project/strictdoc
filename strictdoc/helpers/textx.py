from typing import Any

from textx import get_model


def drop_textx_meta(textx_object: Any) -> None:
    textx_object._tx_parser = None  # pylint: disable=protected-access
    textx_object._tx_attrs = None  # pylint: disable=protected-access
    textx_object._tx_metamodel = None  # pylint: disable=protected-access
    textx_object._tx_peg_rule = None  # pylint: disable=protected-access
    textx_object._tx_model_params = None  # pylint: disable=protected-access


def preserve_source_location_data(parsed_object: Any) -> None:
    """
    Saving the source location information in the parsed object.
    """
    the_model = get_model(parsed_object)
    line_start, col_start = the_model._tx_parser.pos_to_linecol(
        parsed_object._tx_position
    )
    line_end, col_end = the_model._tx_parser.pos_to_linecol(
        parsed_object._tx_position_end
    )
    parsed_object.ng_line_start = line_start
    parsed_object.ng_line_end = line_end
    parsed_object.ng_col_start = col_start
    parsed_object.ng_col_end = col_end
    parsed_object.ng_byte_start = parsed_object._tx_position
    parsed_object.ng_byte_end = parsed_object._tx_position_end
