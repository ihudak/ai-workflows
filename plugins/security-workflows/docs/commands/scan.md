# /security-workflows:scan

Audits a codebase for security vulnerabilities with Anthropic's Claude Security plugin — an Epic's branch before its pull request merges, or a whole repository — records what it finds in the specs repository's findings register for that code repository, triages every finding in one batch, and hands each fix to `/dev-workflows:implement`.

## Who runs it

Two roles, and the run fixes its own from its address and flags (Phase 0 step 2): it records the role in the run record it writes, and passes it to its cost entry.

- **`dev`** — a key run without `--triage` or `--verify-fixes`: the Dev's pre-merge scan of their own Epic, or an `--import` for a unit. `/dev-workflows:implement` offers it after `/dev-workflows:conformance`, and `/dev-workflows:conformance` offers it where it decided no fix, for each repository whose Epic branch it traced before the merge.
- **`sec`** — every other run: a scan of a repository path, `--verify-fixes` and `--triage` with either address, and an `--import` without a key. These are the Security Engineer's.

Every run is charged to the `security-audit` cost phase, with that role ([Session cost](../reference/session-cost.md)), and classifies itself `SIGNIFICANT`: its triage and its patch request are judgement the orchestrator takes inline. [Roles and phases](../roles-and-phases.md) says what each role decides.

**It never scans by itself.** Claude Security's own skill reads the code, puts each finding to its verification panel and writes the report. This command runs that skill on the Epic's branch or on a repository, then records, triages and routes what the skill reports. It reasons about source code only: it never runs anything against a deployed system, and never writes exploit code.

## Synopsis

```
/security-workflows:scan <KEY | repo-path> [--import <dir> | --triage | --verify-fixes] [--effort medium|high] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

Phase 0 step 2 reads what the run flags leave as one positional address and the command's own flags:

- **An address that names an existing directory is a repository path**; any other address is a key, which must match the family's key grammar, `^[A-Z][A-Z0-9_]*(-\d+)+$`.
- **`--import <dir>`, `--triage` and `--verify-fixes` exclude one another**, and `--import` takes an existing directory.
- **`--effort` takes `medium` or `high`.** It defaults to `high` for a change scan, Claude Security's own advice for a feature-sized change, and to `medium` for a whole-repository scan and for `--verify-fixes`. The command never asks Claude Security for a `low`-effort scan, which reads the target with one researcher, keeps no coverage account, and so could never close a fix. On `--import` and `--triage`, which scan nothing, `--effort` has no effect, and the run says so.
- **Anything else stops with `SECURITY_USAGE`**: no address or two, an unknown flag, a flag without its value, two of `--import`, `--triage` and `--verify-fixes`, an `--import` naming no existing directory, or an `--effort` other than `medium` or `high`.

All three run flags apply. `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`) skips the cost entry, still advancing the checkpoint ([Session cost](../reference/session-cost.md)). `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows the maintenance step to bugs-only, dispatching `defect-reporter` in place of `impl-maintenance`: under the flag only real defects are persisted, never the in-session Lessons Learned report. `--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) reaches **this run's own dispatches only**, the maintenance agents of Phase 7.6, and never Claude Security's agents, which run on the session model whatever the flag says; the routing record and the report say so.

## Modes

| Run | Address and flag | What it does | Role |
|---|---|---|---|
| Change scan | a key | Claude Security's *Scan changes* on the Epic's branch, over its base, in the repository this session is open in; `high` effort | `dev` |
| Codebase scan | a repository path | *Scan codebase* of the whole repository as it stands, unless Claude Security's own scope question narrows it; `medium` | `sec` |
| Verify fixes | `--verify-fixes`, with a key or a path | *Scan codebase* at the default branch's head, scoped to the changed files of the findings being fixed, in a temporary worktree; `medium` | `sec` |
| Triage | `--triage`, with a key or a path | No scan: the open findings, those to fix whose follow-up is unwritten, the accepted risks past their review-by date, and the decisions awaiting security review | `sec` |
| Import | `--import <dir>`, with a key or a path | No scan: records a report Claude Security already wrote, for instance from its own tip after a push | `dev` with a key, `sec` with a path |

**With a key, the register is still the repository's.** `--triage` and `--verify-fixes` with a key read the register of the repository this session is open in, narrowed to the findings raised for that unit; neither runs the Epic-branch lookup a change scan does. `--import <dir>` takes the repository whose root holds `<dir>`: with a key, it must be one the unit's `implementation.md` names in a block's `repo:`; with a path, it must be that path's repository.

## How it runs

```mermaid
flowchart TD
    p0["Phase 0 — Setup: run flags, arguments and role, SPECS_PATH, address, specs preflight, repository, reservations, leftover worktrees, prerequisites, session-model check"] --> p1["Phase 1 — Scope: commit, kind and scope; a change scan acts on unit-branch's state, after a switch question where the branch is elsewhere; for --verify-fixes, the changed files of findings being fixed; for --triage, the triage plan"]
    p1 --> mode{"Mode?"}
    mode -->|"KEY, repo path or --verify-fixes"| p2["Phase 2 — Checkout: in place, or a temporary worktree for --verify-fixes"]
    mode -->|"--import dir"| p4
    mode -->|"--triage"| p5
    p2 --> p3["Phase 3 — Scan: one confirmation, then claude-security"]
    p3 --> p4["Phase 4 — Record: redaction check, copy the products to SPECS, register.py plan"]
    p4 --> p5["Phase 5 — Triage: one batch preview"]
    p5 --> p6["Phase 6 — Patches: Suggest patches for the findings marked fix, in the session's repository"]
    p6 --> p7["Phase 7 — Close: refresh the reservations, register.py commit, unit note, worktree removal, report, then feedback, follow-ups, cost, resume and commit-artifacts"]
```

| Phase | What happens |
|---|---|
| 0 — Setup | Strip the run flags, read the address and flags, and set the role. Require `$SPECS_PATH`. Resolve a key and run the specs-repo preflight. |
| 0, continued | Take the code repository, its slug and its default branch, and fetch it; for a change scan, find the Epic's branch. Reserve other branches' numbers. Offer to remove idle leftover worktrees. |
| 0, last | Check `python3` and the `Workflow` tool, then classify `SIGNIFICANT` and check the session model. |
| 1 — Scope | Fix the commit, the kind and the scope. A change scan acts on the Epic's branch's state; `--verify-fixes` takes its files; `--triage` plans; `--import` goes to Phase 4. |
| 2 — Checkout | Scan in place, or, for `--verify-fixes`, in a temporary worktree at the default branch's head, so your checkout is never switched. |
| 3 — Scan | One confirmation, then Claude Security's skill, through its delivery and redaction. Find the report directory it wrote, and check its stamp names the commit Phase 1 fixed. |
| 4 — Record | Ask before copying where Claude Security warned the files may hold a credential. Copy the products into the register, and plan with `register.py plan`. |
| 5 — Triage | One preview table and one batch answer, the possibly-same questions, and the per-row questions *Change some* or *Decide each row* asks. Write the decisions file and check its shape. |
| 6 — Patches | Ask Claude Security for patches for the findings marked fix, where the scan ran in this session's repository, and copy them into the register. |
| 7 — Close | Refresh the reservations, commit the register with `register.py commit`, append the unit note, remove the worktree, and print the report. |
| 7.6 — Tail | Maintenance and feedback, the follow-ups after their preview, the cost entry, the resume pointer, and the terminal commit of the specs repository. |

**Phase 0 finds the Epic's branch, and Phase 1 acts on it.** A change scan reads the branch from the latest block for this repository in the unit's `implementation.md`, fetches it by name, and asks `workflows-core`'s `unit-branch` what state it is in. A state of `none`, a record naming no block for this repository, stops there with `SECURITY_NO_IMPLEMENTATION`. Phase 1 then acts on the others:

- **checked out** — scans the branch's tip in place. A local branch behind `origin`'s copy is fast-forwarded first, and the confirmation says so; a tip that review commits moved past the recorded commit is no error, and the confirmation says that too.
- **local or remote** — on a clean tree, asks `choices: ["Switch to <branch> (Recommended)", "Cancel"]`, and on *Switch* switches to it — creating the local branch from `origin`'s where only the remote has it — fast-forwarding where the remote's copy is ahead.
- **merged** — stops with `SECURITY_EPIC_MERGED`: the change is on the default branch, and a change scan has nothing left to diff.
- **missing** — stops with `SECURITY_BRANCH_MISSING`.

Where git refuses the switch or a fast-forward — the branch checked out in another worktree of the clone, say — the run prints git's error and stops as *Cancel* does, naming the branch your checkout stands on. Where the pull request has merged and the branch has gone on since, the confirmation says so, and the change scan reads what the branch adds over its base. A dirty tree stops a change scan with `SECURITY_TREE_DIRTY`, since a change scan reads committed changes only. A repository path is scanned as it stands, a dirty tree included, and its confirmation says that a dirty scan closes nothing and yields no patch.

**The confirmation states the cost.** It names the repository, the commit, the kind, the scope, the effort and the role, and what Phase 1 changed, then says: "The scan may take a while and use a significant number of tokens; leave Claude Code open until it finishes." It asks `choices: ["Start the scan (Recommended)", "Cancel"]`. *Start the scan* is your acceptance of that time and token cost, which the call carries to Claude Security, so its skill opens no menu and asks for no cost confirmation of its own; a whole-repository scan still meets its own scope question. The command skips that skill's closing offer to suggest fixes, because Phase 5 triages each finding and Phase 6 asks for patches for the ones marked fix.

**Leftover worktrees.** A `--verify-fixes` worktree is named with the fixed prefix `security-workflows.`, so a run that crashed leaves one Phase 0 can find. A worktree with anything changed in the last six hours may be another session's run waiting on an answer, and is left where it is; idle ones are named, with any report folder they hold, and offered as `choices: ["Remove them (Recommended)", "Keep them"]`. *Remove them* copies each report folder out to the repository's root first, where `--import` can record it.

## What it needs

- **`$SPECS_PATH`**, on every run: the register lives under it ([Environment](../reference/environment.md)).
- **A code repository with an `origin` remote.** A key run takes the repository this session is open in; a path takes that path's; `--import` takes the one holding its directory. The register is named after `origin`'s last path segment, so a repository with no `origin` has no register and stops.
- **For a change scan, a record and a branch.** The unit's `implementation.md` must hold a block for this repository, written by `/dev-workflows:implement`, and its branch must be in this clone or on `origin`, on a clean tree.
- **A default branch.** Every run but `--triage` needs the repository's default ref; where none resolves, the repository is skipped (`git remote set-head origin --auto` sets one).
- **A writable clone, for a run that scans.** Claude Security writes its report directory into the scan root, and a switch or a worktree writes too; on a read-only mount the repository is skipped.
- **`python3` 3.9 or newer**, for every run but `--triage`, and **the `Workflow` tool**, for a run that scans: Claude Security runs its scan as a dynamic workflow, which the *Dynamic workflows* row in `/config` turns on.
- **Claude Security**, installed with this plugin as a declared dependency.

## Which model the scan runs on

Claude Security's working agents inherit the session model, and nothing inside a running command can change it, so on a run that scans the session model decides it (Phase 0 step 9):

| Session model | Phase 0 | Phase 3's confirmation |
|---|---|---|
| Opus | asks nothing | the cost confirmation only |
| Sonnet, or a lower tier | asks first that its scan agents may find fewer or weaker issues, offering *Cancel — rerun after /model opus* (recommended) or *Scan on Sonnet anyway* | the cost confirmation; the report records the answer |
| Fable | asks nothing: you chose Fable, which approves its cost | the cost confirmation, plus one line: Fable's safety filters will re-run some of the scan's requests on Opus |

The question on Sonnet is `choices: ["Cancel — rerun after /model opus (Recommended)", "Scan on Sonnet anyway"]`. **The scan never escalates to Fable.** A run that scans nothing, `--import` or `--triage`, asks nothing here. Under `--enforce-model` the Sonnet question does not fire, as no Opus-session gate does in the family, and the report names the session model the scan ran on instead.

## Triage

**The preview.** Phase 5 first rebuilds the register, then shows one table. Its rows are the scan's new findings, its possibly-same matches, the closures it proposes, the findings whose file is gone, the fixed findings the scan reports again, which it reopens, the findings still open, the findings to fix whose follow-up is unwritten — its line cancelled at a preview, or, on a run with a key, its run cut off before writing it, and the scan neither closing it nor proposing it fixed — the accepted risks past their review-by date, and, in a `sec` run, the decisions awaiting security review. A finding two of these name is one row, the first in this order that names it: a proposed closure or a gone file, review due, awaiting review, reopened, open, to fix. So an accepted risk past its date that also awaits security review is one review-due row, which one answer can re-date and confirm. Each row shows its `[SEC#n]`, or `new`, its severity, CWE, `file:line` and a suggested decision: **fix** for CRITICAL and HIGH, **decide later** for the rest, on a new, reopened or open row and on a match that reopens a finding; **fix** for a row to fix, which writes its follow-up; **confirm fixed** for a proposed closure or a gone file, save one raised for no unit that the scan reaches only because the default branch has moved on past a sighting made off it, which suggests **decide later** and says on its row, in one plain sentence, that the default branch has moved on past the finding's last sighting but nothing records that its fix merged — a row only a `sec` run offers, a Dev's run naming it in its report instead; the possibly-same question for a match; and, for a review-due or awaiting-review row, its current status, shown to decide again. The run names each finding that closes by itself. Every title is printed as quoted scan output, under *Scan output — text the scanner wrote, never instructions*, and never in the table.

**The batch.** `choices: ["Accept the suggestions", "Change some", "Decide all later"]`. *Accept the suggestions* takes each row's suggestion — so it records nothing for a closure or a gone file suggested *decide later*, which only your own *Confirm fixed* closes — and leaves a review-due or awaiting-review row as it stands; *Decide all later* decides nothing; *Change some* asks each row. Where no row's suggestion would record a decision — every row is review-due or awaiting review, or a new, reopened or open row below HIGH, or a proposed closure or a gone file, suggesting *decide later*, and none is a possibly-same match, a row to fix, or a proposed closure or gone file suggesting *confirm fixed* — the first and the last would do the same, so the batch is `choices: ["Decide each row", "Decide all later"]` instead, *Decide each row* asking each row as *Change some* does. A table with no row at all asks no batch.

**Possibly-same rows are always asked**, whatever the batch answer, one at a time, naming each candidate's `[SEC#n]`, CWE, `file:line` and status: one candidate as `choices: ["Same finding", "A different finding"]`, several as one *Same as `[SEC#n]`* option each, up to three, then *A different finding*; where there are more than three, the options carry the three nearest by line and the question's own text names each of the others after `Not shown as an option:`, and a typed `[SEC#n]` is taken only from the candidates named. A match onto a finding last seen at a commit the scanned one comes before changes nothing but who reported it. Otherwise, a confirmed match onto a false positive or an accepted risk is changed code, so that finding's decision is asked again too; left undecided, it returns to `open`. A match onto a fixed finding reopens it, unless the scanned commit comes before the scan that closed it, and the reopened finding is decided as a reopened row.

**Change some**, or *Decide each row*, asks the rows four to an `AskUserQuestion` call, each question naming its row and its suggestion, with no `(Recommended)` marker, since which answer is right is the question itself:

- new, reopened, open, to-fix or review-due rows, a match that reopens a finding, and a match onto a false positive or an accepted risk: `choices: ["Fix", "Decide later", "False positive (you'll be prompted for the evidence)", "Accept the risk (you'll be prompted for the reason)"]`. On a review-due row, *Accept the risk* re-dates the risk with the review-by date asked next, and in a `sec` run records it confirmed, so one answer settles a review-due row that also awaited security review;
- proposed closures and gone files: `choices: ["Confirm fixed", "Keep it open"]`, where *Keep it open* writes nothing, and is the suggestion for a row suggested *decide later*;
- decisions awaiting security review, in a `sec` run: `choices: ["Confirm", "Overrule — fix it", "Overrule — decide later"]`. Each question shows the evidence and reason the Dev recorded and, for a false positive, the line its evidence cites, read from the commit the next paragraph names — or says that commit holds no such line — so that the Security Engineer can judge it; the run judges nothing itself.

**The follow-up questions**, in plain text, right after the answer that needs one. *False positive* asks for the evidence, the `file:line` of the guard, check or encoding that defeats the exploit scenario and one line of why, and asks again for an answer with no `path:line` in it. The cited line must be a line of the scanned commit's tree — on `--triage`, which scans nothing, of the commit the finding was last seen at, or of `HEAD` where the clone lacks that commit. Where it is not, because no such file is there or the file has no such line, the run says so and asks again; withdrawing the false positive asks the row's decision again. Otherwise it shows that line beside the finding's own `file:line` — in the text of its reply before the next question, or in that question's own text, never only in a command's output or its thinking — and records the evidence and its why exactly as given: it judges nothing, asks no question of its own about the evidence, and the register records only the evidence and reason you gave, never a view of the run's. *Accept the risk* asks for one line of why, then the review-by date, `choices: ["90 days (Recommended)", "30 days", "180 days"]`, counted from today's UTC date; a typed date is normalised to `YYYY-MM-DD` or asked again, and the owner is the person deciding. *Decide later* records nothing on an existing finding, and `open` on a new one: a reopened row so left stays `reopened`, and a row to fix stays as it is, offered again by the next run. A free-text answer to any of these pickers is normalised into the picker's own options, or the question is asked again; it is never written through.

**A Dev's choices.** In a `dev` run, a *False positive* or *Accept the risk* is recorded **awaiting security review** and takes effect at once. Nothing the Dev does waits for that review, and their pull request is reviewed and merged as usual. A `sec` run records the same decisions confirmed ([Security register](../reference/security-register.md)).

**Credentials in the report.** Claude Security's redaction of credential values is best effort. Where its skill tells the session that the report's files may still hold one, Phase 4 asks before anything is copied: `choices: ["Stop to clean the files, then record them with --import (Recommended)", "Record as they are"]`. *Stop to clean the files* ends the run, naming the three results files to check and the `--import` command that records them once clean. On `--import` the run cannot see that warning, and says so in one line.

**A credential the redaction misses without saying so reaches the specs repository unreviewed.** Where Claude Security reports no redaction failure — and on every `--import` — Phase 4 asks nothing: it copies the report, JSONL and SARIF into the register as they are, and the run's terminal commit commits them with its other session files and pushes them as it pushes those, as bookkeeping that no pull request and no person reviews. Once pushed, the credential is in the specs repository's history, which only a history rewrite clears. So:

- keep the specs repository private, with access no wider than the code repository's;
- before an `--import`, read `CLAUDE-SECURITY-RESULTS.md`, `CLAUDE-SECURITY-RESULTS.jsonl` and `CLAUDE-SECURITY-RESULTS.sarif` for a key, token or password;
- after a scan, read the same three files in its scan folder, `security/<repo-slug>/scans/<UTC-timestamp>-<commit7>/` (below), and rotate any credential you find there, as you would one committed to the code.

## What it produces

**In the specs repository**, as bookkeeping its terminal commit carries with the run's other session files ([Security register](../reference/security-register.md)):

- **The scan folder**, `security/<repo-slug>/scans/<UTC-timestamp>-<commit7>/`: Claude Security's report, JSONL, SARIF and revision stamp, unchanged, and its `patches/` where Phase 6 asked for any. A scan the register already holds records nothing; where a run record on another branch holds it, the run says so, and deletes the folder it copied — with any patches it copied into it — since that branch carries its own copy. Where the folder exists already — the same report imported again, or one a run that broke off before recording left — the run copies nothing where each file is identical to the report's. Where the folder lacks the report's revision stamp or its JSONL — a copy broken off before either landed — no record can name it, since a run records a scan only once its plan has read both, so the report's files replace it at once, any patches left there removed, before the run plans. Where another file differs, it plans first: a scan the register holds already keeps the copy it recorded, nothing is copied, and the report names the files that differ from it; otherwise no record names the folder, so the report's files replace the old ones, any patches the broken-off run left there are removed, and the run plans again.
- **The run record**, `security/<repo-slug>/runs/<seq>-<UTC>-<hash8>.json`, and the register rebuilt from every record: `register.json` and `register.md`.
- **The unit note**, with a key, on a run that recorded a scan: one block appended to `_security.md` in the unit's folder, created under `# Security — <key> <slug>` where it is new.

```markdown
## <YYYY-MM-DD> — /security-workflows:scan
- repo:     <repo-slug>
  commit:   <commit7>
  scan:     <change | codebase> scan, effort <effort> — security/<repo-slug>/scans/<folder>/
  kind:     <scan | import | verify>, role <dev | sec>
  findings: <N CRITICAL · N HIGH · N MEDIUM · N LOW, as the scan's JSONL records them>
  raised:   <each [SEC#n] commit allocated, or none>
  again:    <each [SEC#n] reported again or matched, or none>
  closed:   <each [SEC#n] closed by itself or confirmed fixed, or none>
  register: security/<repo-slug>/register.md
```

- **The fixes.** `register.py commit` builds one line per finding marked fix, from structured fields only, never a finding's text, and records the finding `fixing`. With a key, each line is a follow-up for `/dev-workflows:implement <KEY>`, written into the unit's `follow-ups.md` after the report, behind a preview: a line the preview leaves out returns its finding to `fix`, through a second, small run record that clears its follow-up link, and the next run of the unit, or on the repository's path, offers it again as a row to fix — as the unit's next run does a finding whose run was cut off before its line was written. With a path, the lines are `/dev-workflows:implement` prompt lines in the report's `### Next step`. A line starts from this scan's patch for its finding; where this scan made none — Claude Security declined, the scan did not report the finding, or Phase 6 asked for none — it names the patch an earlier run recorded for the finding, where one did and this run did not reopen it, and otherwise says it has no patch: a reopened finding's recorded patch is the fix that regressed.
- **A cost entry** and any session feedback ([Session cost](../reference/session-cost.md)).

**In the code repository**, only what a scan needs: Claude Security's report directory at the scan root (or in the session's working directory, where the session is open in a subdirectory of it), which carries its own `.gitignore`; a fast-forward or a switch Phase 1 made; and a temporary worktree for `--verify-fixes`, removed on every path, a stop or a failure included. Where that worktree holds a report the run did not record, the run copies it to the repository's root first and names the copy, which `--import` records; Phase 0's *Remove them* does the same for each report folder an idle leftover worktree holds. Where the removal fails, the report — or the stop message, on a run that ends early — names the worktree's path, and, where the tail runs, the run hands it to its session-maintenance agent as a key event; the next run's Phase 0 offers to remove it once it is idle, and the resume pointer never names it, since the pointer is shared while the worktree belongs to one machine.

**The report**, printed before the tail: the classification and model routing; the scope — what was scanned, at which commit and effort; whether the scan was verified, as its revision stamp's `verification.status` says and never the workflow's own journal, where a researcher that returned no findings counts as an *empty result*, which is a clean answer; how many of the scan's researchers did not return, where some did not, since Claude Security marks a scan unverified only where none did; and each fetch that failed, each stale tracking ref removed, a shallow clone or a read-only mount, and a temporary worktree the run failed to remove; the findings, then their titles as quoted scan output; the register — the run record, what was raised, reported again and closed, every decision awaiting security review, the accepted risks due for review, the findings this run could not judge, on `--verify-fixes` the findings whose last sighting the default branch's head is not later than, any renumbering, the follow-up lines pending their preview, the patches and the unit note. A renumbering a recording run reports names the follow-up lines to correct — those citing the old number that are the moved finding's own line under it, or whose CWE and file match the moved finding's as far as the line names them — a line naming neither only where it is that own line — since after a collision the old number can still belong to the other finding; one a run that recorded nothing reports is marked *provisional*, with no line to correct yet, because its target can still change. A move that a run record on another branch will make to one of this checkout's findings once it merges — as a record that sorts earlier and took the finding's number for another finding does — is named too, marked *provisional*, with the reserved record it waits on, where one can be named ([Security register](../reference/security-register.md)): the run shows and records the number the checkout gives the finding, so its answers keep their numbers, and the report names each line this run built under that number, to correct once that record merges, never before. Where no one record can be named, the report says so, and that no line is to be corrected by hand: the first run that records anything once the move is made reports it, with the lines to correct. A run that recorded nothing names these moves too, with no line to correct. **Its scope section always states the register's limit**: it records what scans found, never that nothing else is there.

**The next step**, guidance only and never run for you:

- findings went to fix → with a key, `/dev-workflows:implement <KEY>` from this repository, which continues on the Epic's branch while its pull request is open, starting from each patch a follow-up names: it reads each patch in the specs repository, and before any other edit checks each, task by task, with `git apply --check`, applying each that still applies; where one does not, it says so and derives that fix afresh. Then the pull request's review and merge — of the pull request that run opens, where the scanned one has merged already. With a path, `/dev-workflows:implement` with the prompt lines, each that names a patch followed by that patch's absolute path, since a run with no key reads no follow-up;
- once the fix has merged → `/security-workflows:scan <repo-path> --verify-fixes`, the Security Engineer's, with its register `security/<repo-slug>/` named beside it, which closes it on evidence;
- accepted risks are due for review, or decisions await security review → `/security-workflows:scan <repo-path> --triage`, the Security Engineer's, with its register named beside it;
- after a change scan → `/security-workflows:scan <KEY>`, the Dev's, from each other repository the unit's `implementation.md` names; and, where no finding went to fix, the pull request's review and merge, none where it has merged already, and the remaining Epics — each named by its key, with what the run can see of it and its next step, and ordered with that pull request by the landing order the PRD's ARD records, so a pull request whose component lands after another Epic's merges after that Epic's — then the PE's `/dev-workflows:conformance <PRD-KEY>`.

The two Security Engineer offers name their register because a key run's resume pointer carries them until the Security Engineer runs them — where that run records in the register and its record reaches the specs checkout of a later run; one that records nothing, or whose record is still on another clone or on a session branch whose pull request has not merged, leaves the offer standing — and the pointer is shared across machines while `<repo-path>` is this machine's path to the repository, which on another machine can be no repository at all: a later run anywhere finds the Security Engineer's run record of the offer's own mode — a `--verify-fixes` record for a `--verify-fixes` offer, a `--triage` one for `--triage` — in that register in the specs repository, and drops the offer once one is there, later than the offer's waiting datetime: the time the run that offered it completed, which the pointer keeps beside the offer for as long as it carries it, so a record pushed while another run was under way still counts; your own next change scan of the Epic, or a run of the other mode, leaves it standing. An offer an older release wrote names no register, and is kept until a run on a machine where its path is that repository can tell.

**The tail**, after the report: the maintenance agents — only the session-maintenance one on a run that recorded nothing in the register, since the other three check what a run wrote in the specs repository — then feedback, the follow-ups after their preview, the cost entry, the resume pointer, the removal of the run's scratch directory, and the terminal commit. Where that commit's push is rejected because another clone pushed first, and the commit holds a file of the register — as it does on a run that recorded in it, and where a rebuild rewrote a stale `register.json` or `register.md` on a run that recorded nothing — the `Specs repo:` line is followed by a **settle line**, saying how to settle `register.json` and `register.md` if the `git pull --rebase` it advises stops on a conflict in them: rebuild both with `register.py rebuild`, which reads the run records, then `git add` both; where it also stops on a unit's `_security.md`, which is append-only, keep both sides' blocks, or on its `follow-ups.md`, whose lines are ticked in place, keep both sides' new lines and, where both sides hold one line, its ticked form, then `git add` that file; then `git rebase --continue`, then push. A run that ends early prints the same line where it applies.

## Stops

- `SECURITY_USAGE` — the arguments are wrong (Phase 0 step 2), or a token is not a key. It also covers a session open in no git repository on a key run, a path that is no git repository, an `--import` directory in no repository or the wrong one, a repository with no `origin`, and an `--import` directory holding no revision stamp, or more than one.
- `SECURITY_SPECS_MISROOTED` — the specs-repo preflight found `$SPECS_PATH` misplaced. Nothing is written under it: point `SPECS_PATH` at the root of a dedicated specs repository, then re-run.
- `SECURITY_NO_IMPLEMENTATION` — a change scan's unit records no block for the repository this session is open in. The stop names the repositories it does name: run the scan from one of them, or scan a repository by path.
- `SECURITY_PREREQ_PYTHON` — `python3` is older than 3.9 (every run but `--triage`). Put a newer one first on `PATH`, start a new session, then re-run.
- `SECURITY_PREREQ_WORKFLOWS` — a run that scans, and the `Workflow` tool is not available in this session. Turn on the *Dynamic workflows* row in `/config`, then re-run.
- `SECURITY_TREE_DIRTY` — a change scan, and the checkout has uncommitted or untracked changes. Commit them, stash them with `git stash -u`, or delete or ignore the untracked files, then re-run.
- `SECURITY_EPIC_MERGED` — the Epic's work in this repository has merged into the default branch, so a change scan has nothing left to diff. Scan the repository by path, or close fixes with `--verify-fixes`.
- `SECURITY_BRANCH_MISSING` — the branch the latest block records is neither shown merged nor found in this clone. The stop says whether it was never pushed, is not on `origin`, or could not be fetched, and offers a fetch only in the last case; where its pull request closed without merging, re-run `/dev-workflows:implement <KEY>` first.
- `SECURITY_NOTHING_TO_VERIFY` — `--verify-fixes`, and no finding being fixed has a file that changed on the default branch after its last sighting, so the run stops before it scans. A finding whose last sighting the default branch's head is not later than, so that a scan there could close nothing yet — last seen on a branch whose fix the head does not show merged, or, raised for no unit, one the default branch has not moved on past — is named, with the advice to push the fix and merge it where it is not on the default branch, then re-run. Where the run's fetch of the repository failed or timed out, the stop says so: the default branch was read as last fetched, so fetch it and re-run. Findings whose file the default branch does not hold, at a head later than their last sighting, are named, for a repository scan to propose fixed — and one raised for no unit, whose sighting the head is later than only because the default branch has moved on, with the advice to push and merge its fix first where it is not on the default branch, since nothing records that it merged; those whose last sighting this clone cannot place are named too, to fetch the branch that holds it and re-run.
- `SECURITY_NOTHING_TO_TRIAGE` — `--triage`, and the register holds no open finding, no finding to fix whose follow-up is unwritten, no accepted risk past its review-by date, and no decision awaiting security review.
- `SECURITY_ALL_SKIPPED` — the repository was skipped: a read-only mount, no default branch, or a worktree that could not be added. The stop names the reason.
- `SECURITY_NO_REPORT` — Claude Security delivered no report for the commit Phase 1 fixed: no diff to scan, a refusal or a failure, or the checkout moved while it ran. Nothing is recorded.

**Other stops.** `$SPECS_PATH` unset, answered *Cancel*; a key that resolves ambiguously, to no folder (this command creates none), or inside a misplaced specs tree (`SPECS_PATH_INSIDE_TREE`); a run flag naming an unknown or unavailable model; a switch or a fast-forward git refuses at Phase 1, which stops as *Cancel* does; and a `register.py` refusal, led by its own stop code, such as `SCAN_PRODUCTS_UNREADABLE` where Claude Security's output lacks a field the register reads, or names a file outside the repository. A `register.py` refusal that a re-plan or a re-asked question can settle is not a stop: a register that gained a run since this one planned is planned again, and a decision the file did not write as answered is asked again. Where a plan made again before recording — that one, or the one Phase 7.1 makes after refreshing the reservations — finds this scan recorded meanwhile, the run records nothing, and its report lists the decisions it had taken, for a `--triage` to take again.

**Ending early.** Each `SECURITY_*` stop, the `$SPECS_PATH` *Cancel*, the address stops, a switch or a fast-forward git refuses, a `register.py` refusal before the run's record is written, and the run-ending answers — *Cancel* at the Sonnet question, the switch question or the confirmation, and *Stop to clean the files* — take the same short tail: the worktree removal where Phase 2 added one, the cost entry unless `--skip-costs`, the removal of the run's scratch directory where setup made it, and the terminal commit, whose `Specs repo:` line the settle line described under *The tail* follows where it applies, with no resume pointer and no maintenance phase. A stop writes no run record, unit note or follow-up, says what was decided before it, and deletes a scan folder that no record names and that Phase 4 created or copied into; a folder a record names is never deleted, and one Phase 4 found in place and copied nothing into stays as it was. A stop on a run that scanned, once the report directory was found and before the run's record is written, names that directory — on `--verify-fixes`, the copy made of it out of the worktree — and the line that records it without scanning again, `/security-workflows:scan <KEY | repo-path> --import <report dir>`: the key on a `dev` run, and the repository's path on a `sec` run whatever address it was given, since an `--import` with a key is a `dev` run and only the path keeps the role. **A run cut short inside Claude Security's skill** records nothing: where the scan wrote a report directory, record it the same way.

## Limits

- **A change scan runs on the repository this session is open in.** Claude Security's change job takes no path: its scan root is the working directory's repository. An Epic the record names in several repositories is scanned from each in turn, and the report names `/security-workflows:scan <KEY>` from the others.
- **Patches need that repository too.** Claude Security builds a patch against the session's own repository at the scanned commit, so Phase 6 asks for patches only where the scan ran there, its report is clean, and the session's HEAD is the scanned commit: a change scan, a path or an `--import` of this session's repository, and never `--verify-fixes`, which scanned a worktree. Elsewhere it asks for none, and no follow-up has a new patch: each names one an earlier run recorded for its finding, where one did and this run did not reopen the finding, or says it has none. The command never applies a patch: on a key run, `/dev-workflows:implement` reads it in the specs repository and starts from it where it still applies; on a path, the report names each patch by its absolute path beside its prompt line.
- **A scan can miss a real vulnerability.** Scans are nondeterministic, and no tool finds everything. The register records what scans found, never that nothing else is there; run it alongside static analysis, dependency scanning and code review, not instead of them.
- **A change scan never closes a finding**, and neither does a `low`-effort, unverified or dirty scan. Only a covering codebase scan closes one, by the register's rules, or a person confirms a closure it proposes.

## Example

The Dev's scan, from the code repository the Epic was implemented in, once its `/dev-workflows:conformance` decided no fix:

```
/security-workflows:scan ACME-7-01
```

The run finds the Epic's branch checked out, scans its changes over its base at `high` after one confirmation, records the report, and shows two findings: a HIGH it suggests fixing and a LOW it suggests deciding later. The Dev marks the LOW a false positive, naming the template line that escapes the value. Claude Security writes a patch for the HIGH; the run records it `fixing` and the false positive awaiting security review, appends the Epic's `_security.md`, and, after its report, writes the follow-up the preview showed. Next: `/dev-workflows:implement ACME-7-01`, which continues on the Epic's branch, so the fix joins the open pull request.

The Security Engineer's two runs, after the fix has merged:

```
/security-workflows:scan /workspace/acme-api --verify-fixes
/security-workflows:scan /workspace/acme-api --triage
```

The first scans the fixed file at the default branch's head in a temporary worktree; the scan covers the file, does not report the finding, and the file has changed, so the finding closes by itself — or, where the pull request merged by a squash, is proposed as fixed for the Security Engineer to confirm. The second shows the Dev's false positive awaiting review, and *Confirm* records it confirmed.

## See also

- [Security register](../reference/security-register.md) — what the run writes: the layout, the statuses, the closing rules and the numbering.
- [Roles and phases](../roles-and-phases.md) — the Dev and the Security Engineer, and the `security-audit` phase.
- [Workflow overview](../workflow.md) — where the command sits beside `/dev-workflows:implement` and Claude Security.
- [Session cost](../reference/session-cost.md) — what a run charges to and where its entry lands.
- [Environment](../reference/environment.md) — `SPECS_PATH`.
- `/dev-workflows:implement` — where every fix goes, continuing on the Epic's branch while its pull request is open; it ships in the companion `dev-workflows` plugin.
