# GIT-G1 evidence

The measurements the GIT-G1 design (`../2026-11-08-git-g1-shared-specs-git-design.md`) argues from. They are snapshots: line numbers are at the commit each names, and the files have moved on since. Re-locate by content before acting on one.

| File | What it is | Measured at |
|---|---|---|
| `contract.md` | The standard call of the five specs-repo git entry points — `specs-preflight`, `commit-artifacts`, `handoff-to-main`, `require-on-main`, `branch-check` — written down from `workflows-core:specs-repo-git` and `workflows-core:phase-handoff`: each one's caller inputs, outputs and flags, ordering obligations, variation points (V1.x–V5.x), interactive points, and what is mechanical versus what needs judgment. | `4fef611b` |
| `audit-A.md` | Thirteen commands — `workflows-core`'s six that run the preflight, `dev-workflows`' six, `/security-workflows:scan` — compared with the contract: every departure classed R (a variation the references define), P (purposeful, with the command's reason), D (drift) or U (unclear), each command's readiness, and the options the shared step must offer. | `4fef611b` |
| `audit-B.md` | The same for `docs-workflows`' six commands and the idea-route ladder (`/idea` to `/update-spec`). | `de2da52f` |
| `audit-C.md` | The same for `/epics`, the two knowledge-base commands, the two proposals and the six BRD-route commands. | `de2da52f` |

Each audit's §1 lists the latent bugs it found. Batch B36 (`workflows-core` 1.78.16, `dev-workflows` 4.59.7, `docs-workflows` 1.35.9, `product-workflows` 3.78.9) fixed them in the commands as they stood, so those sections describe the tree before that batch. The options lists (§2) and the readiness verdicts (§3) are what the design takes forward.
