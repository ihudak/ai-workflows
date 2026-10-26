# Verification — the overlap read lists what a requirement reaches (to-fix PR1, FBB-B13)

**Date:** 2026-10-26 · **Branch:** `iv-gu/overlap-read` · **Versions:** workflows-core 1.49.0, dev-workflows 4.33.0, product-workflows 3.39.0

## What changed, and the population it serves

`workflows-core:grilling-technique` gained *What a requirement overlaps*, five kinds listed before a requirement is read: its condition, what it imports and what imports it, its trigger's other outcomes, its place on a path (both ways), and the inherited `[AD#N]` Rules. `escalation-rules`' inline-fix read cites it; `/design` and `/specify` apply it before a play-back and print an `Overlap read:` line; the fix steps of `/design`, `/specify`, `/create-prd`, `/create-ard`, `/prd-proposal` and `/brd-proposal` cite it instead of narrower wording.

Measured before the design, four live misses on the e2e copies, each found by the artifact's Opus reviewer, three of them spending the one re-review:

| Case | Run | Kind | Source |
|---|---|---|---|
| A | `/design BOOK-3-01`, 2026-10-26 (session `0c71a857`) | its place on a path: security hooks placed ahead of a database-down answer | feedback `BOOK-3-01-design-overlap-read-misses-decision-premises`, `…-playback-cross-decision-read` |
| B | `/specify BOOK-2-01-01`, 2026-10-13 | what it imports: "every rule of a change" carried a `PUT`-only rule to `POST` | `specify-overlap-read-misses-inherited-rules`, `specify-fix-cycle-unverified-overlaps` |
| C | `/specify BOOK-2-01-02`, 2026-10-13 | its trigger's other outcomes: a new outcome left sibling criteria on the old set | `specify-new-outcome-siblings-unqualified`, `specify-precedence-and-inheritance-playback` |
| D | `/design BOOK-1-01`, 2026-10-26 (session `803edf03`) | the inherited `[AD#N]` Rules: a fix accepted missing a 30-second bound with no deviation | `BOOK-1-design-applied-fix-ard-overlap-unread` |

The reach: the ten callers of `grilling-technique` for the gate read, and the seven commands that fix inline for the fix read. The command pointers and the `Overlap read:` line go only to `/design` and `/specify`, where the misses were measured.

## Blind replay

**Method.** Each case was rebuilt as a small task file: the artifact as the run had it at the step that missed (A and C at a play-back, B and D after an inline edit), the rules the run followed, and an instruction to apply them. Each case got two files, one with the rule text at `origin/main` (`8f87d1c9`) and one with this branch's, labelled `<case>1`/`<case>2` at random. Eight fresh Opus agents each read one file and nothing else.

**Result.** All eight named the measured conflict, under the old rules as under the new. The four agents under the new rules printed the `Overlap read:` line in its format where the step asks for one (A and C), and three of the four listed the kinds by name. Several of them found more, under either arm: in A, a second transaction committed after the first leaves D5's "no partial write" false; in B, `[AC10]` keeps a `200` for a change the new criteria refuse.

**What it shows, and what it cannot.** The old rule was not misunderstood: in a fresh context holding only the task, it caught every case. So the replay does not show the change's value. That value lies in long sessions, where the measured misses happened, and a small replay cannot reach them. Two further limits apply. The new rule's worked examples are these four cases, so the new arm was shown the answer. And the replay checks that the rule can be understood and the line printed, never that a run follows it. `docs/superpowers/to-fix.md` PR3 carries the test that can show it: the next live `/design` or `/specify` run, with a trigger for a dedicated reader if the line is missing or a conflict of a listed kind reaches the reviewer anyway.

## Review

An Opus review of `c9323fa0` returned one MAJOR, five MINOR and four NIT findings, all verified against the tree and fixed in `b67af263`. The MAJOR: the kind then named *what runs before it* read only from the requirement that answers a failure, so a step placed ahead of it and written later, case A's order, listed nothing; it became *its place on a path*, read both ways. The MINORs: `escalation-rules`' lead sentence still named only "the same condition"; three docs pages kept the narrow read; the two proposal commands read a fix one way only; the rule did not say where the lists go; and FBB-B13 part (3) had no batch. A scoped re-review of `b67af263` confirmed all ten fixed and found one MINOR (the batch counts in `fix-batches.md` no longer added up) and three NITs (a dead pointer, a docs sentence too dash-heavy to parse, and this replay cited with no record), fixed in the next commit.

## Gates

The full chain of `.github/workflows/validate-catalog.yml`'s `run:` steps, run as one `&&` chain on the branch, exits 0 with no warning after each commit. `.claude/rules/plugin-updates.md` was 56 characters under its 20,000-character warning before this change. Its new bullet fits because the 1.45.0 bullet's measurement moved to `docs/maintainers/rationale.md#coupling-1-45-reads`.
