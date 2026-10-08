# Bounded run (shared reference)

Single source of truth for running a command under a time cap on every host. macOS ships no `timeout` binary, so a call written as a bare `timeout <N>s <cmd>` fails there with `command not found` — and a caller that reads a failed call as "skip" (a slug→clone map skipping a directory, a qmd probe dropping to the fallback) then silently skips everything.

Consumers: every command, agent and reference that caps a call — the slug→clone maps and clone-identity lines of `/dev-workflows:design`, `/dev-workflows:ready`, `/docs-workflows:document`, `/docs-workflows:release-notes`, `/product-workflows:create-ard`, `/product-workflows:epics`, `/product-workflows:idea`, `/product-workflows:prd-ground` and `/product-workflows:specify`; `workflows-core:components` §1; `workflows-core:docs-grounding` step 3.5; and `docs-grounder`.

## The idiom — `bounded <seconds> <command…>`

`bounded <N> <cmd>` is shorthand for this one line, with `<N>` the cap in whole seconds:

```
if command -v timeout >/dev/null 2>&1; then timeout <N>s <cmd>; elif command -v gtimeout >/dev/null 2>&1; then gtimeout <N>s <cmd>; else perl -e 'alarm shift; exec @ARGV or exit 127' <N> <cmd>; fi
```

`bounded 5 git -C <dir> remote get-url origin 2>/dev/null` therefore runs `timeout 5s git -C <dir> remote get-url origin 2>/dev/null` on a host with GNU `timeout`, `gtimeout 5s …` on a macOS host with Homebrew coreutils, and `perl -e 'alarm shift; exec @ARGV or exit 127' 5 git -C <dir> remote get-url origin 2>/dev/null` everywhere else. It is not a shell function: a caller writes the line out, or, in an agent, writes it out once and refers to it as "the bounded-run form" afterwards.

- **The Bash tool call** that runs it sets the tool's timeout to at least (N+5)·1000 ms, so the cap fires before the tool kills the call.
- **Timed out** is exit `124` (`timeout`, `gtimeout`) or `142` (the perl form: the shell reports SIGALRM as 128 + 14). Any other non-zero exit is the command's own failure; a caller that does not distinguish the two treats both as a failed call.
- **A missing `timeout` binary never changes which retrieval rung or branch is taken.** The same call succeeds, fails or times out on a host with or without it.

Verified 2026-10-06 on macOS 26.7 (perl 5.34.1, neither `timeout` nor `gtimeout` installed): `perl -e 'alarm shift; exec @ARGV or exit 127' 1 sleep 3` exits `142`; `… 5 true` exits `0`; `… 5 sh -c 'exit 7'` exits `7`; `… 5 git -C <clone> remote get-url origin` prints the URL and exits `0`; `… 5 <a command not on the path>` exits `127`. Without `or exit 127`, a failed `exec` falls through and perl exits `0` having run nothing; with it, a missing command exits `127`, as `timeout` reports one.
