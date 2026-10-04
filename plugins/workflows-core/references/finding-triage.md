# Finding triage (embedded — shared reference)

The step between a reviewer's findings and a fixer's edits. Run by the **orchestrator**, never by the
fixer: `review-fixer` and `doc-fixer` run on the detection/Sonnet chain while `code-review`,
`doc-reviewer`, and `epic-reviewer` are Opus-pinned, and a dismissal decision must not sit at a weaker
station than the one that produced the finding.

## When this runs

Wherever an **Opus reviewer's reasoned findings feed a fixer**:

| Path | Triage |
|---|---|
| `code-review` → `review-fixer` (`/implement`, `/vuln`, `/upgrade`) | yes |
| `doc-reviewer` → `doc-fixer` (`/document`, keyed mode) | yes |
| `epic-reviewer` → `doc-fixer` (`/epics`) | yes |
| `docs-scaffold-reviewer` → the orchestrator itself (`/docs-init`, and `/docs-brand` standalone) | yes |
| `docs-audit-reviewer` → the orchestrator itself (`/docs-audit`) | yes |
| `proposal-reviewer` → the orchestrator itself (`/prd-proposal`, `/brd-proposal`) | yes |
| a style checker → `doc-fixer` (`/document` direct mode, and the style-fix cycles inside `/document` keyed mode and `/epics`) | **no** |

**Where there is no fixer, the orchestrator is the fixer, and triage still runs.** `docs-scaffold-reviewer`, `docs-audit-reviewer` and `proposal-reviewer` are Opus-pinned and their findings are reasoned claims, but none has a dedicated fixer agent behind it: `/docs-init` and a standalone `/docs-brand` apply the survivors themselves, by direct edit, because the scaffold diff has none (docs-workflows design D25); `/docs-audit` applies them to `docs-backlog.yml` itself, on the same design decision and for the same reason — the file it wrote is the artefact under review and a fixer would add nothing between the finding and the edit; and `/prd-proposal` and `/brd-proposal` fix surviving BLOCKERs inline, editing both proposal artifacts themselves, because a proposal has no delegated writer. **The three group two and one on re-review, so a new caller states which group it follows rather than leaving it to the nearest neighbour.** For `/docs-init`, a standalone `/docs-brand` and `/docs-audit`, which run no re-review at all, that makes the station argument above *stronger*, not moot — the dismissal and the edit sit in one place, so nothing downstream would catch a finding dropped without a reason. `/prd-proposal` and `/brd-proposal` do re-review once after their inline fix, and § On re-review carries forward, at its recorded outcome, a finding triage already dropped where the text it names is unchanged, rather than deciding it again — so that re-review is no second chance for a dismissal, which still has to carry its own reason. `/docs-init`, a standalone `/docs-brand` and `/docs-audit`, which run no re-review, settle an emptied set with a prompt that has no re-review arm (§ When triage empties the survivor set). Everything below applies unchanged with "the fixer" read as "the orchestrator's own edit": survivors only, the patch gate binds that edit, and an emptied survivor set is settled by the user rather than silently promoted. An `--inline` `/docs-brand` run dispatches no review of its own; its diff is triaged inside `/docs-init`'s.

The seam is **reasoned-claim producer vs deterministic producer**, not code vs docs. A reviewer finding
is a claim about consequence and can be checked against the thing it names. A linter violation is not —
a rule matched or it did not, and there is nothing to trace. `/document` and `/epics` each dispatch
`doc-fixer` more than once; this step attaches to the **reviewer-fed dispatch only**.

A review that returns the `Diff: unreadable at <path>` marker never reaches this step. That verdict
reports a capture failure, not a finding about the change: there is no location to verify it at, and its
own BLOCKER says so. The caller stops on the marker (`/implement`, `/vuln`, `/upgrade` each check the
review's first line before acting on the verdict), so no fixer is dispatched and nothing is triaged.

## The step

For each finding, **before any grouping or deduplication**:

1. **Verify its own claimed consequence** at the location it names. Read past the changed lines — into
   the callers, the guards upstream, whatever else the site depends on — far enough to tell whether that
   consequence actually occurs. Another finding's outcome, however adjacent, never settles this one.
2. **Keep, mark unverified, or dismiss** — one outcome per finding, from what verification established:
   - **Keep** a finding where verification confirmed its consequence. A kept finding is a **survivor**.
   - **Dismiss** noise, and a claim the verification refuted — no path to the claimed consequence at the
     named site is a refutation, checked, and a valid disposal. Whatever the reason, **it must dispose
     of that finding's own claim** — by refuting it, or, for an unverified finding the next bullet
     dismisses, by its grade if true: a true fact about neighbouring code that leaves the claim standing
     settles nothing, and the finding is kept where verification confirmed it and is otherwise one
     verification could not settle.
   - **Mark unverified** a finding verification could not settle — the diff and the code around it leave
     open whether its consequence occurs. Use this only where they leave the question open; where they
     are enough to decide, keep the finding or dismiss it. Its grade if true is the reviewer's, raised by
     effect as step 4 says. One whose grade if true is `MAJOR` or `BLOCKER` is recorded at that grade,
     marked `(unverified)`, with what would settle it — the file to read, the input to trace, the run
     that would show it. One whose grade if true is only `MINOR` or `NIT` is dismissed, with that grade
     and what would settle it as its reason. An unverified finding changes nothing the verdict gates;
     it reaches the user through § Reporting.
3. **Record every dismissal and every unverified finding with its reason.** Never drop a finding
   silently. There is no "reject and say nothing" disposition and none may be added.
4. **Raise a grade by effect, never lower one.** Where a survivor's grade reflects the spec's, the
   plan's or the task's silence on the input that triggers it, rather than what the people the change
   serves meet if it ships as it stands — users of the software, readers of the document — raise
   it, to `MAJOR` at most: a `BLOCKER` changes the verdict, and the verdict is not triage's to
   restate (§ When triage empties the survivor set). Step 2 grades an unverified finding by this rule
   too. Record every raise with its reason.
5. **Rule on what the reviewer set aside.** Where the review carries a `### Declined to judge` list
   (`code-review` returns one), rule on each line: it **stands** — record why — or it is a **defect**,
   recorded with its grade by effect and what shows it. A line ruled a defect is never handed to the
   fixer: no finding of the review carries it, and the verdict was taken without it.

**A reviewer with two grades** — one filing only `BLOCKER` and `RECOMMENDATION` — maps onto steps 2
and 4 with `RECOMMENDATION` below `MAJOR`: an unverified `RECOMMENDATION` is dismissed with its note,
and step 4 raises nothing, since the grade above it is `BLOCKER`.

Only survivors are handed to the fixer — never an unverified finding, never a dismissed one.

## When triage empties the survivor set

Triage disposes of findings; it does not restate the verdict. Where no finding behind a non-`PASS`
verdict survives, every one of them dismissed or unverified, the verdict is left standing on nothing —
and because the **verdict**, not the survivor set, is what gates every downstream branch, the run would
otherwise dispatch a fixer with no findings to apply, or escalate a `BLOCKER` that did not survive
triage. The disposition, in order:

1. **Never dispatch the fixer with an empty survivor list.** It has nothing to apply, and the Fix
   Report a later re-review would falsify has nothing to be falsified against. Skip the dispatch.
2. **Never run the unresolved-`BLOCKER` escalation on a `BLOCKER` that did not survive triage** —
   unless the user keeps the verdict at step 3's prompt. That escalation exists for a `BLOCKER` that
   survived a fix cycle, not for one that never survived triage; a user who keeps the verdict says the
   review stayed blocked (§ On re-review), at their own word.
3. **Surface it and let the user settle the verdict.** Report the verdict, the fact that nothing
   survived, every dismissal with its reason and every unverified finding with what would settle it,
   then ask:
   ```
   choices: ["Proceed as if the verdict were PASS — every disposition is recorded (Recommended)", "Re-review, supplying every disposition's reason", "Keep the verdict and stop for a human decision", "Cancel"]
   ```
   A caller that runs no re-review — `/docs-init`, a standalone `/docs-brand`, `/docs-audit` — asks
   without the re-review arm:
   ```
   choices: ["Proceed as if the verdict were PASS — every disposition is recorded (Recommended)", "Keep the verdict and stop for a human decision", "Cancel"]
   ```
   **Keep the verdict** means the review stayed blocked: the caller takes its stop or escalation over
   the `BLOCKER`s the reviewer raised. Where the kept verdict is not `BLOCK` the reviewer raised none,
   and a caller whose stop for a review that stayed blocked is an escalation ends the run instead — or,
   working unit by unit, the unit — as its own Cancel does. **Cancel** is the caller's own cancel.
   **Never** promote a non-`PASS` verdict to `PASS` silently. The orchestrator's authority under this
   reference is over *findings*; a verdict its own findings no longer support is the user's to settle.

A partly emptied set is not this case: where at least one finding survived, the verdict stands and the
command's normal branch runs on the survivors.

This section governs the first review. On a re-review, § On re-review settles the verdict instead —
there, no survivor is handed to a fixer, and its own prompt carries no re-review arm. The prompt
above, in either form, is the **first settle prompt**, since it settles the first review; it and
§ On re-review's are this reference's **settle prompts**.

## The patch gate

A survivor may be auto-fixed only where it shows a defect that **actually occurs**, missing coverage for
a specific case, or a broken gate or convention — **not a state nothing reaches** — and where the
smallest fix adds no public surface, **guards no state the finding did not demonstrate**, and **edits no
file that tells agents or contributors how to work in the repository — `CLAUDE.md`, `AGENTS.md`,
`.github/copilot-instructions.md`, a file under `.claude/rules/` or `.github/instructions/`,
`CONTRIBUTING.md`, `CODING_STANDARDS.md` — that the change under review did not itself edit**. A
survivor failing any of those conditions is surfaced for a human decision instead of patched.

The guard clause is the load-bearing one: a guard added for a state the finding never demonstrated is
the most common shape of a "fix" applied to a false positive, and it is invisible afterwards because it
looks like defensive coding.

The instruction-file clause exists because `code-review` reads the repository's instruction and
contributor files as its documented standards: a finding that the change contradicts one of them is
the likeliest kind to reach the fixer, and editing the file to agree with the code makes such a
finding disappear without settling it. Where the change under review itself edited the file, a
finding on it is a finding on the change, and the clause does not apply. A fixer agent is not handed
the diff, so it applies the clause by the finding's location: it edits such a file only where the
finding's own location is in that file.

## On re-review

A **re-review** is any review a run dispatches over an artifact this run has already reviewed to a
verdict, whatever that verdict was: the one re-review a caller's cap allows, a re-review the user
chose at § When triage empties the survivor set, and `/implement`'s review of its Phase 3.5 fix delta.
For a caller that works unit by unit, the artifact is the unit's own change, never the working tree's
cumulative diff. A `### Re-classification` return is no verdict: whether the review dispatched after
the user overrides one is a re-review turns only on whether an earlier review reached a verdict over
that artifact. A re-review's findings are triaged by § The step, with one check first and three
rules after.

**First, carry what this run already ruled.** A finding that names the same location as a row this
run already logged over that artifact — a code site or a document passage, whose line numbers may
have moved with the fix — and makes the same claim, where the text there still reads as the row
describes, keeps that row's outcome. It is marked **carried**, is not verified again, and is never
handed to a fixer again. A row whose fix changed the text there no longer matches: verify that
finding afresh. A carried survivor is a finding this run has not fixed — a fix that did not take, or
one no fixer was handed — and counts as a survivor below. **The one exception** is a re-review the
user chose at § When triage empties the survivor set, which exists to put every disposition's reason
to the reviewer: there, a re-raised dismissed or unverified finding is verified afresh against the
reviewer's answer.

**Then:**

1. **No survivor of a re-review is handed to a fixer** — each artifact gets at most one fix cycle, and
   only before its first re-review. Each survivor is recorded in the triage line at its own severity,
   and a second verdict that is not `BLOCK` gates nothing further.
2. **The caller's second-verdict stop or escalation acts on a `BLOCKER` surviving the re-review's
   triage — never on the verdict word.** A `BLOCKER` carried as dismissed or unverified is not one.
   A review **stayed blocked** where a `BLOCKER` survives its re-review's triage, or where the user
   keeps the verdict at either settle prompt — the name every caller that re-reviews gives this stop;
   a caller that works unit by unit may count a settle prompt's **Cancel** as one too, and says so; and a caller whose own rule keeps a first review's `BLOCKER` from the fixer, because its fix lies in another code repository, counts that `BLOCKER` as one, and says so.
3. **Where the second verdict is `BLOCK` and no `BLOCKER` survives**, the verdict is one its own
   findings no longer support. Never promote it silently: report the verdict, each carried row with
   its outcome and every new disposition, then ask:
   ```
   choices: ["Proceed — no BLOCKER survived triage, and every disposition is recorded (Recommended)", "Keep the verdict and stop for a human decision", "Cancel"]
   ```
   There is no re-review arm: a re-review's verdict is settled here, never by another review.
   **Proceed** continues as the caller does after a second verdict that is not `BLOCK`. **Keep the
   verdict** means the review stayed blocked: the caller takes its stop or escalation over the
   `BLOCKER`s the reviewer raised — at the user's word, not on triage's. **Cancel** is the caller's
   own cancel.

## Reporting

The orchestrator's run report carries one triage line per review pass, and the line names:

- how many findings were reviewed, and how many **survived**, are **unverified** and were
  **dismissed** — the three always sum to the findings reviewed, and a finding in none of them is a
  triage failure; on a re-review, also how many were **carried**;
- on a re-review, every survivor with its severity — none of them is handed to a fixer;
- **every dismissal with its reason** — a triage that reports only survivors is indistinguishable from
  a reviewer that found less;
- every unverified finding with its grade if true and what would settle it;
- every raise, with the grade it moved from and to and the effect that moved it;
- where the review carried a `### Declined to judge` list, each line with its ruling;
- where a settle prompt was asked, its answer, so a verdict the user settled is never left unmarked.
