# Documentation grounding on `$DOCS_PATH` (shared reference)

Several authoring commands produce markedly better output when grounded in the
product's existing shipped documentation — current behavior, customer-facing
terminology, and well-documented analogous features to model new work on. When
`$DOCS_PATH` is set and valid, the commands below ground on it automatically so
the operator never has to add "please also check the documentation in `<dir>`".

This governs *whether docs grounding runs and against what root*, and *how the
result is consumed*. It is **read-only**: these commands never write into
`$DOCS_PATH`. Every miss is a **silent, non-blocking skip** — never an error,
never `emit-block`.

Consumers: `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`,
`/brd-intake` (grill-rank consumption); `/epics`, `/release-notes`
(writer-attach consumption); `/prd-ground` (lead-only consumption).
`/document` does **not** consume this file — it only uses `$DOCS_PATH` as a
write-target discovery hint (see its Phase 0). `/brd-split` deliberately does
**not** consume it either: it allocates requirements to a recorded fate, and
documentation does not inform that decision.

## Procedure — `resolve-docs-grounding <command-name>`

1. **Flags first.** If the invocation carries `--no-docs`, return
   `docs_grounding: OFF`, `reason: "disabled with --no-docs"`. If it carries
   `--docs <path>`, set `docs_root = <path>` and skip step 2.
2. **Resolve the root.** `docs_root = ${DOCS_PATH:-/workspace/docs}` (a single
   directory; the AI container mounts docs at `/workspace/docs`, so the default
   lets grounding work even if the var is not re-exported).
3. **Validity gate — ON only when all hold** (else `OFF` with a one-line reason):
   - `docs_root` is non-empty,
   - it is an existing, readable directory (`test -d "$docs_root" && test -r "$docs_root"`),
   - it contains at least one markdown file
     (`find "$docs_root" -type f -name '*.md' -print -quit` is non-empty).
   On a host where `/workspace/docs` is absent, the gate fails → `OFF` → the run
   behaves exactly as it does without docs grounding.
3.5. **Index state — qmd only.** Skip entirely when `command -v qmd` fails: `retrieval: fallback`, silent, exactly as it does without this step. Otherwise probe with `bounded 10 qmd status` and `bounded 10 qmd collection list` (`workflows-core:bounded-run`). **If either probe fails or times out, treat that exactly as `qmd` absent** — `retrieval: fallback`, silent, no prompt — which mirrors `docs-grounder`'s rung 3 so the command and the agent degrade identically instead of disagreeing about the same broken install. Apply **Shadow detection** below before selecting a coverage branch: a shadowing project-local index means `retrieval: fallback`, no build or refresh, with the shadow clause in the plan-approval line. Otherwise take one branch according to whether a collection covers `docs_root`.

   **Global vector counts do not prove coverage of this root.** A positive `Vectors:` count from `qmd status` can belong entirely to unrelated collections. Successful probes that find no collection covering `docs_root` therefore take the no-collection branch even when the global count is positive. These probes alone establish neither orphaned documents nor a corrupt registry: do not diagnose either, recommend registry repair, or suppress the build choice on that evidence. No direct SQLite inspection or repair belongs to this procedure.

   **One state is narrower, and it is the one the probes can see: an index with documents and no collections at all.** `qmd collection list` reports none — `Collections (0)`, `No collections found`, or no collection entry at all — while `qmd status` reports `Total: <D> files indexed` with `D > 0`. Positive vectors belonging to other roots cannot explain that, because there are no other roots: the index holds documents that no collection reaches. A field run met exactly this — 22,000 documents and 92,330 vectors under an empty collection registry — and was steered into rebuilding what was already built. The cause is still not diagnosed here (a damaged registry, a removed collection whose rows survive, a `qmd cleanup` that has not run), so the no-collection prompt is still shown, but its recommendation moves, its build option says what it may cost, and the plan-approval line says why:

   ```
   choices: ["Skip — ground with keyword fallback this run (Recommended — the index already holds <D> documents that no collection reaches; inspect it with 'qmd status' before rebuilding)",
             "Build the docs index anyway — <N> markdown files; may re-embed documents the index already holds",
             "Turn docs grounding off for this run"]
   ```

   A collection that exists and does not cover `docs_root` is the ordinary no-collection branch, whatever either count says.

   **A collection covers `docs_root`** → `bounded 60 qmd update`. Incremental (qmd re-indexes only changed files), instant when nothing changed, and safe to kill because the index is SQLite and rolls back. On a cap breach, prompt once — never silently pay 60 seconds on every future run:

   ```
   choices: ["Continue with the current index — some pages may be stale (Recommended)",
             "Finish the refresh now — uncapped",
             "Turn docs grounding off for this run"]
   ```

   **No collection covers `docs_root`** → prompt once, at plan approval, before any of the run's real work. `<N>` is `find "$docs_root" -type f -name '*.md' | wc -l`:

   ```
   choices: ["Build the docs index now — one-time, <N> markdown files, downloads a ~1.3 GB model on first use (Recommended — every later run is faster and better grounded)",
             "Skip — ground with keyword fallback this run",
             "Turn docs grounding off for this run"]
   ```

   On "Build": `qmd collection add "<docs_root>" --name docs` then `qmd embed`, **uncapped** — killing a consented build wastes the work it has already done — reporting elapsed time on completion. The prompt disappears permanently once the index exists.

   **Index building NEVER happens inside `docs-grounder`.** An agent cannot ask, so an agent told to self-heal has only two options: burn many minutes silently, or abort on its own judgment. This step exists because the orchestrator can ask.
   **Embedding coverage is a proportion, not a boolean.** `qmd status` reports both a document count and a vector count, so the `qmd-vector` rung is selected on *partial* coverage exactly as on full — and a collection that is, say, two-thirds embedded returns low-relevance noise from `qmd vsearch` for most queries while the digest in fact comes from lexical `qmd search`. Reporting full semantic retrieval while delivering little of it is the defect, not the degradation itself. When the index has embeddings but fewer than the document count, keep `retrieval: qmd-vector` — vector search does work for the embedded slice — and append the partial-coverage clause to the plan-approval line, naming both numbers.

4. **Return** `{ docs_grounding, docs_root, retrieval, reason }`, where `retrieval` is `qmd-vector | qmd-lexical | fallback`. `docs-grounder` re-probes and its rung selection is authoritative; this value drives the prompts above and the line below.

**Default-safety note.** A `/workspace/*` default is safe here because this is a
read-only search base — a wrong/missing default just misses and silently skips.
This mirrors `${REPOS_PATH:-/workspace}`. The one write root, `SPECS_PATH`, deliberately does **not** default; do not change that.

## Plan-approval line

When `resolve-docs-grounding` returns, surface one line in the command's plan/approval (or config-confirm) step, with an off switch. This reference owns the format; consumer commands quote it.

```
docs grounding: ON <root> (retrieval: qmd-vector)
docs grounding: ON <root> (retrieval: qmd-lexical — index has no embeddings)
docs grounding: ON <root> (retrieval: qmd-vector; index refresh exceeded 60s — some pages may be stale)
docs grounding: ON <root> (retrieval: qmd-vector; docs checkout <N> days old — refresh on the host)
docs grounding: ON <root> (retrieval: fallback — qmd absent)
docs grounding: ON <root> (retrieval: fallback — probe failed: <which call, exit or timeout>)
docs grounding: ON <root> (retrieval: fallback — no collection covers this docs root; build once: qmd collection add "<root>" --name docs && qmd embed)
docs grounding: ON <root> (retrieval: fallback — the index holds <D> documents but no collections; a rebuild may duplicate them — check `qmd status` first)
docs grounding: ON <root> (retrieval: qmd-vector; index <M> of <N> documents embedded — vector search covers only part of the corpus)
docs grounding: ON <root> (retrieval: fallback — a project-local .qmd index in <cwd> is shadowing the user-scope one; run from another directory or remove it)
docs grounding: OFF (<reason>)
```

Choose the fallback form by the observed cause: a failed probe establishes no coverage result, so it never uses the no-collection/build-advice form. None of the forms above carry the off switch inline — consumer commands state it separately (e.g. "off switch: --no-docs") alongside the verbatim line, per each command's own plan/approval step.

**Docs-checkout staleness.** A fresh index over a stale checkout still grounds on stale docs, and a read-only docs mount cannot be pulled from inside the container. One pure read — `git -C "$docs_root" log -1 --format=%cI`, skipped silently when the root is not a git checkout — appends the clause when the newest commit is more than **14 days** old. That threshold is shared with `${CLAUDE_PLUGIN_ROOT}/references/read-only-repos.md` §5, so the two move together.

**Shadow detection.** `qmd status` prints `Index: <path>` as its first line, which step 3.5 already parses. When that path is not the user-scope `~/.cache/qmd/index.sqlite`, a project-local `.qmd` index in the current directory is shadowing it — name that cause rather than reporting a generic miss. A `qmd init` run by hand in a working repo silently disables docs grounding, and the failure is otherwise indistinguishable from never having built an index.

## Dispatch — `dispatch-docs-grounder`

Run only when `docs_grounding: ON`. Dispatch the read-only agent (model tier per
the run's `model_routing` — the `detection_model` §2.1 Sonnet chain is the
default for this retrieval agent):

```
→ Agent (subagent_type: "workflows-core:docs-grounder", model: <detection_model; under §10, run_flags.enforced_model>):
  > "Ground this work in the product docs and return the digest:
  >
  > docs_path:       <docs_root>
  > feature_summary: <2–4 sentences: the goal + capability themes for this run>
  > key:        <the PRD/Epic/ticket key, or omit when the run holds none>
  > themes:          [capability themes, or []]"
```

Wait for the digest. On `status: ERROR` or any dispatch failure, treat as
`docs_grounding: OFF` and proceed as the run does without docs grounding (record one line in the final report).
On `status: EMPTY`, proceed the same way; the digest simply adds nothing.

## Consumption

**`grill-rank`** (`/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/brd-intake`):
Feed `docs_references` to the grill as positive grounding (facts to build on,
analogous precedents to model after, building-block altitude/permissions).
**Rank** each `docs_challenges` entry into the command's existing
Impact × Uncertainty gap list — do **not** append. A docs challenge competes for
attention and never adds a question — a *question slot* only where the caller's
grill is capped, which among the grill-rank consumers with a grill is `/idea`
alone (and there this is what preserves its ≤10-question bound). `/create-prd`,
`/update-prd`, `/create-ard` and `/specify` grill to convergence, where ranking
decides what is asked **first**, never how much is asked.

**`/brd-intake` is the one consumer this rule is stated differently for, and it
is a different shape rather than an exception to be tidied away.** It runs no
grill: what it puts to a human is Phase 4's walk over the defect candidates
`brd-reader` returned, and that walk visits every candidate regardless of
ranking. So ranking there reorders the walk and removes nothing — and that
command additionally lets a `docs_challenges` entry be **raised** as an
additional defect candidate, behind the same human confirmation every other
candidate passes through. Raising is not "adding a question": nothing is asked
that a person does not confirm, and the ceiling the no-append rule protects is a
*question budget*, which a walk with no budget does not have. Read the no-append
rule as binding on a capped or convergent grill, which is what it was written
for. Ranking also never pulls a question ahead of its prerequisites: what is
askable now is settled by dependency (`${CLAUDE_PLUGIN_ROOT}/references/grilling-technique.md`),
and rank only orders what is already askable.

**`writer-attach`** (`/epics`, `/release-notes`): Pass the whole digest
(`docs_references` + `docs_challenges`) into the writer agent's input handoff as
`docs_grounding`. The writer uses references for consistency and treats
challenges as authoring cautions.

**`lead-only`** (`/prd-ground`): The digest steers **where to look** and may be
recorded as a **divergence from what the code shows**. It is never evidence, and
it is never passed into a grounding agent's input contract. A document is a
*claim about* behaviour, not the behaviour; a confident, stale page cited as
evidence would satisfy a claim the code does not — the precise failure
`references/grounding-format.md`'s `NOT-PROVABLE` verdict exists to prevent. The
consuming command states the rule and the shape a divergence is recorded in;
this reference fixes only that the mode exists and that it never yields a
citation.

## Invariants

- Read-only; never writes into `$DOCS_PATH`.
- Never blocks; every failure is a silent, non-blocking skip.
- Advisory only — never a gate, never a reviewer BLOCKER.
- Single directory; `${DOCS_PATH:-/workspace/docs}`.
- Index **building and refreshing** happen only in `resolve-docs-grounding` step 3.5, never inside `docs-grounder`, which only probes. A build always requires user consent; a refresh runs bounded at 60s and asks only when that cap is breached.
- The validity gate (step 3) checks the docs root, never the retrieval index — Path B works with no index at all, so gating on one would disable grounding exactly where the fallback still works.
- `resolve-docs-grounding` runs **exactly once per run**, at the earliest phase that shows the `docs grounding:` line; any later invocation in that same run consumes the cached result — it never re-prompts, re-probes, or re-refreshes.
