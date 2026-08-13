# StrictDoc house voice — style profile

STATUS: first genre sub-profile built (user-facing docs). Others
(developer guide, release notes, PR descriptions) not started.

This file is meant to hold corpus-derived, quote-backed observations about
how StrictDoc's own documentation and release notes are actually written —
not generic advice. It has priority over generic style guidance once filled
in, but stays subordinate to explicit user instructions and to the SDG's
"Technical writing" section (`docs/strictdoc_11_developer_guide.sdoc`), which
remains the baseline requirement regardless of what this file says.

To build or extend it, see "Building style_profile.md" in `doc-voice.md` in
this directory. Do not fill this file in without that explicit
corpus-selection step with the user — a profile built from an
unrepresentative or self-selected corpus is worse than no profile, because
it will read as authoritative.

## Corpus notes

- `docs/strictdoc_01_user_guide.sdoc` — used for the "User-facing docs"
  sub-profile below. Sampled closely (Introduction, feature summary,
  Document grammar, Security considerations, IDE support, Syntax rules,
  Hello World tutorial, Document structure/elements, Reserved fields, MID
  vs UID, field types, grammar element properties, relations and roles,
  links and anchors — roughly 2100 of 6073 lines); the remaining ~2/3 of
  the file (Markup, export formats, and everything past "Anchors") has not
  been reviewed yet, so treat this sub-profile as a second pass, not final.
- `docs/strictdoc_02_feature_map.sdoc` — explicitly excluded. Contains
  zero-width-space artifacts (present since the file's first commit,
  2024-11-10) and near-every-paragraph "-ing" participial tails, both
  consistent with an unedited AI draft. Not usable as a voice source as-is.
  To be cleaned up separately (own commit, via feature-docs + doc-voice),
  not part of this profile-building effort.
- Developer guide, release notes, and PR/commit descriptions: not yet
  sampled. Do not assume the rules below apply to them — see "Genre
  sub-profiles" in `doc-voice.md`.

## Genre sub-profiles

### User-facing docs (docs/strictdoc_01_user_guide.sdoc onward)

**Hard bans**

1. No sentence-ending (or sentence-threading) "-ing" participial tail that
   restates a benefit or consequence — "...enabling X", "...ensuring Y",
   "...allowing Z". Across the ~250 sampled lines this occurs once each for
   "enabling" and "ensuring" in the whole 6073-line document; the near-total
   absence is itself the pattern, not a handful of counterexamples. The ban
   targets the construction, not any claim riding on it. If the tail states
   a real fact (for example, that mandatory fields keep documents
   consistent), keep the fact as its own plain sentence and cut only the
   "-ing" framing.
2. Don't route a capability through an abstracted "the feature allows users
   to...". Name the product/component as the grammatical subject directly:
   "StrictDoc allows declaration of document grammars...", "StrictDoc's
   grammar requires each node...", not "This feature enables users to...".

**Allowed and encouraged**

1. Bullet lists instead of prose once there are more than two related facts
   to state — the Introduction goes straight from one definition sentence
   into a bulleted feature summary; the Security section lists what makes
   the web server unsafe as bullets, not a paragraph.
2. Concrete numbers, dates, or version markers when they're known and add
   information: "generation of document trees with up to 2000–3000
   requirements into HTML pages stays within a few seconds"; "deprecated
   since 2025-Q2. The `REQ_PREFIX` alias will be removed from the codebase
   in 2025-Q3." When no number/date is known, a plain description without
   one is fine — the point is not to force one in, or to strip out a real
   one to sound more general, but to include whatever level of concrete
   detail is actually available and useful.
3. `shall` vs `should` used as a deliberate pair, not interchangeably:
   `shall` for a mandatory requirement ("Every requirement shall have its
   `STATEMENT` field specified"), `should` for a recommendation that isn't
   mandatory ("Every requirement should have its `TITLE` field specified").
   Reserve both for normative statements about what a document/field must
   or ought to do; don't spend either on ordinary descriptive sentences.
4. State limitations and weaknesses flatly, without softening or apology:
   "StrictDoc's web server is not yet hardened against unsafe use", "A user
   still has to access the command line... manually."
5. RST admonitions, chosen by purpose, not interchangeably:
   - `.. warning::` — risk, deprecation, or a migration the reader must act
     on.
   - `.. note::` — a supplementary technical clarification.
   - `.. admonition:: Observation` — a practical caveat about how the
     feature plays out in real-world documents.
   - A bold **TL;DR** lead-in (not an admonition directive) — a blunt,
     one-line recommendation stated before the fuller explanation, e.g.
     "**TL;DR** If there is no compelling reason to use the Child
     relations, avoid using them."
6. Tutorial/procedural sections use direct imperative instructions with an
   implied second person: "Open a command-line terminal...", "Run StrictDoc
   as follows:".
7. "Currently, " as a sentence opener to flag a fact that is true now but
   may change, instead of stating it as a permanent given: "Currently, all
   `[REQUIREMENT]`'s fields are optional...", "[STATUS] Currently, only has
   an effect on the Project Statistics screen...".
8. RST list-table (`.. list-table::`) specifically for field/attribute
   reference material (grammar fields, config options, field types) —
   distinct from a plain bullet list, which is used for narrative
   enumeration (features, causes, steps) rather than a field-by-field
   reference.

**Reference examples** (verbatim, StrictDoc's own text)

From the Introduction (`docs/strictdoc_01_user_guide.sdoc:50-64`):

> StrictDoc is software for technical documentation and requirements
> management.
>
> Summary of StrictDoc features:
>
> - The documentation files are stored as human-readable text files.
> - StrictDoc supports two input document formats: SDoc (\*.sdoc) and
>   Markdown (\*.md, see [LINK: SECTION-UG-Markdown-support]).
> - StrictDoc reads these files and builds an in-memory representation of a
>   document tree.

From "Document grammar" (`docs/strictdoc_01_user_guide.sdoc:1913-1921`):

> For anything beyond a small project, it's best to define a document
> grammar early. The default implicit document grammar works for quick
> tests, but real projects often need extra fields or custom node types.
> Starting with your own grammar saves time later.
>
> StrictDoc allows declaration of document grammars with custom fields that
> are specific to a particular document.
>
> First, such fields have to be registered on a document level using the
> ``[GRAMMAR]`` field.

From "Strict rule #1" (`docs/strictdoc_01_user_guide.sdoc:2633-2637`):

> StrictDoc's grammar requires each node, such as ``[REQUIREMENT]``,
> ``[[SECTION]]``, etc., to be separated with exactly one empty line from
> the nodes surrounding it. This rule is valid for all nodes. Absence of an
> empty line or presence of more than one empty line between two nodes will
> result in an SDoc parsing error.

From "Parent vs Child relations" (`docs/strictdoc_01_user_guide.sdoc:2354-2360`):

> **TL;DR** If there is no compelling reason to use the Child relations,
> avoid using them.
>
> Most of the technical requirements documents can be modeled with just a
> Parent relation type. A typical traceability graph for a requirements
> project is typically child-to-parent, where the higher-level parent
> requirements are referred to as "Parents" by their child requirements.

From "Hello World" (`docs/strictdoc_01_user_guide.sdoc:176-190`):

> Open a command-line terminal program supported on your system.
>
> Once you have ``strictdoc`` installed (see [LINK: SDOC_UG_GETTING_STARTED]
> below), use the ``strictdoc new`` command to generate a hello world
> project skeleton.
>
> Run StrictDoc as follows:

### Developer guide, release notes, PR/commit descriptions

Not sampled yet. Build on request, following the same process.
