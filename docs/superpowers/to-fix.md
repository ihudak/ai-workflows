# To fix — open items for another machine or a later session

A running list of work this repository cannot finish by itself: ports to the editions kept elsewhere, and decisions still owed. **Read it before starting work on any edition.** Each item says where it can be done, what to do, how to verify it, and where it came from. When an item is done, delete it here in the same commit that does it, naming that commit in the edition's own changelog or review record.

The repository's three editions of the family: this public one; an internal Claude edition and a Copilot edition, both reachable only from the maintainer's corporate machine. `CLAUDE.md` § Hard constraints and `.claude/rules/gates.md` § *One body, three editions* hold the parity rules.

## E1 — Port `check-docs.sh`'s shared body to the internal Claude and Copilot editions

**Where:** the corporate machine, in each edition's repository. **Source:** this repository at `main` from `030e0f05` on — commits `cb19fa38` and `d0829c80` changed the body.

Everything from the `FAILURES=0` line down (line 185 at `030e0f05`) is byte-identical in all three editions; only the config block above it and `scripts/fixtures/docs/fixture.env` differ. The two commits changed check 12's promised-text part: the families split into `ASKS` (a label *opening* with a verb that asks for text — Enter/Re-enter/Describe, Edit, Specify a path or command, List…manually, Name it/its, Supply the/a), which the `(you'll be prompted` marker excuses, and `PROMISES` (every other family — `I'll <verb>`, `say which`, `give the reason`, `— name it`, a mid-label `supply the`, `(enter`, …), which it **never** excuses, since `escalation-rules` §0 forbids wording the text as a promise whatever else the label says. The selftest gained cases for both.

1. On a branch of the edition, replace the body: keep the edition's lines above `FAILURES=0`, then append this repository's body — `sed -n '/^FAILURES=0$/,$p' <this-repo>/scripts/check-docs.sh`.
2. Run `./scripts/check-docs.sh --root .`. Where check 12 now reports *"promises text the selection cannot carry … the marker never excuses a promise"*, the label is wrong by §0, not the gate: drop the promise phrase and keep the marker — *Correct a field — I'll say which (you'll be prompted)* becomes *Correct a field (you'll be prompted for which)* — and check that the run asks for the text at once after the array. Where it reports *"asks for text"*, add the marker. Here, 191 marked labels at `7c13ce05` matched no `PROMISES` family; an edition's own labels have not been measured.
3. Prove parity: `cmp <(sed -n '/^FAILURES=0$/,$p' scripts/check-docs.sh) <(sed -n '/^FAILURES=0$/,$p' <this-repo>/scripts/check-docs.sh)` prints nothing.
4. Run the edition's whole gate chain, `--selftest` included. Here `--selftest` prints 334 `ok` lines at `030e0f05`; an edition's count differs only by cases its own config switches off.

## E2 — Port the plugin fixes of the 2026-10-15 review to the editions that carry the same text

**Where:** the corporate machine. **Source:** `cb19fa38`, `d0829c80` and the commit that added this file (`git log -1 --format=%h -- docs/superpowers/to-fix.md`); what each fixes and why is in `docs/superpowers/reviews/2026-10-15-review-of-five-merges.md` (F1–F5, the fixed MINORs, and *Re-review of the fix commit*). List the files with `git show --stat <sha>` for each, and read each change with `git show <sha> -- <file>`.

Port a change only where the edition holds the passage it edits. Several sit on features this repository shipped in the five merges reviewed (`e4491695..7c13ce05`) — row B′ of `require-on-main`, the *A selection carries no text* rule and its `(you'll be prompted…)` labels, `/conformance`'s merged-code test — so an edition that has not taken those merges has nothing to port the fix onto: take the merge first, or skip the fix and say so in the edition's record. The groups, by file:

- `workflows-core`: `references/ard-resolution.md` (an ARD only the default branch holds reaches `require-on-main`; only row B leaves it unread), `references/phase-handoff.md` (row B′'s session-file conflict advice).
- `dev-workflows`: `commands/ready.md` and `docs/commands/ready.md` (the added-ARD B′ finding), `hooks/preload-context.sh` and `docs/reference/hooks.md` (no `REPOS_PATH` line for `/implement`).
- `docs-workflows`: `hooks/preload-context.sh`, `commands/release-notes.md`, `docs/commands/document.md`.
- `product-workflows`: `hooks/preload-context.sh`; `commands/brd-reconcile.md` and its docs page (*Correct it* copies `chosen` and the reason out of the review, and the record names every *Correct it* pick); `commands/brd-interview.md`, `commands/brd-split.md`, `commands/epics.md` and its docs page, `commands/create-prd.md`, `commands/create-ard.md` and its docs page, `commands/specify.md`.

Each edition keeps its own versions and changelog. Run its gate chain after.

## E3 — Re-review the deferred findings once the `/conformance` rework lands

**Where:** any machine, once the rework that lets an Epic run of `/conformance` trace unmerged branches is on `main`. **Source:** `docs/superpowers/reviews/2026-10-15-review-of-five-merges.md` — *Deferred — `/conformance`* (C1–C7) and *Deferred — design-level MINORs* (D1–D14).

Re-read each against the tree as it then stands — several `/conformance` findings may be moot — and fix what survives; where an edition carries the same text, port it as E2 says.

## D14 — a decision owed: should the plugin push a branch the operator merged into?

**Where:** this repository; nothing here needs another machine, only the call. **Source:** the review record's D14.

After the operator merges the default branch into a plugin branch, as row B′'s stop asks, the next `commit-artifacts` commits its session files on that branch and does not push it: `push-scope` (`workflows-core:specs-repo-git` §4 step 5) publishes session-file commits alone, and the merge — the operator's own commit, possibly carrying their conflict resolutions — and the default branch's commits behind it are not. The run reports *Committed, not pushed*, and the next deliverable handoff push clears it, so nothing is lost or silent. Two ways to close it:

- **(a) Say it in the stop, keep the rule.** Row B′'s plain form adds that the merge is pushed by the operator — `git -C "$SPECS_PATH" push origin <branch>`, where the branch is on `origin` — or by the next handoff, and that session commits wait until then. The plugin still never publishes a commit it did not make. **Recommended.**
- **(b) Widen `push-scope` on a plugin branch** to leave out commits the default ref already holds and to admit a merge whose second parent is on it. That makes the plugin publish a commit the operator authored, against the rule's whole reason (`docs/maintainers/rationale.md#specs-push-scope`), and needs that rule re-argued first.
