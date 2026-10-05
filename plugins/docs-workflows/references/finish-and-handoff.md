# Finish & handoff (/document — keyed mode)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The mechanics for Phase 6.2's inline-profiling-branch handling and Phase 8.5's
finish & handoff (squash → opt-in push → copy-paste PR draft). Generic git +
PR-draft logic; the command cites this so it stays lean. Read repo specifics
from the resolved `profile`. This flow does not open the pull request itself: docs repos here are Bitbucket-hosted, and Bitbucket offers no CLI that can create one. Where a host does, the family opens one via `gh` — `workflows-core:phase-handoff` §2.6 in `$SPECS_PATH`, `dev-workflows:code-handoff` §2.6 in a code repo — but no command of this plugin opens one anywhere.

## 1. The branch entering Phase 8.5

Phase 6.2 created (normal case) or renamed (inline-profiling case) the work
branch off the base, named per repo convention. The run carries:
- `base_branch` — the base Phase 6.2 resolved.
- `profile_commit` (C0) — set ONLY for an inline-profiling run
  (`profile_source: generated`): the commit `/docs-profile --inline` made on
  `profile_branch`, the branch it cut — the branch Phase 6.2 renames, by its
  name — both handed back by it (`/document` Phase 0 step 4(c)). Never a
  `git log --diff-filter=A` lookup, which names the newest commit that *added*
  `.dev-workflows/docs-profile.yml` — not necessarily the commit this run made.
  Absent otherwise.

Every git call in this flow runs as `git -C <docs_repo_path>`, the docs
repository's top level (`/document` Phase 0 step 2), never from the working
directory — so every path it names is relative to that top level.

## 2. Squash (always)

Stage the run's uncommitted docs-repo edits first — Phase 8 Agent 1 (doc index /
cross-links) may have edited without committing; the Phase 6.2 clean-tree
precondition means anything uncommitted is this run's work.
Then squash:
- squash base = `profile_commit` (C0) when recorded — keeps the profile-config
  commit as a distinct first commit; otherwise
  `git -C <docs_repo_path> merge-base <base_branch> HEAD`.
- mechanics: `git -C <docs_repo_path> add -- <each path under docs_repo_path the run wrote or edited>`
  → `git -C <docs_repo_path> reset --soft <squash-base>`
  → one `git -C <docs_repo_path> commit -m "<message>"`. Never a path outside the docs
  repository — the implementation-gaps draft in the resolved PRD folder, a screenshot staged under
  `screenshot_staging_dir`, or Phase 8's feedback file under `$SPECS_PATH` — which git refuses
  (`fatal: … is outside repository`) along with every other path in the same `add`.
- message follows `profile.commit_convention` when present (example-docs:
  `<KEY> <summary>`); for a repo with no such field, infer from recent
  `git -C <docs_repo_path> log` / `CONTRIBUTING` (a ticket-key prefix, or a conventional-commits
  `docs:` prefix), else fall back to `<KEY> <summary>`. The key carries
  traceability; the reader-visible changelog still must NOT name it.

## 3. Push (opt-in)

Offer `["Push <branch> to origin now", "Skip — I'll push later", "Cancel"]`.
- **Push** → `git -C <docs_repo_path> push -u origin <branch>`; report the result. `git push` is
  git-protocol, not the REST API the zero-external-API invariant forbids.
- **Skip** → "Branch `<branch>` ready with N commit(s). Push when ready."
- **Cancel** → stop and summarise.
Never force-push. Never call a REST API over HTTPS from this flow. (The `gh` CLI wraps the API rather than calling it over HTTPS and is permitted where a host provides one — but that allowance belongs to pull-request creation, which this docs-repo flow does not perform; see §5 and `workflows-core:phase-handoff` §2.6.)

## 4. Host detection

Classify the docs repo's `git -C <docs_repo_path> remote get-url origin`:
- host `bitbucket.org` → Bitbucket Cloud;
- a self-hosted host with `/scm/` in the path or a bitbucket-style hostname →
  Bitbucket Server;
- host `github.com` → GitHub;
- anything else → other.

## 5. PR draft (always; no API)

Compose the draft and BOTH write and show it:
- **write** to the resolved PRD folder as `pr-draft.md`
  (the resolved PRD folder; ask if
  none) — the same destination convention as the release-notes / bug drafts.
- **title**: per `commit_convention` (e.g. `<KEY> <summary>`).
- **body**: what was documented; the output files; the Phase 6.5
  render-verification summary; deferred style/review/render items; a link back to the PRD.
- **DO-NOT-MERGE banner** at the very top WHEN Phase 5.8 recorded any
  `document-as-spec` / `skip-and-report` decision:
  `> ⚠ DO NOT MERGE until <KEY>-implementation-gaps.md is resolved.`
- **host footer**:
  - Bitbucket (Cloud / Server) → "Open a pull request in the web UI and paste
    the title + body above." (No API.)
  - GitHub → additionally offer a command the USER may run:
    `gh pr create --title '<title>' --body-file <pr-draft path>`, the title in
    single quotes with each `'` it holds written `'\''`, since inside double
    quotes its backticks and `$(…)` would be command-substituted.
  - other → "Open a pull request in your host and paste the title + body above."

For a Bitbucket-hosted docs repo there is no CLI to open the pull request with, so this flow writes the draft and the user opens it. This is a host capability limit, not a policy: the family does open one where a host offers a CLI (`workflows-core:phase-handoff` §2.6 in `$SPECS_PATH`, `dev-workflows:code-handoff` §2.6 in a code repo), and no command of this plugin opens one anywhere, this docs repo included.
