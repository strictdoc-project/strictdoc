/**
 * @file TBD
 * @author Stanislav Pankevich, Maryna Balioura <s.pankevich@gmail.com, mettta@gmail.com>
 * @license Apache 2
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: "strictdoc",

  rules: {
    top_node: $ => seq(
      $.DOCUMENT,
      $.EOF,
    ),

    DOCUMENT: $ => choice(
        $._document,
        $.document_error
    ),
    _document: $ => seq(
        $._left_bracket,
        $._document_literal,
        $._right_bracket,
        $._newline_character,
        $._newline_character,
        repeat($.NODE),
        optional($.trailing_end_error),
    ),
    document_error: $ => token.immediate(/./),

    trailing_end_error: $ => /[ \n]+/,
    EOF: $ => seq(token.immediate("%%%"), "\0"),

    _document_literal: $ => choice(
        $.document_literal,
        $.document_literal_error
    ),
    document_literal: $ => "DOCUMENT",
    document_literal_error: $ => /./,

    NODE: $ => choice(
        $._node,
    ),
    _node: $ => seq(
        $._left_bracket,
        $.node_literal,
        $._right_bracket,
        $._newline_character,
        repeat($._NODE_FIELD),
        $._newline_character,
    ),
    node_error: $ => token.immediate(/./),
    node_literal: $ => "NODE",

    _NODE_FIELD: $ => choice(
        $.NODE_FIELD_SINGLELINE, $.NODE_FIELD_MULTILINE
    ),

    NODE_FIELD_SINGLELINE: $ => seq(
        $.node_field_name,
        $._semicolon_character,
        $._whitespace_character,
        $.node_field_singleline_value,
        $._newline_character,
    ),

    NODE_FIELD_MULTILINE: $ => seq(
        $.node_field_name,
        $._semicolon_character,
        $._whitespace_character,
        $.three_arrows_right,
        $._newline_character,
        repeat1($.single_line_string),
        $.three_arrows_left,
        $._newline_character,
    ),

    node_field_name: $ => /[A-Z0-9]+/,
    node_field_singleline_value: $ => /[A-Z0-9]+/,

    three_arrows_right: $ => token.immediate(">>>"),
    three_arrows_left: $ => token.immediate("<<<"),

    single_line_string: $ => seq(token.immediate(/.*/), $._newline_character),

    _left_bracket: $ => choice(
        $.left_bracket,
        $.left_bracket_error
    ),
    left_bracket: $ => token.immediate("["),
    left_bracket_error: $ => /[^\[]/,

    _right_bracket: $ => choice(
        $.right_bracket,
        $.right_bracket_error
    ),
    right_bracket: $ => token.immediate("]"),
    right_bracket_error: $ => /./,

    _semicolon_character: $ => choice(
        $.semicolon_character,
        $.semicolon_character_error
    ),
    semicolon_character: $ => token.immediate(":"),
    semicolon_character_error: $ => token.immediate(/./),

    _whitespace_character: $ => choice(
        $.whitespace_character,
        $.whitespace_character_error
    ),
    whitespace_character: $ => token.immediate(" "),
    whitespace_character_error: $ => token.immediate(/./),

    _newline_character: $ => choice(
        $.newline_character,
        $.newline_character_error
    ),
    newline_character: $ => token.immediate("\n"),
    newline_character_error: $ => token.immediate(/./),
  }
});
