#include "tree_sitter/parser.h"

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#endif

#define LANGUAGE_VERSION 14
#define STATE_COUNT 17
#define LARGE_STATE_COUNT 2
#define SYMBOL_COUNT 21
#define ALIAS_COUNT 0
#define TOKEN_COUNT 10
#define EXTERNAL_TOKEN_COUNT 0
#define FIELD_COUNT 0
#define MAX_ALIAS_SEQUENCE_LENGTH 6
#define PRODUCTION_ID_COUNT 1

enum ts_symbol_identifiers {
  aux_sym_document_error_token1 = 1,
  sym_trailing_end_error = 2,
  sym_EOF = 3,
  sym_document_literal = 4,
  aux_sym_document_literal_error_token1 = 5,
  sym_left_bracket = 6,
  sym_left_bracket_error = 7,
  sym_right_bracket = 8,
  sym_newline_character = 9,
  sym_top_node = 10,
  sym_DOCUMENT = 11,
  sym__document = 12,
  sym_document_error = 13,
  sym__document_literal = 14,
  sym_document_literal_error = 15,
  sym__left_bracket = 16,
  sym__right_bracket = 17,
  sym_right_bracket_error = 18,
  sym__newline_character = 19,
  sym_newline_character_error = 20,
};

static const char * const ts_symbol_names[] = {
  [ts_builtin_sym_end] = "end",
  [aux_sym_document_error_token1] = "document_error_token1",
  [sym_trailing_end_error] = "trailing_end_error",
  [sym_EOF] = "EOF",
  [sym_document_literal] = "document_literal",
  [aux_sym_document_literal_error_token1] = "document_literal_error_token1",
  [sym_left_bracket] = "left_bracket",
  [sym_left_bracket_error] = "left_bracket_error",
  [sym_right_bracket] = "right_bracket",
  [sym_newline_character] = "newline_character",
  [sym_top_node] = "top_node",
  [sym_DOCUMENT] = "DOCUMENT",
  [sym__document] = "_document",
  [sym_document_error] = "document_error",
  [sym__document_literal] = "_document_literal",
  [sym_document_literal_error] = "document_literal_error",
  [sym__left_bracket] = "_left_bracket",
  [sym__right_bracket] = "_right_bracket",
  [sym_right_bracket_error] = "right_bracket_error",
  [sym__newline_character] = "_newline_character",
  [sym_newline_character_error] = "newline_character_error",
};

static const TSSymbol ts_symbol_map[] = {
  [ts_builtin_sym_end] = ts_builtin_sym_end,
  [aux_sym_document_error_token1] = aux_sym_document_error_token1,
  [sym_trailing_end_error] = sym_trailing_end_error,
  [sym_EOF] = sym_EOF,
  [sym_document_literal] = sym_document_literal,
  [aux_sym_document_literal_error_token1] = aux_sym_document_literal_error_token1,
  [sym_left_bracket] = sym_left_bracket,
  [sym_left_bracket_error] = sym_left_bracket_error,
  [sym_right_bracket] = sym_right_bracket,
  [sym_newline_character] = sym_newline_character,
  [sym_top_node] = sym_top_node,
  [sym_DOCUMENT] = sym_DOCUMENT,
  [sym__document] = sym__document,
  [sym_document_error] = sym_document_error,
  [sym__document_literal] = sym__document_literal,
  [sym_document_literal_error] = sym_document_literal_error,
  [sym__left_bracket] = sym__left_bracket,
  [sym__right_bracket] = sym__right_bracket,
  [sym_right_bracket_error] = sym_right_bracket_error,
  [sym__newline_character] = sym__newline_character,
  [sym_newline_character_error] = sym_newline_character_error,
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
  [sym_EOF] = {
    .visible = true,
    .named = true,
  },
  [sym_document_literal] = {
    .visible = true,
    .named = true,
  },
  [aux_sym_document_literal_error_token1] = {
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
  [sym__document_literal] = {
    .visible = false,
    .named = true,
  },
  [sym_document_literal_error] = {
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
  [sym__newline_character] = {
    .visible = false,
    .named = true,
  },
  [sym_newline_character_error] = {
    .visible = true,
    .named = true,
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
  [10] = 8,
  [11] = 11,
  [12] = 12,
  [13] = 13,
  [14] = 14,
  [15] = 15,
  [16] = 16,
};

static bool ts_lex(TSLexer *lexer, TSStateId state) {
  START_LEXER();
  eof = lexer->eof(lexer);
  switch (state) {
    case 0:
      if (eof) ADVANCE(15);
      if ((!eof && lookahead == 00)) ADVANCE(18);
      if (lookahead == 'D') ADVANCE(11);
      if (lookahead == '[') ADVANCE(24);
      if (lookahead == ']') ADVANCE(27);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(14);
      END_STATE();
    case 1:
      if ((!eof && lookahead == 00)) ADVANCE(18);
      if (lookahead == '\n' ||
          lookahead == ' ') ADVANCE(17);
      if (('\t' <= lookahead && lookahead <= '\r')) SKIP(1);
      END_STATE();
    case 2:
      if (lookahead == '\n') ADVANCE(26);
      if (lookahead == '[') ADVANCE(24);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(16);
      if (lookahead != 0) ADVANCE(16);
      END_STATE();
    case 3:
      if (lookahead == '\n') SKIP(3);
      if (lookahead == 'D') ADVANCE(22);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(21);
      if (lookahead != 0) ADVANCE(20);
      END_STATE();
    case 4:
      if (lookahead == '\n') SKIP(5);
      if (lookahead == ']') ADVANCE(27);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(23);
      if (lookahead != 0) ADVANCE(20);
      END_STATE();
    case 5:
      if (lookahead == '\n') SKIP(5);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(23);
      if (lookahead != 0) ADVANCE(20);
      END_STATE();
    case 6:
      if (lookahead == '\n') ADVANCE(28);
      if (lookahead != 0) ADVANCE(16);
      END_STATE();
    case 7:
      if (lookahead == 'C') ADVANCE(13);
      END_STATE();
    case 8:
      if (lookahead == 'E') ADVANCE(10);
      END_STATE();
    case 9:
      if (lookahead == 'M') ADVANCE(8);
      END_STATE();
    case 10:
      if (lookahead == 'N') ADVANCE(12);
      END_STATE();
    case 11:
      if (lookahead == 'O') ADVANCE(7);
      END_STATE();
    case 12:
      if (lookahead == 'T') ADVANCE(19);
      END_STATE();
    case 13:
      if (lookahead == 'U') ADVANCE(9);
      END_STATE();
    case 14:
      if (eof) ADVANCE(15);
      if ((!eof && lookahead == 00)) ADVANCE(18);
      if (lookahead == 'D') ADVANCE(11);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(14);
      END_STATE();
    case 15:
      ACCEPT_TOKEN(ts_builtin_sym_end);
      END_STATE();
    case 16:
      ACCEPT_TOKEN(aux_sym_document_error_token1);
      END_STATE();
    case 17:
      ACCEPT_TOKEN(sym_trailing_end_error);
      if (lookahead == '\n' ||
          lookahead == ' ') ADVANCE(17);
      END_STATE();
    case 18:
      ACCEPT_TOKEN(sym_EOF);
      END_STATE();
    case 19:
      ACCEPT_TOKEN(sym_document_literal);
      END_STATE();
    case 20:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      END_STATE();
    case 21:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      if (lookahead == 'D') ADVANCE(22);
      if (lookahead == '\t' ||
          (0x0b <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(21);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead)) ADVANCE(20);
      END_STATE();
    case 22:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      if (lookahead == 'O') ADVANCE(7);
      END_STATE();
    case 23:
      ACCEPT_TOKEN(aux_sym_document_literal_error_token1);
      if (lookahead == '\t' ||
          (0x0b <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(23);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead)) ADVANCE(20);
      END_STATE();
    case 24:
      ACCEPT_TOKEN(sym_left_bracket);
      END_STATE();
    case 25:
      ACCEPT_TOKEN(sym_left_bracket_error);
      END_STATE();
    case 26:
      ACCEPT_TOKEN(sym_left_bracket_error);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(26);
      if (lookahead != 0 &&
          lookahead != '[') ADVANCE(25);
      END_STATE();
    case 27:
      ACCEPT_TOKEN(sym_right_bracket);
      END_STATE();
    case 28:
      ACCEPT_TOKEN(sym_newline_character);
      END_STATE();
    default:
      return false;
  }
}

static const TSLexMode ts_lex_modes[STATE_COUNT] = {
  [0] = {.lex_state = 0},
  [1] = {.lex_state = 2},
  [2] = {.lex_state = 3},
  [3] = {.lex_state = 4},
  [4] = {.lex_state = 6},
  [5] = {.lex_state = 6},
  [6] = {.lex_state = 4},
  [7] = {.lex_state = 6},
  [8] = {.lex_state = 6},
  [9] = {.lex_state = 1},
  [10] = {.lex_state = 1},
  [11] = {.lex_state = 0},
  [12] = {.lex_state = 0},
  [13] = {.lex_state = 0},
  [14] = {.lex_state = 0},
  [15] = {.lex_state = 0},
  [16] = {.lex_state = 0},
};

static const uint16_t ts_parse_table[LARGE_STATE_COUNT][SYMBOL_COUNT] = {
  [0] = {
    [ts_builtin_sym_end] = ACTIONS(1),
    [sym_EOF] = ACTIONS(1),
    [sym_document_literal] = ACTIONS(1),
    [sym_left_bracket] = ACTIONS(1),
    [sym_right_bracket] = ACTIONS(1),
  },
  [1] = {
    [sym_top_node] = STATE(12),
    [sym_DOCUMENT] = STATE(13),
    [sym__document] = STATE(14),
    [sym_document_error] = STATE(14),
    [sym__left_bracket] = STATE(2),
    [aux_sym_document_error_token1] = ACTIONS(3),
    [sym_left_bracket] = ACTIONS(5),
    [sym_left_bracket_error] = ACTIONS(7),
  },
};

static const uint16_t ts_small_parse_table[] = {
  [0] = 3,
    ACTIONS(9), 1,
      sym_document_literal,
    ACTIONS(11), 1,
      aux_sym_document_literal_error_token1,
    STATE(3), 2,
      sym__document_literal,
      sym_document_literal_error,
  [11] = 3,
    ACTIONS(13), 1,
      aux_sym_document_literal_error_token1,
    ACTIONS(15), 1,
      sym_right_bracket,
    STATE(4), 2,
      sym__right_bracket,
      sym_right_bracket_error,
  [22] = 3,
    ACTIONS(17), 1,
      aux_sym_document_error_token1,
    ACTIONS(19), 1,
      sym_newline_character,
    STATE(5), 2,
      sym__newline_character,
      sym_newline_character_error,
  [33] = 3,
    ACTIONS(21), 1,
      aux_sym_document_error_token1,
    ACTIONS(23), 1,
      sym_newline_character,
    STATE(9), 2,
      sym__newline_character,
      sym_newline_character_error,
  [44] = 2,
    ACTIONS(25), 1,
      aux_sym_document_literal_error_token1,
    ACTIONS(27), 1,
      sym_right_bracket,
  [51] = 1,
    ACTIONS(29), 2,
      aux_sym_document_error_token1,
      sym_newline_character,
  [56] = 1,
    ACTIONS(31), 2,
      aux_sym_document_error_token1,
      sym_newline_character,
  [61] = 2,
    ACTIONS(33), 1,
      sym_trailing_end_error,
    ACTIONS(35), 1,
      sym_EOF,
  [68] = 2,
    ACTIONS(31), 1,
      sym_trailing_end_error,
    ACTIONS(37), 1,
      sym_EOF,
  [75] = 1,
    ACTIONS(39), 1,
      sym_EOF,
  [79] = 1,
    ACTIONS(41), 1,
      ts_builtin_sym_end,
  [83] = 1,
    ACTIONS(43), 1,
      sym_EOF,
  [87] = 1,
    ACTIONS(45), 1,
      sym_EOF,
  [91] = 1,
    ACTIONS(47), 1,
      ts_builtin_sym_end,
  [95] = 1,
    ACTIONS(49), 1,
      sym_EOF,
};

static const uint32_t ts_small_parse_table_map[] = {
  [SMALL_STATE(2)] = 0,
  [SMALL_STATE(3)] = 11,
  [SMALL_STATE(4)] = 22,
  [SMALL_STATE(5)] = 33,
  [SMALL_STATE(6)] = 44,
  [SMALL_STATE(7)] = 51,
  [SMALL_STATE(8)] = 56,
  [SMALL_STATE(9)] = 61,
  [SMALL_STATE(10)] = 68,
  [SMALL_STATE(11)] = 75,
  [SMALL_STATE(12)] = 79,
  [SMALL_STATE(13)] = 83,
  [SMALL_STATE(14)] = 87,
  [SMALL_STATE(15)] = 91,
  [SMALL_STATE(16)] = 95,
};

static const TSParseActionEntry ts_parse_actions[] = {
  [0] = {.entry = {.count = 0, .reusable = false}},
  [1] = {.entry = {.count = 1, .reusable = false}}, RECOVER(),
  [3] = {.entry = {.count = 1, .reusable = false}}, SHIFT(11),
  [5] = {.entry = {.count = 1, .reusable = true}}, SHIFT(2),
  [7] = {.entry = {.count = 1, .reusable = false}}, SHIFT(2),
  [9] = {.entry = {.count = 1, .reusable = false}}, SHIFT(3),
  [11] = {.entry = {.count = 1, .reusable = false}}, SHIFT(6),
  [13] = {.entry = {.count = 1, .reusable = false}}, SHIFT(7),
  [15] = {.entry = {.count = 1, .reusable = true}}, SHIFT(4),
  [17] = {.entry = {.count = 1, .reusable = true}}, SHIFT(8),
  [19] = {.entry = {.count = 1, .reusable = true}}, SHIFT(5),
  [21] = {.entry = {.count = 1, .reusable = true}}, SHIFT(10),
  [23] = {.entry = {.count = 1, .reusable = true}}, SHIFT(9),
  [25] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_document_literal_error, 1, 0, 0),
  [27] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_document_literal_error, 1, 0, 0),
  [29] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_right_bracket_error, 1, 0, 0),
  [31] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_newline_character_error, 1, 0, 0),
  [33] = {.entry = {.count = 1, .reusable = true}}, SHIFT(16),
  [35] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym__document, 5, 0, 0),
  [37] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_newline_character_error, 1, 0, 0),
  [39] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_document_error, 1, 0, 0),
  [41] = {.entry = {.count = 1, .reusable = true}},  ACCEPT_INPUT(),
  [43] = {.entry = {.count = 1, .reusable = true}}, SHIFT(15),
  [45] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_DOCUMENT, 1, 0, 0),
  [47] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_top_node, 2, 0, 0),
  [49] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym__document, 6, 0, 0),
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
