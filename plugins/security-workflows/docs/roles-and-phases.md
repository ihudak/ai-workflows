# Roles and phases

[Workflow overview](workflow.md) shows where the command sits in the family's delivery. This page says what each of its two roles is accountable for, what each decides, and, at the end, what its cost-attribution phase means when you see it on a cost report or in a run's output.

**A run's role is fixed by its address and flags, never chosen.** `/security-workflows:scan` sets it at Phase 0 step 2: **`dev`** for a key run without `--triage` or `--verify-fixes` — the Dev's pre-merge scan, or an `--import` for a unit — and **`sec`** for every other run. It writes the role into every run record it writes, beside every decision it records, and passes it to its cost entry. The plugin enforces no access control: who may confirm a decision is a matter of team practice, and the register records who decided, in which role, and when.

## Dev — the scan before the merge

- **Owns:** the security scan of their own Epic's branch, before its pull request merges, and the decision on each finding that scan raises.
- **Runs:** `/security-workflows:scan <EPIC>`, from the code repository the Epic was implemented in — a change scan of the Epic's branch over its base. `/dev-workflows:implement` offers it after `/dev-workflows:conformance`, before the merge, and `/dev-workflows:conformance` offers it where it decided no fix, for each repository whose Epic branch it traced before the merge; neither runs it for you. For a report made by running `/claude-security` directly, `--import <dir>` with the Epic's key records it under the same role.
- **Decides,** in one triage batch: **fix**; **decide later**; **false positive**, naming the `file:line` of the guard that defeats the exploit scenario and one line of why; or **accept the risk**, with one line of why and a review-by date, 90 days by default. Possibly-same matches are always asked one by one.
- **Produces:** the findings in the repository's register, a block in the Epic's `_security.md`, and, for each finding marked fix, a follow-up in the Epic folder's `follow-ups.md`, starting from Claude Security's patch where it made one.
- **Hands over:** each fix to `/dev-workflows:implement <EPIC>`, which continues on the Epic's branch while its pull request is open, so the fix joins that pull request and goes through the same baseline, review and record as any change; then the pull request's review and merge, as usual. Every false positive and accepted risk the Dev records **awaits security review**, and takes effect at once.
- **Cost phase:** `security-audit`, role `dev`.

## Security Engineer (`sec`) — the audit

- **Owns:** each code repository's security across its Epics: the whole-repository scan, the closure of fixes on evidence, and the review of what Devs decided.
- **Runs:**
  - `/security-workflows:scan <repo-path>` — a codebase scan of the whole repository at `medium`, or of the area Claude Security's own scope question narrows it to;
  - `--verify-fixes`, once a fix has merged — a codebase scan at the default branch's head, scoped to the changed files of the findings being fixed, in a temporary worktree, so the Security Engineer's checkout is never switched;
  - `--triage`, which scans nothing;
  - `--import <dir>` without a key.

  `--verify-fixes` and `--triage` take a key too, narrowing the register to the findings raised for that unit; the run's role stays `sec`.
- **Decides:** in every `sec` run's triage, each decision awaiting security review — *Confirm* it, *Overrule — fix it*, or *Overrule — decide later* — each accepted risk past its review-by date, decided again, and each finding still open. It confirms or refuses the closures a scan proposes, such as a fix the default branch received only through a squash. The false positives and accepted risks it records itself are confirmed at once.
- **Produces:** the register's whole-repository findings, each fix closed on evidence, and, for each finding it marks fix, a follow-up for the unit on a run addressed by a key, or a `/dev-workflows:implement` prompt line in the run's report on a run on a repository path, which has no unit to address a follow-up to.
- **Cost phase:** `security-audit`, role `sec`.

## A Dev is never blocked

A `dev` run's *False positive* or *Accept the risk* takes effect at once: a false positive is not fixed, and an accepted risk waits for its date. It is recorded `confirmed: false`, **awaiting security review**, until a `sec` run confirms it by deciding the same status again, which records `confirmed: true`, or overrules it. **Nothing the Dev does waits for that review**: the Dev's pull request is reviewed and merged as usual, no run stops because another run's register changes are unmerged, and the register reaches the specs repository's default branch as bookkeeping, never by a pull request of its own.

That is a deliberate price. Until the Security Engineer reviews it, a risk the Dev accepted stays accepted. The register shows it plainly: `register.md` lists every such decision in its *Awaiting security review* section, every `sec` run's triage puts each one to the Security Engineer, and each run's report names them. A `dev` run's own triage shows none of them, since only a `sec` run decides them.

## Cost-attribution phases

Every cost-emitting command tags its cost line with a `phase` and a `role`. This plugin's one command reaches one phase. The family's other lifecycle phases belong to the companion plugins' commands, and `workflows-core:cost-emission` §7 is the authority for every pair.

### security-audit

Emitted by `/security-workflows:scan`, role `dev` for a key run without `--triage` or `--verify-fixes` and `sec` for every other run. The command passes `phase: inferred, role: inferred` with the run's role as `run_role`, and the cost phase resolves the pair from it: the role cannot be read from disk, because the run record that carries it is written only by a run that changed the register. Being in this phase means a code repository's security is being audited: a scan, an import, a triage or a fix verification recorded in its register.

It is also reached by inheritance, without a role: `/workflows-core:prompt`, `/workflows-core:feedback`, `/workflows-core:prompt-brainstorm` and `/workflows-core:prompt-grill-me` correcting a scan run inherit its phase and record the role as `n/a`, since `run_role` lives in the scan run alone. [Session cost](reference/session-cost.md) says where each entry lands.
