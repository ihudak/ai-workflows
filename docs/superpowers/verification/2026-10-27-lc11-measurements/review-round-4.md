# LC11 design review, fourth draft

Design: `/workspace/.worktrees/lc11/docs/superpowers/specs/2026-10-27-lc11-run-settles-rejected-push-design.md` (fourth draft).
New scratch evidence: `scratchpad/lc11-review/sb/flow6`. It runs the operator's sanctioned block move through `session-branch.py` with the entry-set `union_copy`. No repository was changed.

**Verdict: READY WITH CHANGES.** N7, N8, m-f, m-g and m-h are resolved, and the N5 NIT is done. No BLOCKER or MAJOR remains. What is left: one MINOR the m-f fallback exposed, and two NITs. All are clarifications a planner can carry, and none needs another design round unless the owner wants the MINOR settled first.

## Status of the third review's items

- **N7 (the entry rule):** resolved. §3.3 is the entry-set rule:
  - headers and entries compared with trailing blank lines stripped;
  - refusal where the headers differ or an entry of `base` is missing from either side;
  - result = `o`, then each entry of `t` that `o` lacks, in `t`'s order;
  - add/add the same, with no `base`;
  - heading shapes pinned per format, so a `## ` of another shape stays inside its entry.

  Dropping my base-header check loses nothing: a header edited on one side already differs between `o` and `t`, and the same edit on both sides is harmless. The three flows are in §4.
- **N8 (§8's merges):** resolved. Every block-shaped path both sides changed is settled from its three blobs, whatever `-X ours` produced; where the function refuses, that source is not merged. One NIT on its wording is below.
- **m-f (the `commit` fallback):** resolved, with its own `unsettled` field, its own §6 line, and the `lift` consequence stated. It exposes m-i below.
- **m-g:** resolved. The upstream write is named in §3.4 step 3 and in §1 rule 8's sweep entry.
- **m-h:** resolved. `*-implementation-gaps.md` is `-merge` in the replay's block and in `ATTRIBUTES`.
- **N5 NIT:** resolved. `numbers` runs on `onto`'s tree, on `c`'s and on the rebuilt one.

## Findings on the fourth draft

### MINOR

**m-i. The operator's sanctioned block move cannot be committed in session-branch mode, and it then blocks every checkout move.**
- `implementation-format` §1 tells the operator to cut a pre-4.1.2 block from the PRD folder's `implementation.md` and append it to the Epic's. That block is on the default branch, so it is in `base` (the version at `merge-base HEAD <tip>`). The cut therefore removes a `base` entry from the working copy, and the rule refuses: measured in `sb/flow6`, *an entry edited or removed*.
- Under §3.8 the PRD file is then `unsettled`. `lift` counts it unpreserved and skips every move of the checkout, the deliverable handoff's switch included. The line's only remedy is "make the working copy hold every entry of both", which means undoing the move.
- Where the removed block is *not* in `base`, the same rule silently restores it, leaving a copy that the reference says `/ready` still counts.
- Population: session-mode users of that hand move, or of any hand fix to a session file. It is small, and nothing is lost.
- *Fix:* in `commit`, where the branch tip's version is the one this worktree was last given (`session-branch-placed.json`'s record equals the tip's blob), the branch has not moved since the overlay was placed. Only the working copy changed, so commit it as it is, removals included. Merge with the entry-set rule only where the branch moved meanwhile, through another worktree or a lift nobody put back. That is the three-way rule's own "only one side changed" case, with `base` set to the placed version.

### NIT

- **"`-X ours` stands for the overwritten shapes alone"** cannot be literal: `-X` applies to the whole merge, not to some paths. Say either that `merge-tree` keeps `-X ours` as today and the block-shaped paths are then replaced from their blobs, or that `-X` is dropped and the overwritten shapes and register files take the session branch's version by path. For any other conflicted path, say whether the source is not merged. In practice no such path exists: a `runs/` record's name carries a hash of its own content, and scan folders are unique.
- **`put-back`'s merge of a foreign working copy** (§8.3: "merged with the branch's version as §8.2 step 2 merges it … listed in `merged`") needs its refusal named. It is presumably `skipped`, the channel §8.3 already uses for a copy it cannot merge.

## Builder questions left

1. **m-i:** use the placed version as the `commit` merge's base where the branch has not moved, or accept the stuck state for hand edits in session mode? *Why:* it decides whether `implementation-format` §1's sanctioned move can be done at all in session mode.

Nothing else needs guessing beyond §6's own list.
