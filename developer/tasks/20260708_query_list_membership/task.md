# Add quantified list membership expressions to the query language

## WHAT

Adds support for quantified list membership expressions in the StrictDoc query language:

Example:
```
any(["tag_a", "tag_b"]) in node["TAGS"]
all(["tag_a", "tag_b"]) in node["TAGS"]
none(["excluded_a", "excluded_b"]) in node["TAGS"]
```

The existing scalar membership expression remains supported:
```
"System" in node["TITLE"]
```

## WHY

StrictDoc already supports substring-style membership checks such as `"System" in node["TITLE"]`. When filtering nodes by tags or other fields, users currently have to repeat this expression with explicit boolean operators:

```
("tag_a" in node["TAGS"] or "tag_b" in node["TAGS"])
```

This becomes noisy for product-line filters and other searches that need to match against a list of accepted values. Quantified list membership keeps the existing `in` mental model while making these filters shorter and easier to read.

## HOW

### Proposed behavior

- `any(["A", "B"]) in X` matches when at least one listed string is contained in `X`.
- `all(["A", "B"]) in X` matches when every listed string is contained in `X`.
- `none(["A", "B"]) in X` matches when none of the listed strings are contained in `X`.
- When `X` is `node["TAGS"]`, matching is exact against comma-space-separated tag values instead of substring-based.
- The order of strings in the list does not affect matching.
- Existing scalar `in` and `not in` expressions keep their current behavior.
- The first implementation supports string lists on the left-hand side only.
- Bare tag list syntax such as `any([tag_a, tag_b]) in node["TAGS"]` is intentionally not supported in this first step, keeping list items consistent with the existing quoted string syntax.
- Reverse list-field semantics such as `all(node["TAGS"]) in ["A", "B"]` are intentionally not supported in this first step.

### Implementation details

- Extend the query grammar with `StringListExpression`.
- Add `AnyInExpression`, `AllInExpression`, and `NoneInExpression` grammar rules.
- Add corresponding query object model classes.
- Register the new expression classes in the query reader.
- Reuse the existing scalar `in` substring evaluation for each string in the list, except for `node["TAGS"]` where matching is exact against comma-space-separated tag values.
- Add parser tests for the new expression types.
- Add evaluator tests for positive matches, negative matches, order-independent matching, and exact tag matching.
- Add evaluator coverage proving scalar `in` on `node["TAGS"]` keeps its existing substring behavior.
- Add parser rejection tests for intentionally unsupported bare-list and reverse-list-field syntaxes.
- Add integration tests covering `--filter-nodes` with `any([...])`, `all([...])`, and `none([...])` in `node["TAGS"]`.
- Add user guide documentation for quantified list membership expressions.

### Future work

- Consider first-class list-valued fields so expressions such as `all(node["TAGS"]) in ["tag_a", "tag_b"]` can be supported.
- Consider subset/equality-style operators if users need reverse checks such as "all node tags are in this allowed set".

### Verification

- Parser support for `any([...]) in ...`.
- Parser support for `all([...]) in ...`.
- Parser support for `none([...]) in ...`.
- Positive evaluator behavior for all three quantifiers.
- Negative evaluator behavior for all three quantifiers.
- Order-independent evaluator behavior.
- Exact `node["TAGS"]` matching that does not match tag substrings.
- Scalar `in` compatibility for `node["TAGS"]` substring checks.
- Parser rejection for intentionally unsupported syntaxes.
- `--filter-nodes` integration behavior for `any([...])`, `all([...])`, and `none([...])` tag filters.
- User guide examples for `any([...])`, `all([...])`, and `none([...])` tag filters.
