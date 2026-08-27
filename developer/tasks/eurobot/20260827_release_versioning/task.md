# Requirement-to-revision planning and release test scoping

## WHAT

Two additions on top of the requirements/test grammar
(`20260827_requirements_and_test_grammar`), both configuration-level:

1. A `TARGET_REVISION` field of type `SingleChoice` on the `REQUIREMENT`
   element, holding the identifier of the revision (e.g. `C1`, `C2`, `D1`) a
   requirement is planned or implemented for. The choice list grows by one
   entry each time a new minor revision starts, edited through the document
   grammar editor already built into StrictDoc's web UI.
2. A documented way to derive, for a given revision, the set of tests to
   execute: query `REQUIREMENT` nodes by `TARGET_REVISION` (StrictDoc's
   Query Engine already supports `node["TARGET_REVISION"] == "C1"` and
   `in [...]` list membership), then follow their `Parent` relations to
   `TEST_CASE` nodes via the Traceability Matrix screen.

## WHY

The team needs two things the Traceability Matrix alone does not give them:
planning which requirement is implemented in which revision, and, from that
plan, knowing which tests to run for a given revision's testing cycle.
`TARGET_REVISION` supplies the first; the Query Engine plus Traceability
Matrix supplies the second, without any StrictDoc code changes.

The revision scheme itself comes from the team's own engineering process
(quoted at the end of this document in the original), summarized here:

A revision covers the whole robot at a point in time: mechanics,
electronics, and software together, never versioned separately. The format
is major.minor.RC:

- Major is a letter, changed only when a revision breaks compatibility with
  the previous one (an interface removed, an architecture rebuilt). Each
  major revision gets a memorable codename, a character from a video game or
  TV series starting with that letter, and people refer to the revision by
  that name rather than the bare letter.
- Minor is a number, incremented at the end of every month on a fixed
  schedule: whatever is actually finished goes into that minor, not whatever
  is close to finished. The train leaves on time and does not wait for
  stragglers.
- RC (release candidate) is cut at the end of every week. A typical month:
  week one ships an architecture change that breaks the prior implementation
  as RC1; week two adapts the implementation to the new interfaces, and
  system tests confirm whether it works, as RC2. Cutting candidates weekly
  means a problem surfaces in week one instead of the last week, when it is
  far more expensive to fix.

Worked example: `C1_RC1` names a major revision codenamed Cortana (the
letter C), minor number 1 for that month, and the month's first weekly
candidate; people say "Cortana RC1." If RC1 turns up a critical problem, the
next attempt ships as `C2_RC2`: the minor number rises because new work
accumulated since RC1, and the RC number rises too, since it is the
revision's second candidate.

The word "release" stays in use, but only for the software build that
corresponds to a given revision (for example, "release C1_RC1"), never as a
separate, parallel software version number. Mechanics, electronics, and
software share one revision grid.

## HOW

`TARGET_REVISION` field: add to the `REQUIREMENT` element defined in
`20260827_requirements_and_test_grammar`. Populate the `SingleChoice` list
as revisions get planned; StrictDoc's grammar editor supports adding a
choice without hand-editing the underlying `.sdoc` files.

Test scoping query: for revision `C1`, run
`node["TARGET_REVISION"] == "C1"` (or an `in [...]` query across several
past minors, for cumulative planning) in the Query Engine search screen to
list the requirements due by that revision. Cross-reference those
requirement UIDs against the Traceability Matrix screen to read off their
linked `TEST_CASE` nodes: that list is the test plan for the revision's RC
testing.

Git tagging: tag the Eurobot project's own repository (not this StrictDoc
fork) `<Letter><Minor>_RC<N>` (for example `C1_RC1`) at each weekly RC cut.
The tag covers the `.sdoc` documents alongside the mechanics and electronics
artifacts stored in the same repository, matching the shared-revision-grid
principle above.

Recovering a past RC's results: `STATUS`
(`20260827_requirements_and_test_grammar`) is a single current value per
`TEST_CASE`, not a history, so a past RC's results live in that RC's own git
tag rather than in the document itself. Enable `"DIFF"` in the Eurobot
project's `project_features` and use
`strictdoc/features/diff_and_changelog` to diff two tags (for example
`C1_RC1` against `C1_RC2`): the diff screen shows exactly which `TEST_CASE`
statuses, and which `REQUIREMENT` nodes, changed between the two.

Codename glossary: the letter-to-codename mapping (C, Cortana, and so on) is
a short glossary kept in the Eurobot project's own documentation. StrictDoc
needs no special support for it; it is plain reference content.

### Source material

The revision scheme above was supplied by the team, in the original:

```
## Версионирование
**Ревизия** — версия робота целиком: механика, электроника и ПО вместе, а не по отдельности. Формат ревизии — **major.minor.RCcandidate**:
- **major** — буква, которая меняется, когда новая ревизия **несовместима** с предыдущей (сломаны интерфейсы, пересобрана архитектура). Каждой major-ревизии даётся **запоминаемое имя** — из компьютерной игры или сериала на эту же букву — и дальше в разговоре и документации ревизию называют по имени, а не по букве.
- **minor** — число, которое растёт в конце **каждого месяца** по принципу **release train**: в очередной minor уходит всё, что готово на этот момент, — не то, что «почти готово». Поезд уходит по расписанию, а не ждёт опоздавших.
- **RCcandidate (RC)** — кандидат в ревизию, выпускается в конце **каждой недели**. Пример логики: на первой неделе месяца выходит обновление архитектуры (прежняя реализация под него перестаёт работать) — это RC1; на второй неделе реализация адаптируется под новые интерфейсы, и системные испытания это подтверждают (или нет) — RC2. Ранние кандидаты нужны, чтобы поймать проблему на первой неделе, а не на последней: чем раньше найдена проблема, тем дешевле её исправить.

**Пример (буквально).** `C1_RC1` — major-ревизия получила запоминаемое имя «Cortana» (буква C), 1 — номер minor этого месяца, RC1 — первый недельный кандидат; в разговоре так и говорят — «Cortana RC1». Если в RC1 найдена критичная проблема, следующая попытка выходит как `C2_RC2`: minor вырос (накопились новые наработки), RC — тоже (это уже второй кандидат ревизии).

Слово «релиз» в книге по-прежнему встречается — но не как отдельная параллельная нумерация ПО, а как **выпуск ПО в рамках очередной ревизии** (например, «релиз C1_RC1» — сборка прошивки/ПО, соответствующая этой ревизии робота). Механика, электроника и ПО версионируются в одной общей сетке ревизий, а не раздельными нумерациями.
```

### Deferred work

Whether `TARGET_REVISION` should also appear on `TEST_CASE` directly
(denormalized, to avoid the two-step query-then-matrix-lookup) is left open.
Start with the requirement-only field and revisit if the two-step process
proves inconvenient in practice.
