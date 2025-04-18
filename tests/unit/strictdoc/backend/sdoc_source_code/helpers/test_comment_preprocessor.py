# The tests in this file has strings with whitespace that must not be linted.
# ruff: noqa: W291,W293
from strictdoc.backend.sdoc_source_code.helpers.comment_preprocessor import (
    preprocess_source_code_comment,
)


def test_001_doxygen_slashes_and_stars():
    source_input = """\
/**
 * @relation(REQ-1, scope=function)
 */
"""

    preprocessed_comment = preprocess_source_code_comment(source_input)

    # Note: There are invisible characters.
    assert (
        preprocessed_comment
        == """\
   
   @relation(REQ-1, scope=function)
   
"""
    )


def test_001_doxygen_three_slashes():
    source_input = """\
///
/// @relation(REQ-1, scope=function)
///
"""

    preprocessed_comment = preprocess_source_code_comment(source_input)

    # Note: There are invisible characters.
    assert (
        preprocessed_comment
        == """\
   
    @relation(REQ-1, scope=function)
   
"""
    )


def test_003_doxygen_two_slashes():
    source_input = """\
//
// @relation(REQ-1, scope=function)
//
"""

    preprocessed_comment = preprocess_source_code_comment(source_input)

    # Note: There are invisible characters.
    assert (
        preprocessed_comment
        == """\
  
   @relation(REQ-1, scope=function)
  
"""
    )


def test_004_python():
    source_input = """\
#
# @relation(REQ-1, scope=function)
#
"""

    preprocessed_comment = preprocess_source_code_comment(source_input)

    # Note: There are invisible characters.
    assert (
        preprocessed_comment
        == """\
 
  @relation(REQ-1, scope=function)
 
"""
    )
