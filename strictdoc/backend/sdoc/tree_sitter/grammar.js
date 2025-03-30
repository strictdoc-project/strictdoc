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
        optional($.trailing_end_error),
    ),
    document_error: $ => token.immediate(/./),

    trailing_end_error: $ => /[ \n]+/,
    EOF: $ => "\0",

    _document_literal: $ => choice(
        $.document_literal,
        $.document_literal_error
    ),
    document_literal: $ => "DOCUMENT",
    document_literal_error: $ => /./,

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

    _newline_character: $ => choice(
        $.newline_character,
        $.newline_character_error
    ),
    newline_character: $ => token.immediate("\n"),
    newline_character_error: $ => token.immediate(/./),
  }
});
