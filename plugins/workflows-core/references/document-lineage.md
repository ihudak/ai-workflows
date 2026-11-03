# Document lineage (shared reference)

Single source of truth for the **lineage record** — which version of each upstream document a document in the specs repository was built from — and for the check a consumer runs on it before it builds on that document. A specification is built from a PRD, its ARDs, its grounding files and, on an Epic, its `epic.md`; a design from a specification. When an upstream is revised after a downstream was built from it, the next command that reads the downstream would build on a stale chain without a word. The record and the check close that gap: the record names the exact bytes each upstream had when the downstream's run read it, and the check walks the chain and **asks** when one of them moved. It never stops a run on its own account.

`scripts/lineage.py` does every read, write and comparison, called as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" <subcommand> …` — `${CLAUDE_PLUGIN_ROOT}` being `workflows-core`, whose file this is, as for `scripts/session-branch.py` in `workflows-core:specs-repo-git`. Its kind table is `scripts/lineage-kinds.json` beside it (§4). Each subcommand prints one JSON object and exits `0`; any other exit is a failure, reported with the first line of its stderr (§5, §6). It is tested in CI by `python3 plugins/workflows-core/scripts/lineage.py --selftest`.

Consumers: `/product-workflows:specify`, `/product-workflows:epics`, `/product-workflows:update-spec` and `/dev-workflows:design` — `grep -l 'document-lineage' plugins/*/commands/*.md` lists them.

## 1. The record

Two frontmatter keys on the downstream document, written only by the script:

```yaml
upstreams:
  - path: specifications/PRD-0042-checkout/prd.md   # relative to $SPECS_PATH
    blob: <40-hex git blob id of the bytes the run read>
    version: null                                    # the upstream's Version, or null where its kind has none
accepted:                                            # written only by a "Proceed" answer (§6)
  - path: specifications/PRD-0042-checkout/prd.md
    blob: <the blob the operator accepted>
```

- **`upstreams:`** lists every input the producing run read, each by the path it was read at. The blob is captured **when the run reads the input**, never when it writes its output, so an input that moved mid-run reads as moved. It is the git blob id **of the bytes the run actually read**: the default branch's blob for an input gated on it, and `git hash-object` of the working-tree bytes for one read from disk — a grounding file, which nothing gates; an `epic.md` `require-on-main` reported `absent`; a copy the run went on with as `pass_amending` or `unmanaged`. A blob id rather than a `Version` because a hand edit that forgets to bump `Version` still changes the bytes, as `/product-workflows:prd-proposal`'s `priced-against` record hashes them.
- **`accepted:`** lists what the operator accepted on this document's behalf (§6): an upstream at its then-current blob, or an unrecorded document at its blob. A later move of that upstream — a different blob — asks again.
- **Every other frontmatter key is kept**, in place and byte for byte: the script rewrites these two blocks and nothing else.
- **A rewrite of the document by its own command re-stamps `upstreams:`** and carries forward each `accepted:` entry whose blob is still that path's blob on the default branch, dropping the rest.

## 2. When an upstream counts as moved

The current copy of an upstream is read from the default branch (`<default-ref>`, as `specs-preflight` resolved it).

1. **Same blob as recorded** → not moved.
2. **A different blob** → the script reads the recorded copy by its blob id (`git cat-file -p`) and compares **live items** by key, per the upstream's row in the kind table (§4). No live item added, changed or withdrawn → **not moved**: a note another command wrote (`/dev-workflows:design`'s `## Engineering review`, an open question ticked, an `Engineering proposal (/design):` answer), a header count or whitespace never asks. Otherwise it moved, and the keys that changed are what the operator sees.
3. **Item keys** are an item's full ID path where its IDs restart under a parent — a specification's `[U02]/[AC01]/[TC03]`, since AC and TC numbers restart per story and per criterion (`product-workflows:specification-format`) — and its own ID where they do not (`[US#2]`, `[AD#3]`). Text outside every item is compared per `## ` section, keyed `§<heading>`; a kind with no item IDs is compared that way alone.
4. **A superseded or withdrawn item** (its heading carries ` — Superseded by` or ` — Withdrawn`) is reported once, as withdrawn, and the items nested under it are not reported again.
5. **The recorded blob is not in the clone** — a shallow clone, rewritten history, or working-tree bytes that were never committed → reported as moved, with *recorded copy unavailable — cannot list items*.
6. **The upstream is absent from `<default-ref>`** → reported as absent, never as moved: the gate that reads that upstream owns that state.

## 3. A missing record, and the coverage boundary

- **A document of a covered kind (§4) with no `upstreams:` key** is reported as having no lineage record: whether its upstreams moved cannot be told. It asks once (§6); *Proceed* records an `accepted:` entry for that document at its current blob, so the same consumer is not asked again until it changes. This is the path every document written before this reference existed takes.
- **The walk follows a document's record only where its kind is covered.** A document of an uncovered kind is a **top** of the walk: it is compared as an upstream — blob and items — but its own record is never looked for, and its lack of one never asks.

## 4. The kind table

`scripts/lineage-kinds.json` is the table, and the script reads nothing else to tell kinds apart: a new kind is one row there. Each row names its files (by basename), whether it is **covered**, the command that **revises** it when it is the stale downstream, whether its header carries a `Version`, its item patterns, the sections excluded as notes, the lines ignored, and where each was measured (`_source`). Summarised:

| Kind | Files | Items | Excluded | Reviser | Covered |
|---|---|---|---|---|---|
| specification | `specification.md` | `[Uxx]` › `[ACxx]` › `[TCxx]` | `## Engineering review`, every `Open questions` heading's section, `- [ ]`/`- [x]` lines, `Engineering proposal (/design):` lines, the `Version` and `Open questions` header lines | `/product-workflows:update-spec` | yes |
| epic | `epic.md` | none — per section | — | `/product-workflows:epics` | yes |
| design | `design.md` | none — per section | the `Version` and `Open questions` header lines | `/dev-workflows:design` | yes |
| prd | `prd.md` | `[US#n]`, `[AC#n]`, `[SM#n]`, `[SMC#n]`, `[UC#n]`, `[FR#n]` | — | `/product-workflows:update-prd` | no |
| ard | `ard.md`, `ard-<area>.md` | `[AD#n]` | — | `/product-workflows:create-ard` | no |
| grounding | `code-grounding.md`, `design-grounding.md` | `[CG#n]`, `[DG#n]` | — | — | no |
| decisions | `decisions.md` | `[VD#n]`, `[CD#n]`, `[AS#n]` | — | `/product-workflows:brd-interview` | no |
| idea | `idea.md` | none — per section | — | — | no |

A file matching no row is compared as plain text, whitespace collapsed. Only `specification.md` and `design.md` carry a `Version`; every other kind is shown by its short blob id (§6).

## 5. `record` — the producer entry point

Executed by a command that writes a document of a covered kind, in two steps.

1. **When the run reads its inputs**, capture them, before reading any of them:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" capture --specs "$SPECS_PATH" --ref <default-ref> --from-ref <path>… --from-disk <path>… --out <capture-file>`
   — every path relative to `$SPECS_PATH`; `--from-disk` for each input the run reads from the working tree, which is how the family's commands read their inputs, and `--from-ref` only for one it reads from `<default-ref>` itself (`git show <default-ref>:<path>`). Either way the blob is that of the bytes read (§1): a working-tree copy equal to the default branch's has the default branch's blob. `<capture-file>` is a file the run creates where `workflows-core:run-flags` puts its temporary files.
2. **After the run writes each document**, and before its handoff stages it, stamp it:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" stamp --specs "$SPECS_PATH" --ref <default-ref> --doc <the document's absolute path> --capture <capture-file>`
   — then, where the run's `upstream-check` (§6) was answered *Proceed*, accept into it:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" accept --doc <the document's absolute path> --check <check-file>`

**Any non-zero exit stops the run** with `<COMMAND>_LINEAGE_FAILED: <the first line of the script's stderr>`, `<COMMAND>` being the calling command's error prefix, before it writes anything further: a document stamped wrongly or not at all would hide a stale chain from every later run.

## 6. `upstream-check` — the consumer entry point

Executed by a command after its own gates have passed the documents it reads (`workflows-core:phase-handoff` `require-on-main`, §3), before its first agent dispatch or other expensive work. The caller supplies `docs` — the documents of a covered kind it is about to build on, relative to `$SPECS_PATH` — and `output`, its own existing output document where one is on disk (the one a re-run rewrites), else none.

1. **Check:** `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" check --specs "$SPECS_PATH" --ref <default-ref> [--output <output's absolute path>] --out <check-file> <docs…>`. A non-zero exit stops the run with `<COMMAND>_LINEAGE_FAILED`, as in §5. The check walks from each document up its recorded `upstreams:` and on through every covered upstream's own record, to the top of the covered chain (§3), and reports every stale link it meets — not only the documents' direct ones.
2. **Nothing stale and nothing missing** — the JSON's `stale` and `missing` are both empty → say nothing more; the Final report carries `Lineage: current` (§7). An `accepted` entry is a link `output` already accepted, and is not asked again.
3. **Otherwise show one block**, then ask. One line per stale link: `<downstream> ← <upstream> <recorded> → <current>: changed <keys>; new <keys>; withdrawn <keys>` — `<recorded>` and `<current>` being the `Version` where the upstream's kind carries one, else the first seven characters of each blob, and an empty kind of change left out; *recorded copy unavailable — cannot list items* in place of the keys where the JSON's `unavailable` is true. One line per missing record: `<doc>: no lineage record — cannot tell whether its upstreams moved`. One line per absent upstream is not shown here: its gate owns it. Then ask, with `escalation-rules` loaded as the caller's **Load the question rules.** step loaded them:

   `choices: ["Stop — revise <highest> first with <reviser> (Recommended)", "Proceed — record that I accepted these upstreams"]`

   — `<highest>` and `<reviser>` from the JSON's `highest`: the stale downstream nearest the top of the chain, and the command that revises it, its `<KEY>` filled with that document's folder key. Fixing the top link first is the only order that settles the chain, since revising a lower document against a stale higher one leaves it stale.
4. ***Stop*** → the run stops with `<COMMAND>_UPSTREAM_STALE: <highest> is behind its upstreams — revise it first with <reviser>`, writing nothing further, its Final report naming each stale link.
5. ***Proceed*** → keep `<check-file>`; after the run writes each document whose walk passed through an accepted link, `record` step 2 accepts into it (§5). A run that stops before writing records nothing, and the next run asks again: nothing was built on the acceptance. The Final report names each accepted link.

## 7. Report line

Every caller's Final report carries one `Lineage:` line: `Lineage: current`; `Lineage: <n> stale link(s), <m> unrecorded — accepted` with each named; `Lineage: stopped — <highest> is behind its upstreams`; or `Lineage: not checked — <reason>` where the run never reached `upstream-check`.
