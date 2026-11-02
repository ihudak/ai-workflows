# D31 (1) — a flagged code defect cannot ship unseen

To-fix D31, part (1) only (`docs/superpowers/to-fix.md`, *Design-level*). Parts (2)–(4) stay open as written there.

## Intent

A BRD-route slice can hold a `code-defect-log.md`: entries recording a defect in the customer's code that a decision turned on, each with a disposition the operator chose. When a sibling slice's reconciliation moves a decision such an entry depended on, `/brd-reconcile`'s stale cross-reference sweep cannot rewrite the entry. Every field of it is the operator's. So the sweep writes a `- **Hit:** <path> › [CDF#n] — <what> — needs-a-human` line into that sibling's reconciliation record (`brd-reconcile.md`, *The stale cross-reference sweep*; worked example in `decision-register-format.md` §9).

Today that flag reaches the operator only if `/brd-interview` later works a round on the flagged slice. Otherwise two things happen:

- **`/brd-interview` cannot ask it.** When every round is closed and nothing else is askable, it takes the no-new-round path and only *reports* the flag as waiting (`brd-interview.md`, *Resolve the round*, the no-new-round path). A re-disposition is written only once a round record names it (`decision-register-format.md` §8).
- **`/brd-package` cannot see it.** It ships the log with the stale disposition, because none of its gates reads a reconciliation record.

The customer then receives a package whose code-defect log contradicts a decision already moved.

## Decisions (the maintainer's)

1. **A `/brd-package` gate** (decided 2026-10-29). Before packaging, the gate reads the latest reconciliation record of every slice under the parent for an unanswered `needs-a-human` flag on one of this slice's `[CDF#n]`. Where it finds one, it asks: re-disposition first through `/brd-interview`, or ship with the flag named in the Final report.
2. **`/brd-interview` opens a round for an unanswered flag** (decided 2026-11-02). This makes the gate's "re-disposition first" option work when every round is closed: an unanswered flag counts as something askable, so *Every round is closed* opens round `<highest + 1>`. That round puts the flag to the operator in *Put each `[V]` to the operator* and writes `flag answered` on its round record's `code defects:` line. Rejected alternatives:
   - a gate that could only ship or stop, where "stop" led nowhere while every round is closed;
   - `/brd-package` answering the flag itself, which would make it a second writer of the log.

3. **The sibling records are read as they are on disk, not gated on `main`** (decided 2026-11-02), as `/brd-interview`'s step 9 reads them. In the normal flow every earlier command's handoff is merged before the next runs, so the two reads agree. Where they differ, reading on disk is the safer choice:
   - **A declined `/brd-reconcile` handoff:** the record exists only in the folder. Reading on disk still sees the flag, while a gate on `main` would miss it or block.
   - **A sibling PR still open, or two sessions at once:** whether the record is seen depends on the checkout. That is accepted, and branch-check (`phase-handoff` §6) already catches most of it at the start of a run.

## Settled after the builder check (my calls)

- **`--round N` and the re-open path follow the new trigger through the existing mirror rule.** They take whatever branch the bare run would take (`brd-interview.md`, *Resolve the round*). A flag is answered by whichever counted round record names it.
- **"Ship anyway" is not remembered.** Every `/brd-package` run re-reads the records and asks again, so `/brd-package` writes nothing. The docs page says so.
- **The new `/brd-package` step comes after step 7** (the rounds gate, whose round records decide which flags are answered) and before step 10.

## Goals

- **Packaging asks first.** `/brd-package` never packages a slice holding an unanswered flag without asking the operator.
- **"Re-disposition first" always works.** Choosing it and running `/brd-interview` puts the flag to the operator whatever the state of the rounds, and the next `/brd-package` run no longer sees it.
- **Shipping with the flag is reported.** That choice names each flag (entry, record, hit) in `/brd-package`'s Final report.
- **One statement of "flagged".** The rule saying what makes an entry flagged and what answers a flag is stated once. Today it lives in `/brd-interview`'s *Put each `[V]` to the operator* re-disposition trigger. Both commands cite that one statement.

## Non-goals

- D31 parts (2)–(4): flags from prerequisites under another parent, flags in a reconciliation record that is no longer the latest, and records older than 3.58.0 that write no `- **Hit:**` line.
- Any change to `/brd-reconcile` or to what the sweep writes.
- Anything the customer sees. The flag is plugin-internal. The bundle, the customer prompt and the delivery note do not name it (*How nothing plugin-internal reaches the customer*).

## Anti-goals

- `/brd-package` writes `code-defect-log.md` or any round record. `/brd-interview` stays the log's only writer of dispositions.
- The gate parses an id out of free text. The `<entry>` slot is resolved against the ids the log holds, exactly as `/brd-interview` does today. A hit naming no id in the log is reported and never acted on.
- A second copy of the flag rule drifting from the first.

## Constraints

- **Read only through `decision-register-format.md` §8.** Round records and reconciliation records are read that way, so no torn write counts.
- **Where the gate sits.** It belongs in Phase 0, beside the other gates (steps 6–8). It is cheap and must come before the self-review's model spend.
- **Questions.** The question is an `AskUserQuestion` `choices:` array of 2–4 options with no "Other", presented verbatim, after `/brd-package` has loaded the question rules (`check-questions`).
- **Phase 0's paragraph saying "Do not send the operator back to `/brd-interview`"** (step 6) is about a register that is not on file. Re-read it against the new trigger and keep it true, since there the interview's round test still decides.
- **Releases.** product-workflows gets a minor bump. A coupling bullet is needed only if a workflows-core reference changes; none is expected.
- **Claim-expiry sweep.** At minimum, rewrite these sentences:
  - "A flagged entry reaches the operator only on a run that works a round" (`brd-interview.md`);
  - the no-new-round path's "as waiting for the next run of this command that works a round";
  - to-fix D31 (1), and E-8 in `docs/superpowers/brd-route-follow-ups.md`;
  - the docs pages for `/brd-interview` and `/brd-package`.

  Count each phrase before and after the edit, per `.claude/rules/claim-sweep.md`.

## The shape (decided) and what is left to the builder

- **The shared rule.** "An entry is flagged by …; a flag is answered once a counted round record names it …" moves from `brd-interview.md` into `references/code-defect-log-format.md` as a new section. That reference is already the log's authority, both commands cite it, and both cite the new section. *My call:* placing it there rather than in `decision-register-format.md`.
- **`/brd-interview` reads the records in step 9 of *Resolve inputs and gate the grounded BRD*.** It already reads the latest reconciliation record of every slice under the parent. Where the step lives does not change.
- **`/brd-interview`, *Every round is closed*.** An unanswered flag makes round `<highest + 1>` non-empty even when the round's question generation finds no customer question. Left to the builder:
  - how such a round is opened and closed: holding only `[V]`s, and closed in the same write where it holds no `[C]`, as the round-1 no-question branch already does;
  - what its round record's other lines say.

  The no-new-round path then no longer meets a flag, and its "report as waiting" sentence becomes unreachable. Remove it or rewrite it.
- **`/brd-package` Phase 0, a new step.** It applies only where the folder holds a `code-defect-log.md`:
  - **Inputs:** read the reconciliation records and round records as the shared rule says, and collect the unanswered flags.
  - **None found:** nothing is printed and the run proceeds.
  - **Any found:** print each one (`[CDF#n]`, record path, hit text), then ask once for the whole set:
    `["Stop — re-disposition them first with /product-workflows:brd-interview <BRD-KEY> (Recommended)", "Ship anyway — name them in the Final report"]`.
    The first option ends the run with a named stop code (*my call:* `BRD_PACKAGE_FLAGGED_DEFECTS`) and makes no handoff, since nothing has been written. The second carries the list to the Final report.
  - **A record that exists and cannot be read:** stop, naming it. Its flags are undecidable, as `/brd-interview` treats it. *My call:* stop rather than ask.
- **Final report.** On "Ship anyway", add a `Flagged code defects shipped:` line naming each `[CDF#n]` with its record. Builder: where it goes among the existing lines.
- **Docs.** Update `plugins/product-workflows/docs/commands/brd-package.md` (the new gate, its stop code and its question) and `brd-interview.md`'s docs page (the new round trigger).

## Measured population

Zero on every tree on this machine (2026-10-29): no `- **Hit:**` line and no `code-defect-log.md` on any ref. The machinery shipped in 3.58.0 the day before. Design from the worked example in `decision-register-format.md` §9, and test the prose against it end to end:

- the sibling reconciles and writes the hit;
- `/brd-package` on the flagged slice stops at the gate;
- `/brd-interview` opens round `<highest + 1>`, puts the flag, and writes `flag answered`;
- `/brd-package` passes the gate.
