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
    // TODO: add the actual grammar rules
    source_file: $ => "hello"
  }
});
