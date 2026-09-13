---
name: technical-writing-guide
description: Rules and DO/AVOID examples for writing terse, well-structured technical documentation - BLUF, sentence case, active voice, concise wording, and structure over prose. Use when writing or editing technical docs, READMEs, specs, or reviewing text for clarity and conciseness.
---

# Technical writing guide

Version: v1

## Check-in

MANDATORY: When this skill is used in a response, print this line before anything else:

`**technical-writing-guide v1** activated`

## Rule of thumb

Make documentation useful. Apply this to every document, section, page, paragraph, sentence, table, and diagram.

## How to apply this skill

- Writing new text: draft with BLUF, then check every sentence against the rules below before finishing.
- Editing or reviewing existing text: go rule by rule, flag each violation by rule name, and rewrite it using the matching DO pattern.
- Do not apply a rule if it would remove technical accuracy or necessary context — see "Preserve technical accuracy and essential context."
- Final pass, mandatory: your own rewrite is new text. A rule check done only against the original, pre-edit sentence does not cover what your edit just produced. After all edits, take every sentence you personally wrote or rewrote — not just the ones you drafted from scratch — and run the full rule list against it a second time, from the top of this document, as if reading it cold. Fixing one violation (e.g. a semicolon, a merged sentence, a passive verb) commonly creates a different one nearby, so a targeted fix to one rule is not a substitute for this full re-pass.
- If you are reviewing your own prior edit (e.g. the user flags one violation), do not treat the fix as done once that specific violation is fixed. Re-run the full rule list against every sentence you changed while fixing it — the fix itself is new text and is exactly as unverified as anything else you write.

## Unique useful documents

Criteria for a useful document:

- A colleague can read the page without further explanation.
- A colleague can use the page during onboarding.
- Stretch goal: the page holds up as a review artifact for ESA/DLR.

## Bottom line up front

Use BLUF (bottom line up front). State the conclusion or key point before the supporting details. Readers should understand the conclusion, decision, or request without reading the entire message.

This is a deductive writing style: start with the conclusion, then explain the reasoning, evidence, or background that supports it. Avoid an inductive structure, where the reader must follow the entire chain of reasoning before discovering the main point at the end. Deductive writing reduces cognitive effort and helps readers decide immediately whether they need to read the supporting details.

## Use sentence case

Use Sentence case, not Title Case, for headings, titles, and similar text. Capitalize only the first word and any proper nouns.

Rationale: Title Case alternates capital and lowercase letters, which increases reading effort: `Managing External Python Dependencies in Large Software Projects`.

Examples:

- DO: `Managing dependencies with Python.`
- AVOID: `Managing Dependencies With Python.`

## Technical writing

Keep all technical writing terse.

### Keep sentences short

Aim for 15–20 words per sentence and treat 25 words as a soft limit. If a sentence exceeds 25 words, check whether it can be split without losing clarity or technical precision.

Rationale: Short sentences reduce cognitive load and make technical information easier to understand.

### Use the minimum wording required for precision and clarity

Remove words that do not add information or improve understanding, including filler, redundant qualifiers, and unnecessary transitions.

The rule of thumb: can I delete this word, sentence, or paragraph without losing the informational value?

Rationale: Concise wording makes the important technical information easier to identify.

Examples:

- DO: `To validate, the system first loads the configuration file.`
- AVOID: `In order to be able to perform the validation, the system needs to first load the configuration file.`


- DO: `The function returns the same value.`
- AVOID: `Basically, this means that the function will simply return the same value again.`

### Repeat the subject instead of using ambiguous references

Avoid "this," "that," "these," "those," and "it" when they refer to information from a previous sentence. Repeat the subject when needed.

If several consecutive sentences repeat the same subject, consider introducing the subject once and listing its predicates as bullet points.

Rationale: Repeating the subject may feel redundant in general writing, but technical writing prioritizes unambiguous references over stylistic variety.

Examples:

- DO: `The configuration validation prevents invalid states during startup.`
- AVOID: `The parser validates the configuration before startup. This prevents invalid states.`


- DO: `The OBC sends the command to the PDH. The PDH validates the command before execution.`
- AVOID: `The OBC sends the command to the PDH. It validates the command before execution.`


- DO:

```
The parser:
- validates the configuration
- reports validation errors
- stores the validated configuration.
```

- AVOID: `The parser validates the configuration. The parser reports validation errors. The parser stores the validated configuration.`

### Prefer direct statements over indirect or elaborate phrasing

State the relevant fact directly.

Rationale: Direct statements reduce interpretation and make the author's meaning explicit.

Examples:

- DO: `The parser does not support empty sections.`
- AVOID: `It should be noted that the parser is not currently capable of handling empty sections.`

### Prefer direct statements over contrastive statements

State what something is or does directly. Avoid explaining it by contrasting it with what it is not.

Rationale: Direct statements keep attention on the relevant behavior instead of unnecessary alternatives.

Examples:

- DO: `The parser processes the entire directory.`
- AVOID: `The parser does not process files individually but instead processes the entire directory.`


- DO: `This component forwards the data to the PDH.`
- AVOID: `This component is not responsible for storage. Instead, it forwards the data to the PDH.`

### Keep sentences, paragraphs, and sections focused on one point

Separate independent ideas into separate sentences, paragraphs, or sections. Split a paragraph into smaller paragraphs or sentences when it contains multiple ideas. Split a section into focused subsections when it covers more than one topic.

Rationale: One point at a time makes technical information easier to understand, scan, and reference.

Examples:

- DO: `The command validates the configuration before writing the output to disk. Configuration validation prevents later failures caused by invalid configuration.`
- AVOID: `The command writes the output to disk, and it also validates the configuration, which is useful because invalid configuration can otherwise cause failures later.`

#### One idea/fact per sentence

A sentence should state one fact. When a sentence joins two independent clauses with "and", "but", "so", or "which", and each clause could stand as its own fact, split it into separate sentences — even if the combined sentence is short enough to satisfy the word-count guideline.

Exception: keep clauses joined when they describe a single tightly coupled action or a direct cause and effect, and splitting would force an artificial subject repetition without adding clarity (for example, `The receiver discards the packet if its checksum is invalid.`). Judge by whether the reader loses or gains clarity, not by clause count alone.

Examples:

- DO: `The parser validates input. The parser logs errors to stdout.`
- AVOID: `The parser validates input and logs errors to stdout.`


- DO: `The scheduler retries failed jobs. Retries use exponential backoff.`
- AVOID: `The scheduler retries failed jobs, and it uses exponential backoff.`


- DO:

```
The parser reads the configuration file and validates its syntax. Validation errors are logged to the console and the parser exits with a nonzero code.

The parser caches the parsed configuration in memory for later use by other components.
```

- AVOID: `The parser reads the configuration file and validates its syntax. Validation errors are logged to the console and the parser exits with a nonzero code. The parser also caches the parsed configuration in memory for later use by other components.`

### Do not repeat information unless repetition is necessary for understanding

State each fact once unless the reader needs additional context.

Rationale: Repetition increases document length without adding information.

Examples:

- DO: `The cache is cleared on startup.`
- AVOID: `The cache is cleared on startup. This means that every startup clears the cache.`

### Preserve technical accuracy and essential context

Do not sacrifice precision or introduce ambiguity to make the text shorter. Brevity must not make the text ambiguous.

Rationale: Technical writing must remain precise enough to support correct interpretation and implementation.

Examples:

- DO: `The request times out if no response is received within 5 seconds.`
- AVOID: `The request fails after 5 seconds.`

### Use active voice

Active voice makes technical writing more direct. It also makes the actor and responsibility explicit. Use passive voice only when the actor is genuinely unknown or irrelevant.

Rationale: Active voice makes responsibilities and system behavior easier to identify.

Examples:

- DO: `The system loads the configuration file before validating it.`
- AVOID: `The configuration file is loaded before validation is performed.`


- DO: `The receiver discards the packet if its checksum is invalid.`
- AVOID: `The packet is discarded if its checksum is invalid.`


- DO: `The engineer linked the requirement to the test case.`
- AVOID: `The requirement was linked to the test case.`

### Name the responsible party instead of "us vs. them"

Avoid pronouns such as "we," "us," "they," and "them" when referring to teams, organizations, or components. Name the responsible party explicitly.

Rationale: Explicit names prevent ambiguity about ownership and responsibility. They also avoid tribal "us vs. them" framing between teams or organizations.

Examples:

- DO: `Thales provides the interface. Airbus implements the client.`
- AVOID: `We provide the interface, and they implement the client.`


- DO: `Boeing sends the telemetry to Thales.`
- AVOID: `They send the telemetry to us.`

## Avoid common AI-writing patterns

Text drafted by an LLM tends to carry tics that read as filler in technical docs. Strip these on top of the rules above (for prose outside technical docs, the `humanizer` skill covers the broader pattern set).

- **Hedging phrases**: "it's worth noting that," "generally speaking," "in many cases" — state the fact or omit the sentence.
- **Em dash overuse**: an em dash used for nearly every aside. Use a period, comma, or colon instead. Reserve the em dash for a genuine interruption.
- **Rule-of-three padding**: forcing three examples or adjectives where one or two suffice ("fast, reliable, and efficient"). List only as many items as add distinct information.
- **Throat-clearing openers**: "This document describes..." followed by a sentence that repeats the title. Open with the BLUF instead.

Examples:

- DO: `The parser rejects malformed input.`
- AVOID: `It's worth noting that, generally speaking, the parser tends to reject malformed input in most cases.`


- DO: `The scheduler retries failed jobs up to three times.`
- AVOID: `The scheduler is fast, robust, and efficient — it retries failed jobs up to three times.`

## Punctuation

### Avoid semicolons

No semicolons. This rule applies to joining two clauses in a sentence and to separating items in a list. Split it into separate sentences instead. When a lead-in and its bullets form one sentence, put the period only on the last item. The other items are mid-sentence, not sentence-final.

- DO: `The build failed. Check the logs for details.`
- AVOID: `The build failed; check the logs for details.`

- DO:

```
The parser:
- validates the configuration
- reports validation errors.
```

- AVOID:

```
The parser:
- validates the configuration;
- reports validation errors;
```

## More structure, less prose

Prefer lists, tables, and focused subsections over long blocks of prose.

Rationale: Structure reduces context switching and makes technical documents easier to scan, understand, navigate, and maintain.

### Use lists for enumerations

Use bullet points or a numbered list instead of embedding multiple items in a long sentence.

Examples:

- DO:

```
The command-line tool accepts five flags:
- --verbose: enables detailed logging.
- --dry-run: previews changes without applying them.
- --force: skips confirmation prompts.
- --output: specifies the destination path.
- --config: points to a custom configuration file.
```

- AVOID: `The command-line tool accepts five flags: --verbose for detailed logging, --dry-run for previewing changes, --force for skipping confirmation prompts, --output for specifying the destination path, and --config for pointing to a custom configuration file.`

### Use tables for structured comparisons

Use a table when comparing multiple items across the same set of attributes.

Examples:

- DO:

```
| Environment | CPUs | Memory | Disk |
|---|---|---|---|
| Staging | 2 | 4 GB | 10 GB |
| Production | 8 | 32 GB | 100 GB |
```

- AVOID: `The staging environment uses 2 CPUs, 4 GB of memory, and a 10 GB disk. The production environment uses 8 CPUs, 32 GB of memory, and a 100 GB disk.`

## Worked example

A single paragraph, rewritten by applying BLUF, active voice, direct statements, subject repetition, and list structure together.

AVOID:

```
It should be noted that in order to be able to deploy the service, several things generally need to happen first. The configuration file is read by the deployment script, and then it is validated. If the configuration is invalid, the deployment is not performed, which is useful because this prevents partial or broken deployments. Once the configuration has been validated, the script also checks that the target environment is reachable, and after that it uploads the build artifact and restarts the service.
```

DO:

```
The deployment script validates the configuration before deploying. This prevents partial or broken deployments.

To deploy, the script:
- reads and validates the configuration file
- checks that the target environment is reachable
- uploads the build artifact
- restarts the service.
```
