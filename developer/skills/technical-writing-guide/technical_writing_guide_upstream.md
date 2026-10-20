---
name: technical-writing-guide
description: Rules and DO/AVOID examples for writing short, well-structured technical documentation - BLUF, topic sentences, short paragraphs, sentence case, active voice, consistent terminology, concise wording, and structure over prose. Use when writing or editing technical docs, READMEs, specs, or reviewing text for clarity and conciseness.
---

# Technical writing guide

Version: v1.2

## Check-in

MANDATORY: When you use this skill in a response, print this line before anything else:

`**technical-writing-guide v1.2** activated`

## Rule of thumb

Make documentation useful. Apply the rule of thumb to every document, section, page, paragraph, sentence, table, and diagram.

## How to apply this skill

- New text: draft with BLUF. Then check every sentence against the rules below before you finish.
- Edit or review of existing text: go rule by rule. Flag each violation by rule name. Rewrite the violation with the matching DO pattern.
- Do not apply a rule if the rule would remove technical accuracy or essential context (see "Preserve technical accuracy and essential context").
- Final pass, mandatory: your own rewrite is new text. A rule check against the original sentence does not cover the text that your edit produced. After all edits, take every sentence that you wrote, including every sentence that you rewrote. Run the full rule list against each of these sentences a second time, from the top of this document, as a first-time reader would. A fix for one violation (for example, a semicolon, a merged sentence, a passive verb) often creates a different violation nearby. As a result, a targeted fix to one rule does not replace the full second pass.
- Review of your own prior edit (for example, after the user flags one violation): a fix to that one violation does not complete the review. Run the full rule list again against every sentence that the fix changed. The fix is new text. As a result, the fix needs the same check as any other text that you write.

## Unique useful documents

Criteria for a useful document:

- A colleague can read the page without further explanation.
- A colleague can use the page during onboarding.
- Stretch goal: the page meets the quality standard of an artifact in a formal review.

## Bottom line up front

Use BLUF (bottom line up front). State the conclusion before the supporting details. The reader gets the conclusion, decision, or request from the opening sentences alone.

BLUF is a deductive style. Start with the conclusion. Then explain the reasoning, evidence, or background that supports the conclusion. Avoid an inductive structure, where the reader must follow the entire chain of reasoning to find the conclusion at the end.

BLUF applies at every level. A document opens with its conclusion. A section opens with its summary. A paragraph opens with its topic sentence (see "Open each paragraph with a topic sentence").

Rationale: Deductive writing reduces cognitive effort. The reader can also decide at once whether to read the supporting details.

## Use sentence case

Use sentence case instead of Title Case for headings, titles, and similar text. Capitalize only the first word and any proper nouns.

Rationale: Title Case mixes capital and lowercase letters. The mix increases the reading effort: `Managing External Python Dependencies in Large Software Projects`.

|  | Example |
|---|---|
| AVOID | Manage Dependencies With Python |
| DO | Manage dependencies with Python |

## Units of meaning: fact and topic

The rules below split text at two levels. Each level has its own unit of meaning.

| Unit | Definition | Carried by | Split when |
|---|---|---|---|
| Fact (also called idea) | One statement about one subject: what the subject is, has, or does. | A sentence | The sentence makes more than one statement that could be true or false independently. |
| Topic | One question that a group of facts answers together, for example "How does the link layer handle corrupted frames?" | A paragraph | The facts answer more than one question. |

A section covers a broader topic. The topic of a section breaks down into the topics of its paragraphs.

Tests for each unit:

- Fact test: can one part of the sentence be false while the other part is true? If yes, the sentence holds two facts. Split the sentence.
- Topic test: write the question that the paragraph answers. If one question does not cover every sentence, the paragraph holds two topics. Split the paragraph.

The topic test depends on the breadth of the question. "What does the receiver do?" covers more facts than "How does the receiver check frames?" Match the breadth of the question to the amount of text. A short text needs only broad topics. A long text needs narrower topics, so that the reader can scan the text.

|  | Example |
|---|---|
| AVOID | The receiver checks the CRC of each frame and runs on core 1. |
| DO | The receiver checks the CRC of each frame. The receiver runs on core 1. |

In the AVOID sentence, the CRC check and the core assignment can each be true or false independently. The sentence holds two facts, so split it into two sentences. Both sentences answer one broad question, "What does the receiver do?", so they stay in one paragraph. In a longer description of the receiver, the CRC check and the core assignment can each grow into a paragraph of its own, for example:

|  | Example |
|---|---|
| DO | The receiver has two properties that affect the rest of the system: the CRC check and the core assignment.<br><br>The receiver checks the CRC of each frame. The receiver computes a CRC-32 over the header and the payload. If the result does not match the CRC field of the frame, the receiver drops the frame. Each dropped frame increments the `rx_crc_errors` counter.<br><br>The receiver runs on core 1. No other real-time task runs on core 1. This isolation lets the receiver process each frame within 50 µs. The network interface sends its interrupts to core 1 only. |

The first paragraph names both facts. Each of the next paragraphs opens with one of the two facts as its topic sentence. Each of these paragraphs answers a narrower question: "How are frames checked?" or "Where does the receiver run?"

## Paragraphs and sections

A paragraph groups related facts. A paragraph break tells the reader where one topic ends and the next topic begins.

### Keep each paragraph and section on one topic

Give each paragraph one topic (see "Units of meaning: fact and topic"). When a paragraph drifts to a second topic, start a new paragraph. Split a section into focused subsections when the section covers more than one topic.

Do not split a short text into one-sentence paragraphs. When a text has only a few sentences, one broad topic usually covers every sentence. Split into narrower topics when the text grows and each narrower topic has enough content to stand alone.

In a longer text, a one-sentence paragraph is acceptable. When a single fact has a different topic from the surrounding paragraphs, give that fact its own paragraph. Do not attach the fact to an unrelated paragraph to avoid a short paragraph.

Rationale: A paragraph break signals a new topic. The signal only works if every paragraph keeps to one topic.

|  | Example |
|---|---|
| AVOID | The parser reads the configuration file and validates its syntax. The parser logs validation errors to the console and exits with a nonzero code. The parser also caches the parsed configuration in memory for later use by other components. |
| DO | The parser reads the configuration file and validates its syntax. The parser logs validation errors to the console and exits with a nonzero code.<br><br>The parser caches the parsed configuration in memory for later use by other components. |

### Open each paragraph with a topic sentence

The first sentence of a paragraph is the topic sentence. The topic sentence states the main point of the paragraph. The sentences after the topic sentence explain, qualify, or add detail to the topic sentence. A good topic sentence also links to the previous paragraph (see "Link paragraphs through key terms").

Self-check: read only the first sentence of each paragraph, in order. These first sentences alone must tell the complete story of the document. If the story has gaps or jumps, move or rewrite the topic sentences.

Rationale: Topic sentences let a reader understand a document from its first sentences alone. The reader then reads the rest of a paragraph only for the details.

|  | Example |
|---|---|
| AVOID | The receiver checks the CRC of each frame. The receiver drops each frame with an invalid CRC. The receiver forwards the remaining frames to the router. As a result, the router only sees intact frames. |
| DO | The link layer forwards only intact frames to the router. The receiver checks the CRC of each frame. The receiver drops each frame with an invalid CRC. The receiver forwards the remaining frames to the router. |

### Build up information one step at a time

Introduce one new fact per sentence. Each sentence builds on a key term from an earlier sentence (see "Echo a key term from the previous sentence"). Introduce a component before you describe its behavior. Describe the general case before the special case.

Rationale: When a paragraph delivers several new facts at once, the reader must hold all the new facts in memory. As a result, the reader often reads the paragraph a second time.

|  | Example |
|---|---|
| AVOID | If the flight software misses a 500 ms kick on the GPIO line, the hardware watchdog of the OBC resets the processor, after which the boot loader reads the reset cause from the status register and starts the safe-mode image for a watchdog reset. |
| DO | The OBC has a hardware watchdog. The flight software kicks the watchdog every 500 ms over a GPIO line. If the flight software misses a kick, the watchdog resets the processor. After the reset, the boot loader reads the reset cause from the status register. For a watchdog reset, the boot loader starts the safe-mode image. |

### Limit paragraphs to six sentences

A paragraph has at most six sentences. If a paragraph grows past six sentences, split the paragraph into two paragraphs, each with its own topic sentence. The limit has no lower bound. A one-sentence paragraph is acceptable, for example, a sentence that introduces a list (see also "Keep each paragraph and section on one topic").

Rationale: Long paragraphs hide the topic boundaries that paragraphs exist to show. A reader also loses focus in a long block of text.

## Logical flow: key terms and connecting words

Key terms and connecting words show how the facts in a text relate to each other. The two tools do different jobs:

- A key term names a concept of the topic, for example the domain term `Onboard Computer (OBC)`. A repeated key term shows that two facts are about the same thing.
- A connecting word states the relation between two facts, for example `as a result`, `because`, or `after that`. A connecting word shows how one fact follows from another.

Together, key terms and connecting words give the text a logical structure that the reader can follow without effort.

### Identify the key terms

A key term is a word or phrase that carries the topic of a paragraph: a component, a signal, a state, or an action. A key term can be a noun (`housekeeping data`), a verb (`downlinks`), or a longer phrase (`during each pass`).

Before you write a paragraph, identify the key terms of the topic. Put the key terms in the topic sentence. Reuse the key terms in the sentences that follow.

Rationale: Key terms tie the sentences of a paragraph together. A reader who tracks the key terms can follow the paragraph from start to end.

|  | Example |
|---|---|
| DO | The **ground station** receives **telemetry** **during each pass**. **During each pass**, the **ground station** checks every **telemetry** frame for errors. After the pass, the **ground station** forwards the error-free **telemetry** to the mission archive. |

### Echo a key term from the previous sentence

Each sentence after the first one in a paragraph reuses a key term from the previous sentence or from the topic sentence. The repeated key term is the explicit link between the two sentences. Repeat the noun itself instead of a pronoun such as "it", "this", or "that".

If no key term from the previous sentence fits, check two causes:

- The new sentence belongs to a different topic. Move the sentence to another paragraph.
- A step is missing between the two sentences. Add the missing sentence.

Rationale: A repeated key term shows the reader exactly which earlier fact the new sentence builds on. A pronoun forces the reader to guess the referent.

|  | Example |
|---|---|
| AVOID | The OBC collects housekeeping data every second. It is then packed into TM packets. This happens in the TM service, which puts them in the downlink queue. |
| DO | The OBC collects housekeeping data every second. The TM service packs the housekeeping data into TM packets. The TM service puts the TM packets in the downlink queue. |

The DO example in "Build up information one step at a time" follows the same pattern: "watchdog", "kick", "reset", and "boot loader" each carry over from one sentence to the next.

### Use one term for one concept

Pick one term for each concept. Use that term throughout the document. Do not switch to a synonym for variety. Define a short form, such as an abbreviation, once. After the definition, use only the short form. The rule applies to verbs and phrases as well as nouns.

Rationale: A reader assumes that a new term names a new thing. Synonyms make one component look like two.

|  | Example |
|---|---|
| AVOID | The tool writes the report to `out/`. The generated document includes all requirements. The output file is overwritten on each run. |
| DO | The tool writes the report to `out/`. The report includes all requirements. The tool overwrites the report on each run. |

|  | Example |
|---|---|
| AVOID | The scheduler starts the job at 02:00. If the job fails, the scheduler launches the job again after 10 minutes. |
| DO | The scheduler starts the job at 02:00. If the job fails, the scheduler starts the job again after 10 minutes. |

### Link paragraphs through key terms

The topic sentence of a new paragraph reuses a key term from the previous paragraph. The reused key term shows how the new topic relates to the previous topic (see "Open each paragraph with a topic sentence").

Rationale: Without a shared key term, a new paragraph looks like an unrelated topic. As a result, the reader loses the thread of the document.

|  | Example |
|---|---|
| AVOID | The OBC collects housekeeping data every second. The TM service packs the housekeeping data into TM packets.<br><br>The X-band transmitter operates at 8.2 GHz. The transmitter is active only during ground station passes. |
| DO | The OBC collects housekeeping data every second. The TM service packs the housekeeping data into TM packets.<br><br>The X-band transmitter downlinks the TM packets during ground station passes. The X-band transmitter operates at 8.2 GHz. |

### Mark how sentences connect

When two sentences are related and the relation is not obvious, state the relation with a connecting word:

- Result: "as a result", "because of".
- Contrast: "but".
- Sequence: "then", "after", "before".
- Simultaneity: "at the same time".

Do not add a connecting word where the relation is already clear from the key terms. Use only common connecting words (see "Use common words instead of formal connecting words and Latin abbreviations").

Rationale: Without a connecting word, the reader must guess whether the second sentence is a consequence, an exception, or an unrelated fact.

|  | Example |
|---|---|
| AVOID | The OBC enters safe mode. The payload stays powered off. |
| DO | The OBC enters safe mode. As a result, the payload stays powered off. |

## Sentences

### Keep sentences short

Aim for 15–20 words per sentence. Split any sentence longer than 25 words. Count a code identifier, path, or command as one word.

Rationale: Short sentences reduce cognitive load. As a result, the reader understands technical information with less effort.

|  | Example |
|---|---|
| AVOID | The ground segment archives every telemetry frame that the spacecraft downlinks during a pass, together with the reception timestamp, the ground station identifier, and the link quality metrics reported by the modem. (32 words) |
| DO | The ground segment archives every telemetry frame from a pass. (10 words) Each archived frame includes the reception timestamp, the ground station identifier, and the link quality metrics from the modem. (19 words) |

### One idea/fact per sentence

A sentence states one fact about one subject (see "Units of meaning: fact and topic"). Check every sentence that joins two independent clauses with "and", "but", "so", or "which". If each clause could stand as its own fact, split the sentence. Split the sentence even if the combined sentence is shorter than 25 words.

Three exceptions keep two parts in one sentence:

- "Exception: two actions that form one step"
- "Exception: a condition and its action"
- "Exception: a concession and its qualification".

|  | Example |
|---|---|
| AVOID | The parser validates input and runs in a separate process. |
| DO | The parser validates input. The parser runs in a separate process. |

|  | Example |
|---|---|
| AVOID | The scheduler retries failed jobs, and it uses exponential backoff. |
| DO | The scheduler retries failed jobs. Retries use exponential backoff. |

|  | Example |
|---|---|
| AVOID | The command writes the output to disk, and it also validates the configuration, which is useful because invalid configuration can otherwise cause failures later. |
| DO | The command validates the configuration. Then the command writes the output to disk. Configuration validation prevents later failures caused by invalid configuration. |

#### Exception: two actions that form one step

Join two actions of one subject in one sentence when the two actions form one step.

- Test: can one specific verb phrase name both actions? "Reads the configuration file" and "validates the syntax" form one step: "loads the configuration". "Checks the CRC of each frame" and "runs on core 1" have no common name. A generic verb such as "processes" or "handles" does not count.
- Limits: at most two verbs, at most 25 words, and no other clause except a condition (`if`, `when`).

Rationale: Two sentences for one step repeat the subject and the object. The repetition adds no clarity.

|  | Example |
|---|---|
| AVOID | The parser reads the configuration file. The parser validates the syntax of the configuration file. |
| DO | The parser reads the configuration file and validates the syntax. |

#### Exception: a condition and its action

Keep a condition and the action that depends on the condition in one sentence.

Rationale: The action is true only under the condition. A split separates the action from the condition.

|  | Example |
|---|---|
| DO | The receiver discards the packet if its checksum is invalid. |

#### Exception: a concession and its qualification

Keep a concession and its qualification in one sentence. A concession admits that something is true or acceptable. The qualification limits the concession, usually after "but".

- Test: does the second clause tell the reader how to apply the first clause? If yes, keep one sentence. If the two clauses describe two separate behaviors, split the sentence (for example, `The parser accepts empty sections. But the parser rejects empty documents.`).
- Limit: at most 25 words.

Rationale: The qualification only makes sense together with the concession. A split presents the two parts as independent facts.

|  | Example |
|---|---|
| AVOID | The default configuration works. But production systems need a higher timeout. |
| DO | The default configuration works, but production systems need a higher timeout. |

### Prefer direct statements over indirect or elaborate phrasing

State the relevant fact directly.

Rationale: A direct statement makes the meaning of the author explicit. As a result, the reader does not need to interpret the text.

|  | Example |
|---|---|
| AVOID | It should be noted that the parser is not currently capable of handling empty sections. |
| DO | The parser does not support empty sections. |

### Prefer direct statements over contrastive statements

State directly what a thing is or does. Do not define a thing by what the thing is not.

Rationale: Direct statements keep attention on the relevant behavior instead of unnecessary alternatives.

|  | Example |
|---|---|
| AVOID | The parser does not process files individually but instead processes the entire directory. |
| DO | The parser processes the entire directory. |

|  | Example |
|---|---|
| AVOID | This component is not responsible for storage. Instead, it forwards the data to the PDH. |
| DO | This component forwards the data to the PDH. |

### Use active voice

Use active voice. Use passive voice only when the actor is unknown or irrelevant.

Rationale: Active voice names the actor. As a result, the reader can identify responsibilities and system behavior.

|  | Example |
|---|---|
| AVOID | The configuration file is loaded before validation is performed. |
| DO | The system loads and validates the configuration file. |

|  | Example |
|---|---|
| AVOID | The packet is discarded if its checksum is invalid. |
| DO | The receiver discards the packet if its checksum is invalid. |

|  | Example |
|---|---|
| AVOID | The requirement was linked to the test case. |
| DO | The engineer linked the requirement to the test case. |

### Avoid "-ing" verb forms

Rewrite "-ing" verbs as a finite verb form (for example, simple present or simple past).

Exception: keep an "-ing" word when the word functions as an established technical noun (`installation and servicing`) or as a fixed modifier inside a technical noun (`operating system`).

Rationale: The "-ing" form can act as a verb, an adjective, or a noun. The position in the sentence decides the role. A reader must resolve the role before the rest of the sentence makes sense. Drafts with many "-ing" forms also tend to stack several actions in one sentence.

|  | Example |
|---|---|
| AVOID | Restarting the service is required after editing the configuration. |
| DO | Restart the service after you edit the configuration. |

|  | Example |
|---|---|
| AVOID | An operator ignoring the interlock risks damaging the arm. |
| DO | An operator who ignores the interlock can damage the arm. |

|  | Example |
|---|---|
| AVOID | Saving the file and then closing the editor completes the task. |
| DO | Save the file, then close the editor. |

## Wording

Keep all technical writing short and to the point.

### Use the minimum wording required for precision and clarity

Remove words that do not add information or improve understanding, including filler, redundant qualifiers, and transitions that state nothing. Keep a connecting word when it tells the reader something they cannot infer (see "Mark how sentences connect").

The rule of thumb: can I delete this word, sentence, or paragraph without losing the informational value?

Rationale: Concise wording makes the important technical information easier to identify.

|  | Example |
|---|---|
| AVOID | In order to be able to perform the validation, the system needs to first load the configuration file. |
| DO | To validate, the system first loads the configuration file. |

|  | Example |
|---|---|
| AVOID | Basically, this means that the function will simply return the same value again. |
| DO | The function returns the same value. |

### Do not repeat information unless repetition is necessary for understanding

State each fact once unless the reader needs additional context. The rule covers facts, not terms. Repeat a term as often as needed (see "Use one term for one concept").

Rationale: Repetition makes the document longer and adds no information.

|  | Example |
|---|---|
| AVOID | The cache is cleared on startup. This means that every startup clears the cache. |
| DO | The cache is cleared on startup. |

### Preserve technical accuracy and essential context

Do not sacrifice precision or introduce ambiguity to make the text shorter.

Rationale: Technical writing must remain precise enough to support correct interpretation and implementation.

|  | Example |
|---|---|
| AVOID | The request fails after 5 seconds. |
| DO | The request times out if no response is received within 5 seconds. |

### Use common words instead of formal connecting words and Latin abbreviations

Replace formal connecting words and Latin abbreviations with common English words.

| AVOID | DO |
|---|---|
| e.g. | for example |
| i.e. | that is |
| thus | as a result |
| therefore | as a result, because of |
| however | but |

Rationale: Readers who are not native English speakers often do not know these words or misread the words. Readers often confuse "e.g." and "i.e.". Readers rarely misread common words.

|  | Example |
|---|---|
| AVOID | The tool supports several output formats, e.g. HTML and PDF. |
| DO | The tool supports several output formats, for example, HTML and PDF. |

|  | Example |
|---|---|
| AVOID | The tool exports only active requirements, i.e. requirements without the `DEPRECATED` status. |
| DO | The tool exports only active requirements, that is, requirements without the `DEPRECATED` status. |

|  | Example |
|---|---|
| AVOID | The OBC enters safe mode. Thus, the payload stays powered off. |
| DO | The OBC enters safe mode. As a result, the payload stays powered off. |

|  | Example |
|---|---|
| AVOID | The CRC of the frame is invalid. Therefore, the receiver drops the frame. |
| DO | Because of the invalid CRC, the receiver drops the frame. |

|  | Example |
|---|---|
| AVOID | The parser accepts empty sections. However, the parser rejects empty documents. |
| DO | The parser accepts empty sections. But the parser rejects empty documents. |

## References

### Repeat the subject instead of ambiguous references

Avoid "this," "that," "these," "those," and "it" when they refer to information from a previous sentence. Repeat the subject when needed. A demonstrative followed by the repeated noun (`this parser`, `these frames`) is acceptable because the noun names the referent.

Rationale: Repeating the subject may feel redundant in general writing, but technical writing prioritizes unambiguous references over stylistic variety.

|  | Example |
|---|---|
| AVOID | The parser validates the configuration before startup. This prevents invalid states. |
| DO | The configuration validation prevents invalid states during startup. |

|  | Example |
|---|---|
| AVOID | The OBC sends the command to the PDH. It validates the command before execution. |
| DO | The OBC sends the command to the PDH. The PDH validates the command before execution. |

#### Restructure the sentence instead of repeating the subject

A repeated subject is correct, but a different sentence structure can often avoid the repetition. Try the structures below before you repeat the subject. Do not use a pronoun or the passive voice instead. If no structure keeps the meaning, repeat the subject.

| Structure | AVOID | DO |
|---|---|---|
| A phrase instead of a second clause | The reader reads the rest of a paragraph only when the reader needs the details. | The reader reads the rest of a paragraph only for the details. |
| A condition about another noun | The reader reads the rest of a paragraph only when the reader needs the details. | The reader reads the rest of a paragraph only when the task requires the details. |
| A verb that carries the condition | The reader reads the rest of a paragraph only when the reader needs the details. | The reader can decide after the first sentence whether to read on. |
| The text as the subject | The reader reads the rest of a paragraph only when the reader needs the details. | The sentences after the topic sentence hold the details. |
| The text as the subject, shorter | The reader reads the rest of a paragraph only when the reader needs the details. | The rest of a paragraph holds the details. |

### Choose a form for several facts about one subject

When consecutive sentences have the same subject, choose the form from the table below. Do not use a pronoun as the subject to avoid the repetition.

| Situation | Form |
|---|---|
| One subject, two actions that form one step | One sentence with two verbs (see "Exception: two actions that form one step") |
| One subject, three or more actions | A lead-in with the subject and a list of the actions |
| One subject, unrelated facts | One sentence per fact, with the subject in each sentence |

Rationale: Each form avoids a pronoun as the subject. In `The parser reads the configuration file. It validates the syntax.`, the word "it" can refer to the parser or to the configuration file.

|  | Example |
|---|---|
| AVOID | The parser validates the configuration. The parser reports validation errors. The parser stores the validated configuration. |
| DO | The parser:<br>- validates the configuration<br>- reports validation errors<br>- stores the validated configuration. |

|  | Example |
|---|---|
| AVOID | The receiver checks the CRC of each frame. It runs on core 1. |
| DO | The receiver checks the CRC of each frame. The receiver runs on core 1. |

### Name the team or organization instead of "we" and "they"

Avoid pronouns such as "we," "us," "they," and "them" when referring to teams, organizations, or components. Name the responsible party explicitly.

Rationale: Explicit names prevent ambiguity about ownership and responsibility. They also avoid tribal "us vs. them" framing between teams or organizations.

|  | Example |
|---|---|
| AVOID | We provide the interface, and they implement the client. |
| DO | Thales provides the interface. Airbus implements the client. |

|  | Example |
|---|---|
| AVOID | They send the telemetry to us. |
| DO | Boeing sends the telemetry to Thales. |

## Avoid common AI-writing patterns

LLM drafts tend to carry patterns that read as filler in technical docs. Apply the rules above and also remove the patterns below. For prose outside technical docs, the `humanizer` skill covers a broader set of patterns.

- **Hedge phrases**: "it's worth noting that," "generally speaking," "in many cases." State the fact or delete the sentence.
- **Em dash overuse**: an em dash for nearly every aside. Use a period, comma, or colon instead. Reserve the em dash for a real interruption.
- **Rule-of-three padding**: three examples or adjectives where one or two suffice ("fast, reliable, and efficient"). List only as many items as add distinct information.
- **Throat-clearing openers**: "This document describes..." followed by a sentence that repeats the title. Open with the BLUF instead.

|  | Example |
|---|---|
| AVOID | It's worth noting that, generally speaking, the parser tends to reject malformed input in most cases. |
| DO | The parser rejects malformed input. |

|  | Example |
|---|---|
| AVOID | The scheduler is fast, robust, and efficient — it retries failed jobs up to three times. |
| DO | The scheduler retries failed jobs up to three times. |

## Punctuation

### Avoid semicolons

Do not use semicolons. The rule applies to two clauses in one sentence and to items in a list. Split two clauses into two sentences. In a list, drop the semicolons. When a lead-in and its bullets form one sentence, put the period only on the last item. The other items have no end punctuation.

|  | Example |
|---|---|
| AVOID | The build failed; check the logs for details. |
| DO | The build failed. Check the logs for details. |

|  | Example |
|---|---|
| AVOID | The parser:<br>- validates the configuration;<br>- reports validation errors; |
| DO | The parser:<br>- validates the configuration<br>- reports validation errors. |

## More structure, less prose

Prefer lists, tables, and focused subsections over long blocks of prose.

Rationale: Structure reduces context switching and makes technical documents easier to scan, understand, navigate, and maintain.

### Use lists for enumerations

Put multiple items in a bulleted or numbered list instead of a long sentence.

|  | Example |
|---|---|
| AVOID | The command-line tool accepts five flags: `--verbose` for detailed logging, `--dry-run` for previewing changes, `--force` for skipping confirmation prompts, `--output` for specifying the destination path, and `--config` for pointing to a custom configuration file. |
| DO | The command-line tool accepts five flags:<br>- `--verbose`: enables detailed logging.<br>- `--dry-run`: previews changes without applying them.<br>- `--force`: skips confirmation prompts.<br>- `--output`: specifies the destination path.<br>- `--config`: points to a custom configuration file. |

### Use tables for structured comparisons

Use a table to compare multiple items across the same set of attributes.

**Example**:

AVOID: The staging environment uses 2 CPUs, 4 GB of memory, and a 10 GB disk. The production environment uses 8 CPUs, 32 GB of memory, and a 100 GB disk.

DO:

| Environment | CPUs | Memory | Disk |
|---|---|---|---|
| Staging | 2 | 4 GB | 10 GB |
| Production | 8 | 32 GB | 100 GB |

## Worked example

The example below rewrites one paragraph with BLUF, a topic sentence, active voice, direct statements, subject repetition, and list structure.

|  | Example |
|---|---|
| AVOID | It should be noted that in order to be able to deploy the service, several things generally need to happen first. The configuration file is read by the deployment script, and then it is validated. If the configuration is invalid, the deployment is not performed, which is useful because this prevents partial or broken deployments. Once the configuration has been validated, the script also checks that the target environment is reachable, and after that it uploads the build artifact and restarts the service. |
| DO | The deployment script validates the configuration before each deployment. As a result, an invalid configuration cannot cause a partial or broken deployment.<br><br>To deploy, the script:<br>- reads and validates the configuration file<br>- checks that the target environment is reachable<br>- uploads the build artifact<br>- restarts the service. |
