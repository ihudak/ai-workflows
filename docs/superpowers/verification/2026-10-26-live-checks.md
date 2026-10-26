# Live checks of 2026-10-26 — `docs/superpowers/to-test-on-real-project.md` on the e2e copies

Each run below used the e2e copies (`ihudak-e2e/bookstore`, `ihudak-e2e/bookstore-specs`) through `~/e2e-copies.sh`, with the plugins installed from this marketplace at workflows-core 1.53.0, dev-workflows 4.36.1, product-workflows 3.43.0, docs-workflows 1.22.0 and security-workflows 0.4.0. The session transcripts are under `~/.claude/projects/-workspace-e2e-bookstore/` on the test machine, named by session id. Each item a run settles is deleted from the to-test list in the commit that adds its record here; each defect a run finds goes to `docs/superpowers/to-fix.md`.

## Run 1 — the Epic pickers (B16-3)

**Setup.** Six throwaway PRDs were added to the specs copy's `main` (`a927da9`): PICK-1 to PICK-4 with a flat `specification.md` and 2, 3, 4 and 5 Epic folders, PICK-5 and PICK-6 with no flat spec and 4 and 5. Every Epic folder held `epic.md` and `specification.md`. In one Opus session, from the code copy, each command was typed in turn, and its Epic picker was answered with Esc and `/clear`. `/specify`'s repo-refresh question, asked before its picker, was answered *no refresh*.

| # | Command | Session | Array | Expected | Result |
|---|---|---|---|---|---|
| 1 | `/implement PICK-1` (flat, 2) | `27693491` | 2 Epics, broad slice | the same | pass |
| 2 | `/implement PICK-2` (flat, 3) | `be362f30` | 3 Epics, broad slice | the same | pass |
| 3 | `/implement PICK-3` (flat, 4) | `3c74aa17` | 2 Epics, broad slice, *Another Epic* | the same | pass |
| 4 | `/implement PICK-4` (flat, 5) | `ef0bcd0b` | 2 Epics, broad slice, *Another Epic* | the same | pass |
| 5 | `/implement PICK-5` (no flat, 4) | `acda797d` | 4 Epics | the same | pass |
| 6 | `/implement PICK-6` (no flat, 5) | `fdc91dd0` | 3 Epics, *Another Epic* | the same | pass |
| 7 | `/specify PICK-2` (3) | `e0b4b223` | 3 ● Epics, broad spec | the same | pass |
| 8 | `/specify PICK-3` (4) | `4bde5b38` | 2 ● Epics, broad spec, *Another Epic* | the same | pass |

**The arrays: pass in all eight.** The markers were right too: ○ for an Epic with a specification and no design under `/implement`, and ● done under `/specify`.

**The prose list: failed in all eight.** B16-3 expects "the prose list above the prompt names every Epic in every case", as `workflows-core:epic-picker` *The cap* and all three picker commands require. No run printed it. No text block, and no thinking line shown before the picker, named more than one Epic key. In the four overflow cases (3, 4, 6 and 8), the Epics left out of the array were named nowhere, yet the remainder option reads *Another Epic from the list above*, and case 3's question says "(listed above)". Filed as to-fix LC1.

**Also seen:**
- The `(Recommended)` marker sat on the first ○ row in cases 4, 5 and 6 and was absent in cases 1, 2 and 3, though cases 3 and 4 have the same shape. Filed with LC1.
- Case 1's narration called both Epics "unspecified", though each has a `specification.md` and the picker's own option text says so.
