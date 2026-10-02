# Resume and checkpoints

A long-running command ends by doing two separate things: it flushes a small pointer file to disk recording exactly where things stand, then it suggests — never performs — the right context action for what comes next, `/compact`, `/clear`, or a session `/rename`. Both are guidance only; the plugin never invokes any of those three itself. The point is to stop relying on you to remember to ask "am I ready to compact or clear" — the pipeline does the disk-flush itself and hands you the choice already framed. The mechanism itself is shared across the whole family; this page describes what `dev-workflows`'s own five commands do with it.

## What `resume.md` is for

`resume.md` exists so you can pick a run back up in a fresh session without re-deriving what the last one already established — what command ran last, what it produced, and what to run next — instead of scrolling back through a compacted or cleared transcript, or worse, re-reading every artifact from scratch to reconstruct where you left off. It is a **"last known position" pointer, overwritten every run, not an append log** — there is exactly one current answer to "where am I," not a history of every past one. It stays intentionally tiny:

```markdown
# Resume — <KEY>[ / <EPIC-KEY>] (<role>)

- **Last completed:** <command> <args> — <phase or 'command complete'> (<ISO datetime>)
- **Artifact:** <relative path to the deliverable just written/committed, or 'none (read-only)'>
- **Next step:** <the exact next command from ### Next step, or 'PRD fully processed'>
- **Suggested session name:** <KEY>-<slug>-<role>   (omit this line on a run whose own `### Context hygiene` block carries no `/rename` suggestion — never the case for this plugin's own five commands: the three that write a `resume.md` at all, `/design`, `/ready` and `/implement`, each print the line, and `/vuln` and `/upgrade` write no pointer; the companion `product-workflows` plugin's `/create-prd` is the family's worked example of a command that writes the file and omits the line, and it is omitted for its phase length rather than for want of a key, which it takes as a mandatory argument)
- **Carry-forward decisions:** <0–N one-line decisions the next phase needs that are NOT already in the artifact; 'none' if none>
```

Any secret, credential, token, or other sensitive value that might otherwise land in the `Carry-forward decisions` line is redacted before writing — a resume pointer records what to do next, never a value worth protecting.

**When it's written.** The write is unconditional for any PRD-scoped run, save one carrying `specs_git: misrooted` (a `$SPECS_PATH` the run found misplaced), and it happens first — before the terminal `commit-artifacts` step, but only after the deliverable artifact is already saved or committed, and after the feedback, follow-up, and cost phases have all run. That ordering matters: several commands compose their printed Final Report before their follow-up and cost phases even run, so tying the write to the printed report would land it before the cost entry it's supposed to follow, and it would never get committed, since `commit-artifacts` itself runs after cost. The canonical terminal order is deliverable and handoff, then feedback, then follow-ups, then cost, then `resume.md`, then `commit-artifacts`. Whether the suggestion (below) actually fires or not, the write itself always happens — **prepare always, suggest adaptively.**

**Where it lands.** Three tiers, walked in order: `$SPECS_PATH` writable with the PRD directory matched → `<PRD-dir>/dev-workflows/resume.md`, the primary case; `$SPECS_PATH` writable but **no PRD directory matched** → the file is skipped outright and the run relies on the printed `### Next step` instead; and `$SPECS_PATH` not writable → skipped, with a one-line warning that no resume pointer could be persisted and you should set it.

**Which runs skip it entirely.** `/implement` in direct mode has no PRD to anchor a pointer to, and neither does the companion plugin's `/docs-workflows:document` in doc-edit mode. `/vuln` and `/upgrade` are non-pipeline runs whose durable state is the branch or PR already on disk. The companion plugins' `/product-workflows:idea` and `/workflows-core:frames` do resolve a PRD folder, but neither is a phase a later run resumes — `/product-workflows:idea` hands its brief off in the same run, and `/workflows-core:frames` repairs a frame-set index rather than advancing the pipeline — so a pointer would only go stale.

## The suggestion: `/compact` or `/clear`

Every next-step option a command offers already carries a role label — see [Roles and phases](../roles-and-phases.md) for what PM, PA, PE, and Dev each own. The context-hygiene suggestion reads those same labels rather than hardcoding a per-command verdict:

- **Staying in the same role** for the next step (`/design E1` → `/design E2`, Dev → Dev) → **`/compact`** — the context is still relevant, so keep the thread going.
- **Moving to a different role** (the companion `product-workflows` plugin's `/product-workflows:epics` PE → `/design` Dev) → **`/clear`** is the better default when one person is wearing both hats, since the prior role's reasoning becomes noise for the next one; `/compact` still works fine if you're continuing right away yourself.
- **The next step could go either way** (the companion `product-workflows` plugin's `/product-workflows:create-prd` → PM `/docs-workflows:release-notes`, or handing off to PA/PE) → both branches are named explicitly: continuing as the same role suggests `/compact`, handing off — even to yourself — suggests `/clear`.
- **You're done, or ending the session** → no suggestion at all.

## Mid-phase checkpoints and big non-pipeline commands

A run doesn't have to finish to earn a checkpoint. `/implement`'s own mid-phase checkpoint (Scope-to-N, or per-Epic) suggests `/compact` to free up budget before continuing — never `/clear` here, since a mid-command checkpoint is never a role transition. `/vuln` and `/upgrade` are large, non-pipeline commands with no role transition of their own: each gets a plain end-of-run `/compact` suggestion near its maintenance handoff, and neither writes a `resume.md`, since their durable state already lives in the branch or PR they produced.

## The `/rename` aid

A PRD key is first available at the companion `product-workflows` plugin's `/product-workflows:idea`, and the commands that print a suggested `/rename <KEY>-<slug>-<role>` line are the PA/PE/Dev ladder — `/design`, `/ready`, `/implement` here, the companion `product-workflows` plugin's `/product-workflows:create-ard`, `/product-workflows:epics`, `/product-workflows:specify`, and the companion `docs-workflows` plugin's `/docs-workflows:document` and `/docs-workflows:release-notes` — plus that plugin's two PM effort-proposal commands, `/product-workflows:prd-proposal` and `/product-workflows:brd-proposal`. The line lets you find this session again later in `claude --resume` by name instead of by scrolling. `<KEY>` is the key that named the folder the run resolved, and `<role>` is the lane tag of the command that just finished — pm, pa, pe, or dev. **That set is not "every command that takes a `<PRD>`"**: `/implement` in direct mode takes no address, `/docs-workflows:document` in doc-edit mode takes none either, and both of those modes write no pointer at all. `/product-workflows:idea` and `/product-workflows:create-prd` are excluded from this aid, and the reason is the phase rather than the key — each of those two takes a mandatory key as its first argument and refuses without one, so a PM run always has a key it could name the session after. The ideation phase is simply short enough that naming the session isn't worth automatically suggesting.

## The contract

Five rules bound everything above: it is **guidance-only** — `/compact`, `/clear`, and `/rename` are always suggested, never invoked by the plugin itself; the disk flush is **prepare-first** — unconditional for a PRD-scoped run, save one carrying `specs_git: misrooted`, and always ahead of the suggestion it accompanies, so acting on the printed suggestion is always safe; the compact-versus-clear split is **role-aware through a single graph**, reading role labels from the next-step offer rather than duplicating that graph here; the whole mechanism is **mode-aware**, degrading to a plain optional `/compact` note (or nothing at all) on a direct, doc-edit, non-pipeline, or pre-PRD run — for one of three reasons, as the skip list above already separates them: there is no PRD anchor to write a pointer against, or the run is non-pipeline and its durable state is the branch or PR already on disk, or there is an anchor and the run is not a phase a later run resumes; and it **never blocks** — the guidance is a nudge appended to the end of the Final Report, exactly like the next-phase offer it sits beside.
