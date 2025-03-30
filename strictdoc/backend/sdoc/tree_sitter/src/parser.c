#include "tree_sitter/parser.h"

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#endif

#define LANGUAGE_VERSION 14
#define STATE_COUNT 51
#define LARGE_STATE_COUNT 2
#define SYMBOL_COUNT 45
#define ALIAS_COUNT 0
#define TOKEN_COUNT 18
#define EXTERNAL_TOKEN_COUNT 0
#define FIELD_COUNT 0
#define MAX_ALIAS_SEQUENCE_LENGTH 8
#define PRODUCTION_ID_COUNT 1

enum ts_symbol_identifiers {
  aux_sym_document_error_token1 = 1,
  sym_trailing_end_error = 2,
  anon_sym_PERCENT_PERCENT_PERCENT = 3,
  anon_sym_NULL = 4,
  sym_document_literal = 5,
  aux_sym_document_literal_error_token1 = 6,
  sym_node_literal = 7,
  aux_sym_node_field_name_token1 = 8,
  sym_three_arrows_right = 9,
  sym_three_arrows_left = 10,
  aux_sym_single_line_string_token1 = 11,
  sym_left_bracket = 12,
  sym_left_bracket_error = 13,
  sym_right_bracket = 14,
  sym_semicolon_character = 15,
  sym_whitespace_character = 16,
  sym_newline_character = 17,
  sym_top_node = 18,
  sym_DOCUMENT = 19,
  sym__document = 20,
  sym_document_error = 21,
  sym_EOF = 22,
  sym__document_literal = 23,
  sym_document_literal_error = 24,
  sym_NODE = 25,
  sym__node = 26,
  sym__NODE_FIELD = 27,
  sym_NODE_FIELD_SINGLELINE = 28,
  sym_NODE_FIELD_MULTILINE = 29,
  sym_node_field_name = 30,
  sym_node_field_singleline_value = 31,
  sym_single_line_string = 32,
  sym__left_bracket = 33,
  sym__right_bracket = 34,
  sym_right_bracket_error = 35,
  sym__semicolon_character = 36,
  sym_semicolon_character_error = 37,
  sym__whitespace_character = 38,
  sym_whitespace_character_error = 39,
  sym__newline_character = 40,
  sym_newline_character_error = 41,
  aux_sym__document_repeat1 = 42,
  aux_sym__node_repeat1 = 43,
  aux_sym_NODE_FIELD_MULTILINE_repeat1 = 44,
};

static const char * const ts_symbol_names[] = {
  [ts_builtin_sym_end] = "end",
  [aux_sym_document_error_token1] = "document_error_token1",
  [sym_trailing_end_error] = "trailing_end_error",
  [anon_sym_PERCENT_PERCENT_PERCENT] = "%%%",
  [anon_sym_NULL] = "\0",
  [sym_document_literal] = "document_literal",
  [aux_sym_document_literal_error_token1] = "document_literal_error_token1",
  [sym_node_literal] = "node_literal",
  [aux_sym_node_field_name_token1] = "node_field_name_token1",
  [sym_three_arrows_right] = "three_arrows_right",
  [sym_three_arrows_left] = "three_arrows_left",
  [aux_sym_single_line_string_token1] = "single_line_string_token1",
  [sym_left_bracket] = "left_bracket",
  [sym_left_bracket_error] = "left_bracket_error",
  [sym_right_bracket] = "right_bracket",
  [sym_semicolon_character] = "semicolon_character",
  [sym_whitespace_character] = "whitespace_character",
  [sym_newline_character] = "newline_character",
  [sym_top_node] = "top_node",
  [sym_DOCUMENT] = "DOCUMENT",
  [sym__document] = "_document",
  [sym_document_error] = "document_error",
  [sym_EOF] = "EOF",
  [sym__document_literal] = "_document_literal",
  [sym_document_literal_error] = "document_literal_error",
  [sym_NODE] = "NODE",
  [sym__node] = "_node",
  [sym__NODE_FIELD] = "_NODE_FIELD",
  [sym_NODE_FIELD_SINGLELINE] = "NODE_FIELD_SINGLELINE",
  [sym_NODE_FIELD_MULTILINE] = "NODE_FIELD_MULTILINE",
  [sym_node_field_name] = "node_field_name",
  [sym_node_field_singleline_value] = "node_field_singleline_value",
  [sym_single_line_string] = "single_line_string",
  [sym__left_bracket] = "_left_bracket",
  [sym__right_bracket] = "_right_bracket",
  [sym_right_bracket_error] = "right_bracket_error",
  [sym__semicolon_character] = "_semicolon_character",
  [sym_semicolon_character_error] = "semicolon_character_error",
  [sym__whitespace_character] = "_whitespace_character",
  [sym_whitespace_character_error] = "whitespace_character_error",
  [sym__newline_character] = "_newline_character",
  [sym_newline_character_error] = "newline_character_error",
  [aux_sym__document_repeat1] = "_document_repeat1",
  [aux_sym__node_repeat1] = "_node_repeat1",
  [aux_sym_NODE_FIELD_MULTILINE_repeat1] = "NODE_FIELD_MULTILINE_repeat1",
};

static const TSSymbol ts_symbol_map[] = {
  [ts_builtin_sym_end] = ts_builtin_sym_end,
  [aux_sym_document_error_token1] = aux_sym_document_error_token1,
  [sym_trailing_end_error] = sym_trailing_end_error,
  [anon_sym_PERCENT_PERCENT_PERCENT] = anon_sym_PERCENT_PERCENT_PERCENT,
  [anon_sym_NULL] = anon_sym_NULL,
  [sym_document_literal] = sym_document_literal,
  [aux_sym_document_literal_error_token1] = aux_sym_document_literal_error_token1,
  [sym_node_literal] = sym_node_literal,
  [aux_sym_node_field_name_token1] = aux_sym_node_field_name_token1,
  [sym_three_arrows_right] = sym_three_arrows_right,
  [sym_three_arrows_left] = sym_three_arrows_left,
  [aux_sym_single_line_string_token1] = aux_sym_single_line_string_token1,
  [sym_left_bracket] = sym_left_bracket,
  [sym_left_bracket_error] = sym_left_bracket_error,
  [sym_right_bracket] = sym_right_bracket,
  [sym_semicolon_character] = sym_semicolon_character,
  [sym_whitespace_character] = sym_whitespace_character,
  [sym_newline_character] = sym_newline_character,
  [sym_top_node] = sym_top_node,
  [sym_DOCUMENT] = sym_DOCUMENT,
  [sym__document] = sym__document,
  [sym_document_error] = sym_document_error,
  [sym_EOF] = sym_EOF,
  [sym__document_literal] = sym__document_literal,
  [sym_document_literal_error] = sym_document_literal_error,
  [sym_NODE] = sym_NODE,
  [sym__node] = sym__node,
  [sym__NODE_FIELD] = sym__NODE_FIELD,
  [sym_NODE_FIELD_SINGLELINE] = sym_NODE_FIELD_SINGLELINE,
  [sym_NODE_FIELD_MULTILINE] = sym_NODE_FIELD_MULTILINE,
  [sym_node_field_name] = sym_node_field_name,
  [sym_node_field_singleline_value] = sym_node_field_singleline_value,
  [sym_single_line_string] = sym_single_line_string,
  [sym__left_bracket] = sym__left_bracket,
  [sym__right_bracket] = sym__right_bracket,
  [sym_right_bracket_error] = sym_right_bracket_error,
  [sym__semicolon_character] = sym__semicolon_character,
  [sym_semicolon_character_error] = sym_semicolon_character_error,
  [sym__whitespace_character] = sym__whitespace_character,
  [sym_whitespace_character_error] = sym_whitespace_character_error,
  [sym__newline_character] = sym__newline_character,
  [sym_newline_character_error] = sym_newline_character_error,
  [aux_sym__document_repeat1] = aux_sym__document_repeat1,
  [aux_sym__node_repeat1] = aux_sym__node_repeat1,
  [aux_sym_NODE_FIELD_MULTILINE_repeat1] = aux_sym_NODE_FIELD_MULTILINE_repeat1,
};

static const TSSymbolMetadata ts_symbol_metadata[] = {
  [ts_builtin_sym_end] = {
    .visible = false,
    .named = true,
  },
  [aux_sym_document_error_token1] = {
    .visible = false,
    .named = false,
  },
  [sym_trailing_end_error] = {
    .visible = true,
    .named = true,
  },
  [anon_sym_PERCENT_PERCENT_PERCENT] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_NULL] = {
    .visible = true,
    .named = false,
  },
  [sym_document_literal] = {
    .visible = true,
    .named = true,
  },
  [aux_sym_document_literal_error_token1] = {
    .visible = false,
    .named = false,
  },
  [sym_node_literal] = {
    .visible = true,
    .named = true,
  },
  [aux_sym_node_field_name_token1] = {
    .visible = false,
    .named = false,
  },
  [sym_three_arrows_right] = {
    .visible = true,
    .named = true,
  },
  [sym_three_arrows_left] = {
    .visible = true,
    .named = true,
  },
  [aux_sym_single_line_string_token1] = {
    .visible = false,
    .named = false,
  },
  [sym_left_bracket] = {
    .visible = true,
    .named = true,
  },
  [sym_left_bracket_error] = {
    .visible = true,
    .named = true,
  },
  [sym_right_bracket] = {
    .visible = true,
    .named = true,
  },
  [sym_semicolon_character] = {
    .visible = true,
    .named = true,
  },
  [sym_whitespace_character] = {
    .visible = true,
    .named = true,
  },
  [sym_newline_character] = {
    .visible = true,
    .named = true,
  },
  [sym_top_node] = {
    .visible = true,
    .named = true,
  },
  [sym_DOCUMENT] = {
    .visible = true,
    .named = true,
  },
  [sym__document] = {
    .visible = false,
    .named = true,
  },
  [sym_document_error] = {
    .visible = true,
    .named = true,
  },
  [sym_EOF] = {
    .visible = true,
    .named = true,
  },
  [sym__document_literal] = {
    .visible = false,
    .named = true,
  },
  [sym_document_literal_error] = {
    .visible = true,
    .named = true,
  },
  [sym_NODE] = {
    .visible = true,
    .named = true,
  },
  [sym__node] = {
    .visible = false,
    .named = true,
  },
  [sym__NODE_FIELD] = {
    .visible = false,
    .named = true,
  },
  [sym_NODE_FIELD_SINGLELINE] = {
    .visible = true,
    .named = true,
  },
  [sym_NODE_FIELD_MULTILINE] = {
    .visible = true,
    .named = true,
  },
  [sym_node_field_name] = {
    .visible = true,
    .named = true,
  },
  [sym_node_field_singleline_value] = {
    .visible = true,
    .named = true,
  },
  [sym_single_line_string] = {
    .visible = true,
    .named = true,
  },
  [sym__left_bracket] = {
    .visible = false,
    .named = true,
  },
  [sym__right_bracket] = {
    .visible = false,
    .named = true,
  },
  [sym_right_bracket_error] = {
    .visible = true,
    .named = true,
  },
  [sym__semicolon_character] = {
    .visible = false,
    .named = true,
  },
  [sym_semicolon_character_error] = {
    .visible = true,
    .named = true,
  },
  [sym__whitespace_character] = {
    .visible = false,
    .named = true,
  },
  [sym_whitespace_character_error] = {
    .visible = true,
    .named = true,
  },
  [sym__newline_character] = {
    .visible = false,
    .named = true,
  },
  [sym_newline_character_error] = {
    .visible = true,
    .named = true,
  },
  [aux_sym__document_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym__node_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_NODE_FIELD_MULTILINE_repeat1] = {
    .visible = false,
    .named = false,
  },
};

static const TSSymbol ts_alias_sequences[PRODUCTION_ID_COUNT][MAX_ALIAS_SEQUENCE_LENGTH] = {
  [0] = {0},
};

static const uint16_t ts_non_terminal_alias_map[] = {
  0,
};

static const TSStateId ts_primary_state_ids[STATE_COUNT] = {
  [0] = 0,
  [1] = 1,
  [2] = 2,
  [3] = 3,
  [4] = 4,
  [5] = 5,
  [6] = 6,
  [7] = 7,
  [8] = 8,
  [9] = 9,
  [10] = 10,
  [11] = 11,
  [12] = 12,
  [13] = 13,
  [14] = 14,
  [15] = 15,
  [16] = 16,
  [17] = 17,
  [18] = 18,
  [19] = 19,
  [20] = 20,
  [21] = 21,
  [22] = 22,
  [23] = 23,
  [24] = 24,
  [25] = 25,
  [26] = 26,
  [27] = 27,
  [28] = 28,
  [29] = 29,
  [30] = 24,
  [31] = 31,
  [32] = 32,
  [33] = 33,
  [34] = 34,
  [35] = 35,
  [36] = 24,
  [37] = 37,
  [38] = 38,
  [39] = 39,
  [40] = 24,
  [41] = 41,
  [42] = 42,
  [43] = 43,
  [44] = 44,
  [45] = 45,
  [46] = 46,
  [47] = 47,
  [48] = 48,
  [49] = 49,
  [50] = 24,
};

static bool ts_lex(TSLexer *lexer, TSStateId state) {
  START_LEXER();
  eof = lexer->eof(lexer);
  switch (state) {
    case 0:
      if (eof) ADVANCE(29);
      ADVANCE_MAP(
        0, 34,
        '%', 10,
        ':', 55,
        '<', 13,
        '>', 16,
        'D', 23,
        'N', 24,
        '[', 49,
        ']', 54,
      );
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(28);
      END_STATE();
    case 1:
      if (lookahead == '\n') ADVANCE(53);
      if (lookahead == '[') ADVANCE(49);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(30);
      if (lookahead != 0) ADVANCE(30);
      END_STATE();
    case 2:
      if (lookahead == '\n') ADVANCE(57);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(30);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(31);
      if (lookahead != 0) ADVANCE(30);
      END_STATE();
    case 3:
      if (lookahead == '\n') ADVANCE(57);
      if (lookahead != 0) ADVANCE(30);
      END_STATE();
    case 4:
      if (lookahead == '\n') SKIP(5);
      if (lookahead == ']') ADVANCE(54);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(39);
      if (lookahead != 0) ADVANCE(36);
      END_STATE();
    case 5:
      if (lookahead == '\n') SKIP(5);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(39);
      if (lookahead != 0) ADVANCE(36);
      END_STATE();
    case 6:
      if (lookahead == '\n') SKIP(6);
      if (lookahead == 'D') ADVANCE(38);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(37);
      if (lookahead != 0) ADVANCE(36);
      END_STATE();
    case 7:
      if (lookahead == ' ') ADVANCE(56);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(30);
      END_STATE();
    case 8:
      if (lookahead == '%') ADVANCE(33);
      END_STATE();
    case 9:
      if (lookahead == '%') ADVANCE(51);
      if (lookahead == '[') ADVANCE(49);
      if (lookahead == '\n' ||
          lookahead == ' ') ADVANCE(32);
      if (('\t' <= lookahead && lookahead <= '\r')) ADVANCE(52);
      if (lookahead != 0) ADVANCE(50);
      END_STATE();
    case 10:
      if (lookahead == '%') ADVANCE(8);
      END_STATE();
    case 11:
      if (lookahead == ':') ADVANCE(55);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(30);
      END_STATE();
    case 12:
      if (lookahead == '<') ADVANCE(43);
      END_STATE();
    case 13:
      if (lookahead == '<') ADVANCE(12);
      END_STATE();
    case 14:
      if (lookahead == '>') ADVANCE(16);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(27);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(41);
      END_STATE();
    case 15:
      if (lookahead == '>') ADVANCE(42);
      END_STATE();
    case 16:
      if (lookahead == '>') ADVANCE(15);
      END_STATE();
    case 17:
      if (lookahead == 'C') ADVANCE(26);
      END_STATE();
    case 18:
      if (lookahead == 'D') ADVANCE(19);
      END_STATE();
    case 19:
      if (lookahead == 'E') ADVANCE(40);
      END_STATE();
    case 20:
      if (lookahead == 'E') ADVANCE(22);
      END_STATE();
    case 21:
      if (lookahead == 'M') ADVANCE(20);
      END_STATE();
    case 22:
      if (lookahead == 'N') ADVANCE(25);
      END_STATE();
    case 23:
      if (lookahead == 'O') ADVANCE(17);
      END_STATE();
    case 24:
      if (lookahead == 'O') ADVANCE(18);
      END_STATE();
    case 25:
      if (lookahead == 'T') ADVANCE(35);
      END_STATE();
    case 26:
      if (lookahead == 'U') ADVANCE(21);
      END_STATE();
    case 27:
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(27);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(41);
      END_STATE();
    case 28:
      if (eof) ADVANCE(29);
      if ((!eof && lookahead == 00)) ADVANCE(34);
      if (lookahead == 'D') ADVANCE(23);
      if (lookahead == 'N') ADVANCE(24);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(28);
      END_STATE();
    case 29:
      ACCEPT_TOKEN(ts_builtin_sym_end);
      END_STATE();
    case 30:
      ACCEPT_TOKEN(aux_sym_document_error_token1);
      END_STATE();
    case 31:
      ACCEPT_TOKEN(aux_sym_document_error_token1);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(41);
      END_STATE();
    case 32:
      ACCEPT_TOKEN(sym_trailing_end_error);
      if (lookahead == '\n' ||
          lookahead == ' ') ADVANCE(32);
      if (('\t' <= lookahead && lookahead <= '\r')) ADVANCE(52);
      END_STATE();
    case 33:
      ACCEPT_TOKEN(anon_sym_PERCENT_PERCENT_PERCENT);
      END_STATE();
    case 34:
      ACCEPT_TOKEN(anon_sym_NULL);
      END_STATE();
    case 35:
      ACCEPT_TOKEN(sym_document_literal);
      END_STATE();
    case 36:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      END_STATE();
    case 37:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      if (lookahead == 'D') ADVANCE(38);
      if (lookahead == '\t' ||
          (0x0b <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(37);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead)) ADVANCE(36);
      END_STATE();
    case 38:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      if (lookahead == 'O') ADVANCE(17);
      END_STATE();
    case 39:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      if (lookahead == '\t' ||
          (0x0b <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(39);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead)) ADVANCE(36);
      END_STATE();
    case 40:
      ACCEPT_TOKEN(sym_node_literal);
      END_STATE();
    case 41:
      ACCEPT_TOKEN(aux_sym_node_field_name_token1);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(41);
      END_STATE();
    case 42:
      ACCEPT_TOKEN(sym_three_arrows_right);
      END_STATE();
    case 43:
      ACCEPT_TOKEN(sym_three_arrows_left);
      END_STATE();
    case 44:
      ACCEPT_TOKEN(sym_three_arrows_left);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(48);
      END_STATE();
    case 45:
      ACCEPT_TOKEN(aux_sym_single_line_string_token1);
      if (lookahead == '<') ADVANCE(44);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(48);
      END_STATE();
    case 46:
      ACCEPT_TOKEN(aux_sym_single_line_string_token1);
      if (lookahead == '<') ADVANCE(45);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(48);
      END_STATE();
    case 47:
      ACCEPT_TOKEN(aux_sym_single_line_string_token1);
      if (lookahead == '<') ADVANCE(46);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(48);
      END_STATE();
    case 48:
      ACCEPT_TOKEN(aux_sym_single_line_string_token1);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(48);
      END_STATE();
    case 49:
      ACCEPT_TOKEN(sym_left_bracket);
      END_STATE();
    case 50:
      ACCEPT_TOKEN(sym_left_bracket_error);
      END_STATE();
    case 51:
      ACCEPT_TOKEN(sym_left_bracket_error);
      if (lookahead == '%') ADVANCE(8);
      END_STATE();
    case 52:
      ACCEPT_TOKEN(sym_left_bracket_error);
      if (lookahead == '\n' ||
          lookahead == ' ') ADVANCE(32);
      if (('\t' <= lookahead && lookahead <= '\r')) ADVANCE(52);
      if (lookahead != 0 &&
          lookahead != '[') ADVANCE(50);
      END_STATE();
    case 53:
      ACCEPT_TOKEN(sym_left_bracket_error);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(53);
      if (lookahead != 0 &&
          lookahead != '[') ADVANCE(50);
      END_STATE();
    case 54:
      ACCEPT_TOKEN(sym_right_bracket);
      END_STATE();
    case 55:
      ACCEPT_TOKEN(sym_semicolon_character);
      END_STATE();
    case 56:
      ACCEPT_TOKEN(sym_whitespace_character);
      END_STATE();
    case 57:
      ACCEPT_TOKEN(sym_newline_character);
      END_STATE();
    default:
      return false;
  }
}

static const TSLexMode ts_lex_modes[STATE_COUNT] = {
  [0] = {.lex_state = 0},
  [1] = {.lex_state = 1},
  [2] = {.lex_state = 2},
  [3] = {.lex_state = 2},
  [4] = {.lex_state = 9},
  [5] = {.lex_state = 9},
  [6] = {.lex_state = 9},
  [7] = {.lex_state = 2},
  [8] = {.lex_state = 47},
  [9] = {.lex_state = 4},
  [10] = {.lex_state = 3},
  [11] = {.lex_state = 3},
  [12] = {.lex_state = 9},
  [13] = {.lex_state = 4},
  [14] = {.lex_state = 3},
  [15] = {.lex_state = 11},
  [16] = {.lex_state = 9},
  [17] = {.lex_state = 7},
  [18] = {.lex_state = 9},
  [19] = {.lex_state = 3},
  [20] = {.lex_state = 3},
  [21] = {.lex_state = 3},
  [22] = {.lex_state = 3},
  [23] = {.lex_state = 47},
  [24] = {.lex_state = 9},
  [25] = {.lex_state = 6},
  [26] = {.lex_state = 14},
  [27] = {.lex_state = 48},
  [28] = {.lex_state = 2},
  [29] = {.lex_state = 2},
  [30] = {.lex_state = 2},
  [31] = {.lex_state = 11},
  [32] = {.lex_state = 4},
  [33] = {.lex_state = 7},
  [34] = {.lex_state = 14},
  [35] = {.lex_state = 3},
  [36] = {.lex_state = 3},
  [37] = {.lex_state = 47},
  [38] = {.lex_state = 0},
  [39] = {.lex_state = 3},
  [40] = {.lex_state = 47},
  [41] = {.lex_state = 0},
  [42] = {.lex_state = 0},
  [43] = {.lex_state = 0},
  [44] = {.lex_state = 0},
  [45] = {.lex_state = 0},
  [46] = {.lex_state = 0},
  [47] = {.lex_state = 0},
  [48] = {.lex_state = 0},
  [49] = {.lex_state = 0},
  [50] = {.lex_state = 48},
};

static const uint16_t ts_parse_table[LARGE_STATE_COUNT][SYMBOL_COUNT] = {
  [0] = {
    [ts_builtin_sym_end] = ACTIONS(1),
    [anon_sym_PERCENT_PERCENT_PERCENT] = ACTIONS(1),
    [anon_sym_NULL] = ACTIONS(1),
    [sym_document_literal] = ACTIONS(1),
    [sym_node_literal] = ACTIONS(1),
    [sym_three_arrows_right] = ACTIONS(1),
    [sym_three_arrows_left] = ACTIONS(1),
    [sym_left_bracket] = ACTIONS(1),
    [sym_right_bracket] = ACTIONS(1),
    [sym_semicolon_character] = ACTIONS(1),
  },
  [1] = {
    [sym_top_node] = STATE(46),
    [sym_DOCUMENT] = STATE(38),
    [sym__document] = STATE(48),
    [sym_document_error] = STATE(48),
    [sym__left_bracket] = STATE(25),
    [aux_sym_document_error_token1] = ACTIONS(3),
    [sym_left_bracket] = ACTIONS(5),
    [sym_left_bracket_error] = ACTIONS(7),
  },
};

static const uint16_t ts_small_parse_table[] = {
  [0] = 6,
    ACTIONS(9), 1,
      aux_sym_document_error_token1,
    ACTIONS(11), 1,
      aux_sym_node_field_name_token1,
    ACTIONS(13), 1,
      sym_newline_character,
    STATE(15), 1,
      sym_node_field_name,
    STATE(16), 2,
      sym__newline_character,
      sym_newline_character_error,
    STATE(3), 4,
      sym__NODE_FIELD,
      sym_NODE_FIELD_SINGLELINE,
      sym_NODE_FIELD_MULTILINE,
      aux_sym__node_repeat1,
  [23] = 6,
    ACTIONS(9), 1,
      aux_sym_document_error_token1,
    ACTIONS(11), 1,
      aux_sym_node_field_name_token1,
    ACTIONS(15), 1,
      sym_newline_character,
    STATE(15), 1,
      sym_node_field_name,
    STATE(18), 2,
      sym__newline_character,
      sym_newline_character_error,
    STATE(7), 4,
      sym__NODE_FIELD,
      sym_NODE_FIELD_SINGLELINE,
      sym_NODE_FIELD_MULTILINE,
      aux_sym__node_repeat1,
  [46] = 7,
    ACTIONS(17), 1,
      sym_trailing_end_error,
    ACTIONS(19), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
    ACTIONS(21), 1,
      sym_left_bracket,
    ACTIONS(23), 1,
      sym_left_bracket_error,
    STATE(12), 1,
      sym__node,
    STATE(43), 1,
      sym__left_bracket,
    STATE(5), 2,
      sym_NODE,
      aux_sym__document_repeat1,
  [69] = 7,
    ACTIONS(21), 1,
      sym_left_bracket,
    ACTIONS(23), 1,
      sym_left_bracket_error,
    ACTIONS(25), 1,
      sym_trailing_end_error,
    ACTIONS(27), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
    STATE(12), 1,
      sym__node,
    STATE(43), 1,
      sym__left_bracket,
    STATE(6), 2,
      sym_NODE,
      aux_sym__document_repeat1,
  [92] = 7,
    ACTIONS(29), 1,
      sym_trailing_end_error,
    ACTIONS(31), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
    ACTIONS(33), 1,
      sym_left_bracket,
    ACTIONS(36), 1,
      sym_left_bracket_error,
    STATE(12), 1,
      sym__node,
    STATE(43), 1,
      sym__left_bracket,
    STATE(6), 2,
      sym_NODE,
      aux_sym__document_repeat1,
  [115] = 5,
    ACTIONS(39), 1,
      aux_sym_document_error_token1,
    ACTIONS(41), 1,
      aux_sym_node_field_name_token1,
    ACTIONS(44), 1,
      sym_newline_character,
    STATE(15), 1,
      sym_node_field_name,
    STATE(7), 4,
      sym__NODE_FIELD,
      sym_NODE_FIELD_SINGLELINE,
      sym_NODE_FIELD_MULTILINE,
      aux_sym__node_repeat1,
  [134] = 3,
    ACTIONS(46), 1,
      sym_three_arrows_left,
    ACTIONS(48), 1,
      aux_sym_single_line_string_token1,
    STATE(23), 2,
      sym_single_line_string,
      aux_sym_NODE_FIELD_MULTILINE_repeat1,
  [145] = 3,
    ACTIONS(50), 1,
      aux_sym_document_literal_error_token1,
    ACTIONS(52), 1,
      sym_right_bracket,
    STATE(10), 2,
      sym__right_bracket,
      sym_right_bracket_error,
  [156] = 3,
    ACTIONS(54), 1,
      aux_sym_document_error_token1,
    ACTIONS(56), 1,
      sym_newline_character,
    STATE(11), 2,
      sym__newline_character,
      sym_newline_character_error,
  [167] = 3,
    ACTIONS(58), 1,
      aux_sym_document_error_token1,
    ACTIONS(60), 1,
      sym_newline_character,
    STATE(4), 2,
      sym__newline_character,
      sym_newline_character_error,
  [178] = 2,
    ACTIONS(62), 2,
      sym_trailing_end_error,
      sym_left_bracket_error,
    ACTIONS(64), 2,
      anon_sym_PERCENT_PERCENT_PERCENT,
      sym_left_bracket,
  [187] = 3,
    ACTIONS(50), 1,
      aux_sym_document_literal_error_token1,
    ACTIONS(66), 1,
      sym_right_bracket,
    STATE(14), 2,
      sym__right_bracket,
      sym_right_bracket_error,
  [198] = 3,
    ACTIONS(68), 1,
      aux_sym_document_error_token1,
    ACTIONS(70), 1,
      sym_newline_character,
    STATE(2), 2,
      sym__newline_character,
      sym_newline_character_error,
  [209] = 3,
    ACTIONS(72), 1,
      aux_sym_document_error_token1,
    ACTIONS(74), 1,
      sym_semicolon_character,
    STATE(17), 2,
      sym__semicolon_character,
      sym_semicolon_character_error,
  [220] = 2,
    ACTIONS(76), 2,
      sym_trailing_end_error,
      sym_left_bracket_error,
    ACTIONS(78), 2,
      anon_sym_PERCENT_PERCENT_PERCENT,
      sym_left_bracket,
  [229] = 3,
    ACTIONS(80), 1,
      aux_sym_document_error_token1,
    ACTIONS(82), 1,
      sym_whitespace_character,
    STATE(26), 2,
      sym__whitespace_character,
      sym_whitespace_character_error,
  [240] = 2,
    ACTIONS(84), 2,
      sym_trailing_end_error,
      sym_left_bracket_error,
    ACTIONS(86), 2,
      anon_sym_PERCENT_PERCENT_PERCENT,
      sym_left_bracket,
  [249] = 3,
    ACTIONS(88), 1,
      aux_sym_document_error_token1,
    ACTIONS(90), 1,
      sym_newline_character,
    STATE(27), 2,
      sym__newline_character,
      sym_newline_character_error,
  [260] = 3,
    ACTIONS(68), 1,
      aux_sym_document_error_token1,
    ACTIONS(92), 1,
      sym_newline_character,
    STATE(29), 2,
      sym__newline_character,
      sym_newline_character_error,
  [271] = 3,
    ACTIONS(94), 1,
      aux_sym_document_error_token1,
    ACTIONS(96), 1,
      sym_newline_character,
    STATE(37), 2,
      sym__newline_character,
      sym_newline_character_error,
  [282] = 3,
    ACTIONS(68), 1,
      aux_sym_document_error_token1,
    ACTIONS(98), 1,
      sym_newline_character,
    STATE(28), 2,
      sym__newline_character,
      sym_newline_character_error,
  [293] = 3,
    ACTIONS(100), 1,
      sym_three_arrows_left,
    ACTIONS(102), 1,
      aux_sym_single_line_string_token1,
    STATE(23), 2,
      sym_single_line_string,
      aux_sym_NODE_FIELD_MULTILINE_repeat1,
  [304] = 2,
    ACTIONS(105), 2,
      sym_trailing_end_error,
      sym_left_bracket_error,
    ACTIONS(107), 2,
      anon_sym_PERCENT_PERCENT_PERCENT,
      sym_left_bracket,
  [313] = 3,
    ACTIONS(109), 1,
      sym_document_literal,
    ACTIONS(111), 1,
      aux_sym_document_literal_error_token1,
    STATE(9), 2,
      sym__document_literal,
      sym_document_literal_error,
  [324] = 3,
    ACTIONS(113), 1,
      aux_sym_node_field_name_token1,
    ACTIONS(115), 1,
      sym_three_arrows_right,
    STATE(20), 1,
      sym_node_field_singleline_value,
  [334] = 2,
    ACTIONS(117), 1,
      aux_sym_single_line_string_token1,
    STATE(8), 2,
      sym_single_line_string,
      aux_sym_NODE_FIELD_MULTILINE_repeat1,
  [342] = 2,
    ACTIONS(121), 1,
      sym_newline_character,
    ACTIONS(119), 2,
      aux_sym_document_error_token1,
      aux_sym_node_field_name_token1,
  [350] = 2,
    ACTIONS(125), 1,
      sym_newline_character,
    ACTIONS(123), 2,
      aux_sym_document_error_token1,
      aux_sym_node_field_name_token1,
  [358] = 2,
    ACTIONS(107), 1,
      sym_newline_character,
    ACTIONS(105), 2,
      aux_sym_document_error_token1,
      aux_sym_node_field_name_token1,
  [366] = 2,
    ACTIONS(127), 1,
      aux_sym_document_error_token1,
    ACTIONS(129), 1,
      sym_semicolon_character,
  [373] = 2,
    ACTIONS(131), 1,
      aux_sym_document_literal_error_token1,
    ACTIONS(133), 1,
      sym_right_bracket,
  [380] = 2,
    ACTIONS(135), 1,
      aux_sym_document_error_token1,
    ACTIONS(137), 1,
      sym_whitespace_character,
  [387] = 1,
    ACTIONS(139), 2,
      aux_sym_node_field_name_token1,
      sym_three_arrows_right,
  [392] = 1,
    ACTIONS(141), 2,
      aux_sym_document_error_token1,
      sym_newline_character,
  [397] = 1,
    ACTIONS(107), 2,
      aux_sym_document_error_token1,
      sym_newline_character,
  [402] = 1,
    ACTIONS(143), 2,
      sym_three_arrows_left,
      aux_sym_single_line_string_token1,
  [407] = 2,
    ACTIONS(145), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
    STATE(47), 1,
      sym_EOF,
  [414] = 1,
    ACTIONS(147), 2,
      aux_sym_document_error_token1,
      sym_newline_character,
  [419] = 1,
    ACTIONS(105), 2,
      sym_three_arrows_left,
      aux_sym_single_line_string_token1,
  [424] = 1,
    ACTIONS(27), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
  [428] = 1,
    ACTIONS(149), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
  [432] = 1,
    ACTIONS(151), 1,
      sym_node_literal,
  [436] = 1,
    ACTIONS(153), 1,
      ts_builtin_sym_end,
  [440] = 1,
    ACTIONS(155), 1,
      anon_sym_NULL,
  [444] = 1,
    ACTIONS(157), 1,
      ts_builtin_sym_end,
  [448] = 1,
    ACTIONS(159), 1,
      ts_builtin_sym_end,
  [452] = 1,
    ACTIONS(161), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
  [456] = 1,
    ACTIONS(163), 1,
      anon_sym_PERCENT_PERCENT_PERCENT,
  [460] = 1,
    ACTIONS(107), 1,
      aux_sym_single_line_string_token1,
};

static const uint32_t ts_small_parse_table_map[] = {
  [SMALL_STATE(2)] = 0,
  [SMALL_STATE(3)] = 23,
  [SMALL_STATE(4)] = 46,
  [SMALL_STATE(5)] = 69,
  [SMALL_STATE(6)] = 92,
  [SMALL_STATE(7)] = 115,
  [SMALL_STATE(8)] = 134,
  [SMALL_STATE(9)] = 145,
  [SMALL_STATE(10)] = 156,
  [SMALL_STATE(11)] = 167,
  [SMALL_STATE(12)] = 178,
  [SMALL_STATE(13)] = 187,
  [SMALL_STATE(14)] = 198,
  [SMALL_STATE(15)] = 209,
  [SMALL_STATE(16)] = 220,
  [SMALL_STATE(17)] = 229,
  [SMALL_STATE(18)] = 240,
  [SMALL_STATE(19)] = 249,
  [SMALL_STATE(20)] = 260,
  [SMALL_STATE(21)] = 271,
  [SMALL_STATE(22)] = 282,
  [SMALL_STATE(23)] = 293,
  [SMALL_STATE(24)] = 304,
  [SMALL_STATE(25)] = 313,
  [SMALL_STATE(26)] = 324,
  [SMALL_STATE(27)] = 334,
  [SMALL_STATE(28)] = 342,
  [SMALL_STATE(29)] = 350,
  [SMALL_STATE(30)] = 358,
  [SMALL_STATE(31)] = 366,
  [SMALL_STATE(32)] = 373,
  [SMALL_STATE(33)] = 380,
  [SMALL_STATE(34)] = 387,
  [SMALL_STATE(35)] = 392,
  [SMALL_STATE(36)] = 397,
  [SMALL_STATE(37)] = 402,
  [SMALL_STATE(38)] = 407,
  [SMALL_STATE(39)] = 414,
  [SMALL_STATE(40)] = 419,
  [SMALL_STATE(41)] = 424,
  [SMALL_STATE(42)] = 428,
  [SMALL_STATE(43)] = 432,
  [SMALL_STATE(44)] = 436,
  [SMALL_STATE(45)] = 440,
  [SMALL_STATE(46)] = 444,
  [SMALL_STATE(47)] = 448,
  [SMALL_STATE(48)] = 452,
  [SMALL_STATE(49)] = 456,
  [SMALL_STATE(50)] = 460,
};

static const TSParseActionEntry ts_parse_actions[] = {
  [0] = {.entry = {.count = 0, .reusable = false}},
  [1] = {.entry = {.count = 1, .reusable = false}}, RECOVER(),
  [3] = {.entry = {.count = 1, .reusable = false}}, SHIFT(42),
  [5] = {.entry = {.count = 1, .reusable = true}}, SHIFT(25),
  [7] = {.entry = {.count = 1, .reusable = false}}, SHIFT(25),
  [9] = {.entry = {.count = 1, .reusable = false}}, SHIFT(24),
  [11] = {.entry = {.count = 1, .reusable = false}}, SHIFT(31),
  [13] = {.entry = {.count = 1, .reusable = true}}, SHIFT(16),
  [15] = {.entry = {.count = 1, .reusable = true}}, SHIFT(18),
  [17] = {.entry = {.count = 1, .reusable = false}}, SHIFT(41),
  [19] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym__document, 5, 0, 0),
  [21] = {.entry = {.count = 1, .reusable = true}}, SHIFT(43),
  [23] = {.entry = {.count = 1, .reusable = false}}, SHIFT(43),
  [25] = {.entry = {.count = 1, .reusable = false}}, SHIFT(49),
  [27] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym__document, 6, 0, 0),
  [29] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym__document_repeat1, 2, 0, 0),
  [31] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym__document_repeat1, 2, 0, 0),
  [33] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym__document_repeat1, 2, 0, 0), SHIFT_REPEAT(43),
  [36] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym__document_repeat1, 2, 0, 0), SHIFT_REPEAT(43),
  [39] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym__node_repeat1, 2, 0, 0),
  [41] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym__node_repeat1, 2, 0, 0), SHIFT_REPEAT(31),
  [44] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym__node_repeat1, 2, 0, 0),
  [46] = {.entry = {.count = 1, .reusable = false}}, SHIFT(22),
  [48] = {.entry = {.count = 1, .reusable = false}}, SHIFT(21),
  [50] = {.entry = {.count = 1, .reusable = false}}, SHIFT(39),
  [52] = {.entry = {.count = 1, .reusable = true}}, SHIFT(10),
  [54] = {.entry = {.count = 1, .reusable = true}}, SHIFT(36),
  [56] = {.entry = {.count = 1, .reusable = true}}, SHIFT(11),
  [58] = {.entry = {.count = 1, .reusable = true}}, SHIFT(24),
  [60] = {.entry = {.count = 1, .reusable = true}}, SHIFT(4),
  [62] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_NODE, 1, 0, 0),
  [64] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_NODE, 1, 0, 0),
  [66] = {.entry = {.count = 1, .reusable = true}}, SHIFT(14),
  [68] = {.entry = {.count = 1, .reusable = true}}, SHIFT(30),
  [70] = {.entry = {.count = 1, .reusable = true}}, SHIFT(2),
  [72] = {.entry = {.count = 1, .reusable = false}}, SHIFT(33),
  [74] = {.entry = {.count = 1, .reusable = true}}, SHIFT(17),
  [76] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym__node, 5, 0, 0),
  [78] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym__node, 5, 0, 0),
  [80] = {.entry = {.count = 1, .reusable = false}}, SHIFT(34),
  [82] = {.entry = {.count = 1, .reusable = true}}, SHIFT(26),
  [84] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym__node, 6, 0, 0),
  [86] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym__node, 6, 0, 0),
  [88] = {.entry = {.count = 1, .reusable = true}}, SHIFT(50),
  [90] = {.entry = {.count = 1, .reusable = true}}, SHIFT(27),
  [92] = {.entry = {.count = 1, .reusable = true}}, SHIFT(29),
  [94] = {.entry = {.count = 1, .reusable = true}}, SHIFT(40),
  [96] = {.entry = {.count = 1, .reusable = true}}, SHIFT(37),
  [98] = {.entry = {.count = 1, .reusable = true}}, SHIFT(28),
  [100] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym_NODE_FIELD_MULTILINE_repeat1, 2, 0, 0),
  [102] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_NODE_FIELD_MULTILINE_repeat1, 2, 0, 0), SHIFT_REPEAT(21),
  [105] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_newline_character_error, 1, 0, 0),
  [107] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_newline_character_error, 1, 0, 0),
  [109] = {.entry = {.count = 1, .reusable = false}}, SHIFT(9),
  [111] = {.entry = {.count = 1, .reusable = false}}, SHIFT(32),
  [113] = {.entry = {.count = 1, .reusable = true}}, SHIFT(35),
  [115] = {.entry = {.count = 1, .reusable = true}}, SHIFT(19),
  [117] = {.entry = {.count = 1, .reusable = true}}, SHIFT(21),
  [119] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_NODE_FIELD_MULTILINE, 8, 0, 0),
  [121] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_NODE_FIELD_MULTILINE, 8, 0, 0),
  [123] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_NODE_FIELD_SINGLELINE, 5, 0, 0),
  [125] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_NODE_FIELD_SINGLELINE, 5, 0, 0),
  [127] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_node_field_name, 1, 0, 0),
  [129] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_node_field_name, 1, 0, 0),
  [131] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_document_literal_error, 1, 0, 0),
  [133] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_document_literal_error, 1, 0, 0),
  [135] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_semicolon_character_error, 1, 0, 0),
  [137] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_semicolon_character_error, 1, 0, 0),
  [139] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_whitespace_character_error, 1, 0, 0),
  [141] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_node_field_singleline_value, 1, 0, 0),
  [143] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_single_line_string, 2, 0, 0),
  [145] = {.entry = {.count = 1, .reusable = true}}, SHIFT(45),
  [147] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_right_bracket_error, 1, 0, 0),
  [149] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_document_error, 1, 0, 0),
  [151] = {.entry = {.count = 1, .reusable = true}}, SHIFT(13),
  [153] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_EOF, 2, 0, 0),
  [155] = {.entry = {.count = 1, .reusable = true}}, SHIFT(44),
  [157] = {.entry = {.count = 1, .reusable = true}},  ACCEPT_INPUT(),
  [159] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_top_node, 2, 0, 0),
  [161] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_DOCUMENT, 1, 0, 0),
  [163] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym__document, 7, 0, 0),
};

#ifdef __cplusplus
extern "C" {
#endif
#ifdef TREE_SITTER_HIDE_SYMBOLS
#define TS_PUBLIC
#elif defined(_WIN32)
#define TS_PUBLIC __declspec(dllexport)
#else
#define TS_PUBLIC __attribute__((visibility("default")))
#endif

TS_PUBLIC const TSLanguage *tree_sitter_strictdoc(void) {
  static const TSLanguage language = {
    .version = LANGUAGE_VERSION,
    .symbol_count = SYMBOL_COUNT,
    .alias_count = ALIAS_COUNT,
    .token_count = TOKEN_COUNT,
    .external_token_count = EXTERNAL_TOKEN_COUNT,
    .state_count = STATE_COUNT,
    .large_state_count = LARGE_STATE_COUNT,
    .production_id_count = PRODUCTION_ID_COUNT,
    .field_count = FIELD_COUNT,
    .max_alias_sequence_length = MAX_ALIAS_SEQUENCE_LENGTH,
    .parse_table = &ts_parse_table[0][0],
    .small_parse_table = ts_small_parse_table,
    .small_parse_table_map = ts_small_parse_table_map,
    .parse_actions = ts_parse_actions,
    .symbol_names = ts_symbol_names,
    .symbol_metadata = ts_symbol_metadata,
    .public_symbol_map = ts_symbol_map,
    .alias_map = ts_non_terminal_alias_map,
    .alias_sequences = &ts_alias_sequences[0][0],
    .lex_modes = ts_lex_modes,
    .lex_fn = ts_lex,
    .primary_state_ids = ts_primary_state_ids,
  };
  return &language;
}
#ifdef __cplusplus
}
#endif
