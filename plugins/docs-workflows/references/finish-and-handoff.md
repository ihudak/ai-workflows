# Finish & handoff (/document — keyed mode; §6, a backlog run)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene`. A citation of one names a rule: before applying it, load the part that holds it, `Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its rule index names, unless that part is already in this conversation word for word; never guess a part's name — until you hold the index (every part carries it), load it with `args: "<name> index"`. A citation that names no rule the index holds loads the whole reference, `args: "<name>"`. Never apply a rule of these references from memory.

The mechanics for Phase 6.2's inline-profiling-branch handling and Phase 8.5's
finish & handoff (squash → opt-in push → copy-paste PR draft). Generic git +
PR-draft logic; the command cites this so it stays lean. Read repo specifics
from the resolved `profile`. This flow does not open the pull request itself: docs repos here are Bitbucket-hosted, and Bitbucket offers no CLI that can create one. Where a host does, the family opens one via `gh` — `workflows-core:phase-handoff` §2.6 in `$SPECS_PATH`, `dev-workflows:code-handoff` §2.6 in a code repo — and no command of this plugin opens one in a docs repository. Its one pull request is `/docs-workflows:release-notes`' own, in `$SPECS_PATH`, for its draft, through `handoff-to-main`.

**§6 is a backlog run's finish**, which its command cites section by section: the check that the backlog and the profile are committed, the branch, one commit per unit, what becomes of a unit that does not commit, one push offer and the printed pull-request draft. §1–§5 are `/document`'s; §6 takes from them only what it names — §2's index restore, §3's push array and §5's use of the repository's pull-request template — and nothing else of theirs applies to a backlog run.

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
cross-links) may have edited without committing — and only those. Under the
Phase 6.2 *Proceed anyway* answer the tree also holds somebody else's changes:
those in a file neither `doc-writer` nor `doc-fixer` wrote or edited, nor
`/document` Phase 6.3's *Regenerate* rewrote, stay out of the squash, and so does
every path of Agent 1's that `/document` Phase 8 reported rather than staged — one
that held such changes before Agent 1 ran, or one outside the docs repository; a
page `doc-writer` or `doc-fixer` wrote or edited, or a build config *Regenerate*
rewrote, carries those changes whole, as that answer's own option says
(*pre-existing changes will appear in the diff*). Such a page that changed while Phase 8's agents ran, with no
agent returning it, goes in as it now reads, that change included: the commit below
takes each path it names from the working tree.
Then squash:
- squash base = `profile_commit` (C0) when recorded — keeps the profile-config
  commit as a distinct first commit; otherwise
  `git -C <docs_repo_path> merge-base <base_branch> HEAD`.
- mechanics: `git -C <docs_repo_path> add -- <each path under docs_repo_path the run wrote or edited, save a path of Agent 1's that Phase 8 reported rather than staged>`
  → `git -C <docs_repo_path> reset --soft <squash-base>`
  → one `git -C <docs_repo_path> commit -F <msg-path> -- ':(literal)<path>' …` **by pathspec**,
  over the paths the squashed commits carry, `git -C <docs_repo_path> diff --name-only -z --no-renames <squash-base> HEAD`
  read before the reset, together with those just staged — never a plain commit, which would
  also carry a change somebody else had staged — and then the index brought back in step as
  `workflows-core:specs-repo-git` §4 step 4 does; the message written first to a
  `command mktemp -t dw-docs-msg-XXXXXX` file outside any repository and removed with
  `command rm -f -- "<msg-path>"` once the commit has been made or has failed: the summary is
  free text, whose backticks and `$(…)` a double-quoted `-m` would command-substitute. Never `add` a path outside the docs
  repository — the implementation-gaps draft in the resolved PRD folder, a screenshot staged under
  `screenshot_staging_dir`, or Phase 8's feedback file under `$SPECS_PATH` — which git refuses
  (`fatal: … is outside repository`) along with every other path in the same `add`.
- message follows `profile.commit_convention` when present (example-docs:
  `<KEY> <summary>`); for a repo with no such field, infer from recent
  `git -C <docs_repo_path> log` / `CONTRIBUTING` (a ticket-key prefix, or a conventional-commits
  `docs:` prefix), else fall back to `<KEY> <summary>`. The key carries
  traceability; the reader-visible changelog still must NOT name it.

Then, before §3, `/document` Phase 8.5 Step 1 checks the commit against the documentation set a
later run's commit scan reads it by (`key-discovery.md` §6), printing one line — that the check did
not run, where git refused the commit — and changing nothing this reference describes.

## 3. Push (opt-in)

Only where §2's commit was made. Where git refused it — a hook's rejection, a signature it
cannot make — report git's error or the hook's output and offer nothing: after the
`reset --soft`, `<branch>` stands at the squash base with the run's changes staged, so a push
would publish the branch without them.

Offer `["Push <branch> to origin now", "Skip — I'll push later", "Cancel"]`.
- **Push** → `git -C <docs_repo_path> push -u origin <branch>`; report the result. `git push` is
  git-protocol, not the REST API the zero-external-API invariant forbids. Where git cannot write
  the repository's `.git/config` — a container that mounts it read-only — `-u` cannot record
  the upstream: git exits 0, prints `could not write config file` or `could not lock config file`, and
  records no upstream. That is not a failed push: the exit status and the `-> <branch>` line are
  the result, and nothing in this reference reads the upstream.
- **Skip** → "Branch `<branch>` ready with N commit(s). Push when ready."
- **Cancel** → stop and summarise.
Never force-push. Never call a REST API over HTTPS from this flow. (The `gh` CLI wraps the API rather than calling it over HTTPS and is permitted where a host provides one — but that allowance belongs to pull-request creation, which this docs-repo flow does not perform; see §5 and `workflows-core:phase-handoff` §2.6.)

## 4. Host detection

Classify the docs repo's `git -C <docs_repo_path> remote get-url origin`, its host first resolved through an SSH alias as `workflows-core:phase-handoff` §2.6.1's `owner-repo` resolves it — `git@github-ig.com:…`, where `github-ig.com` is a `~/.ssh/config` alias whose `HostName` is `github.com`, is GitHub:
- host `bitbucket.org` → Bitbucket Cloud;
- a self-hosted host with `/scm/` in the path or a bitbucket-style hostname →
  Bitbucket Server;
- host `github.com` → GitHub;
- anything else → other.

## 5. PR draft (always; no API)

Compose the draft and BOTH write and show it:
- **write** to the resolved PRD folder as `pr-draft.md` (the resolved PRD folder; ask if none) — the same destination convention as the release-notes / bug drafts — the title on the file's first line, one blank line, then the body, then its **last line** (below).
- **show** the draft without that last line: the title + body a footer below
  tells the user to paste is the printed one, and carries no comment.
- **title**: per `commit_convention` (e.g. `<KEY> <summary>`).
- **body**: what was documented; the output files; the Phase 6.5
  render-verification summary; deferred style/review/render items; a link back to the PRD;
  and, where `/document`'s `nothing_built_answer` is set, the one line its Phase 8.5 step 3
  gives it, the body's first line or its second after the DO-NOT-MERGE banner.
  Where the docs repository carries a pull-request template, the body is that
  template, filled with these facts, per `workflows-core:phase-handoff` §2.7.1,
  with the DO-NOT-MERGE banner below, where there is one, as its required first line.
- **DO-NOT-MERGE banner** at the very top of the body WHEN Phase 5.8 recorded any
  `document-as-spec` / `skip-and-report` decision — never counting one its
  step 0 took from a conformance record, which drafts no gap and holds nothing
  (`workflows-core:source-truth` §7.8):
  `> ⚠ DO NOT MERGE until <KEY>-implementation-gaps.md is resolved.`
  WHEN any of those is `document-as-spec`, a second line beneath it:
  `> ⚠ These pages describe behaviour the code does not have yet (gaps <n>, …): hold the release until each is fixed.`
- **last line**, in the file only, below the body:
  `<!-- implementation records read: <instant> -->`, `<instant>` being the
  instant the run started, in UTC — the `started_at` `/document` took in its
  *Mode detection*, verbatim — then exactly one newline and nothing else: no
  blank line, no trailing space. The DO-NOT-MERGE banner, where there is one,
  stays the body's first line, where the banner bullet above puts it, and this
  comment line is the file's last. Where the run no longer holds `started_at`
  verbatim, it writes no such comment line, never a new reading of the clock,
  which would be later than its start. `/dev-workflows:ready` reads the file's last line
  against exactly
  `^<!-- implementation records read: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z) -->$`,
  as the instant the run that wrote the draft started. Where the line does not
  match — a draft written before `docs-workflows` 1.39.0, or one ending in a
  blank line — or its value is one that command sets aside — an impossible
  time, or one later than the instant its own run started — the draft has no
  instant, and that command dates it as its Phase 1 step 2c says: by the last
  commit that changed it, or, in a shallow clone, not at all.
- **host footer**:
  - Bitbucket (Cloud / Server) → "Open a pull request in the web UI and paste
    the title + body above." (No API.)
  - GitHub → additionally offer a command the USER may run:
    `[ -r '<pr-draft path>' ] && tail -n +3 -- '<pr-draft path>' | gh pr create -R '<owner/repo>' --base '<base_branch>' --head '<branch>' --title '<title>' --body-file -`, to run once `<branch>` is pushed — `<pr-draft path>` the draft's absolute path, `<owner/repo>` the docs repository's, as §4's `owner-repo` call gives it, `<base_branch>` and `<branch>` §1's and §3's — each value in single quotes with each `'` it holds written `'\''`, since inside double quotes backticks and `$(…)` would be command-substituted. `-R`, `--base` and `--head` name the docs repository and its branches, so the command opens nothing in whatever repository the shell stands in, and gh, reading the body from a pipe, has no prompt to ask them with; the `[ -r … ]` test stops it before an unreadable path posts an empty description. `tail -n +3` drops the title line and the blank line under it, so the description starts with the body rather than repeating the title the `--title` flag already sets; `--body-file -` reads the rest from standard input, its last line included, and GitHub shows no HTML comment in a pull request's description.
  - other → "Open a pull request in your host and paste the title + body above."

**A limit of the last line:** a user who pastes from `pr-draft.md` itself, not
from the printed draft, onto a host that shows an HTML comment in a pull
request's description shows that line there too.

For a Bitbucket-hosted docs repo there is no CLI to open the pull request with, so this flow writes the draft and the user opens it. This is a host capability limit, not a policy: the family does open one where a host offers a CLI (`workflows-core:phase-handoff` §2.6 in `$SPECS_PATH`, `dev-workflows:code-handoff` §2.6 in a code repo), and no command of this plugin opens one in a docs repository — `/docs-workflows:release-notes` opens one in `$SPECS_PATH` alone, for its draft, through `handoff-to-main`.

## 6. A backlog run's finish

A *backlog run* works units of the documentation backlog, `<top>/.dev-workflows/docs-backlog.yml`, and moves each unit it finishes; a run of `/docs-workflows:docs-write` is one. A backlog run's command says which of its phases runs each subsection below. This section also leaves to that command its commit verb (§6.3 step 3) and the paths it hands §6.3 and §6.4 — the unit's paths, which the unit's commit holds, and the created and edited paths §6.4 undoes; where this section first takes each, it gives `/docs-workflows:docs-write`'s, as that command's. Here `<top>` is the docs repository's work-tree top level; `<base>` is its default branch's **name** as the command resolved it — `workflows-core:read-only-repos` §3's chain, reads only, and where that is exhausted the local `main`, then `master`; and `unfinished/` is `<top>/.dev-workflows/unfinished/`. Every git call runs as `git -C '<top>'`. Every value this section puts in a command — a path, a branch name, a ref, a file the run made — is single-quoted, each `'` it holds written `'\''`, and placed after `--` where the command takes one; a branch name is held first to `read-only-repos` §3's *Branch names* class, tested as that section says — **by a program handed the name as one single-quoted argument**, `python3 -I -c 'import re, sys; sys.exit(0 if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9._/@+-]*", sys.argv[1], re.ASCII) else 1)' '<name>'`, which exits 0 where it is in the class, a name git printed, one built from the profile's `branch_naming.pattern` and one typed alike — and a name that fails is never printed. A path built from data reaches git as a literal pathspec, `':(literal)<path>'` — or, for `check-ignore`, which takes no pathspec magic, as `'./<path>'` — so no `:` or glob character in it is read as anything but itself. A unit id has passed the class `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` before this section puts it in a directory name or a commit message.

### 6.1 Committed before the run

Before the run writes anything, the backlog and the profile it read are tracked and clean: `git -C '<top>' status --porcelain -z -- '.dev-workflows/docs-backlog.yml' '.dev-workflows/docs-profile.yml'` prints nothing, and `git -C '<top>' ls-files --error-unmatch -- '<file>'` exits 0 for each of the two. Otherwise the run stops before any write, naming the file and the commit to make: that file, committed as it stands on the branch the run stands on, before the run is made again. A stash would hide the file the run read, and going on would fold an audit's backlog, or a profile's change, into a page's pull request. Clean, neither file is anything §6.2's stash takes; the command reads both again once §6.2 has put the run on its branch, since a switch and a pull can change them.

### 6.2 Adopt or cut

Once per run, before its first write for any unit. Every unit of the run commits on the one branch this section settles, so a batch's units, stacked there, make one pull request.

1. **Where HEAD stands.** Read `<start>`: `git -C '<top>' branch --show-current`, or, where that prints nothing — HEAD detached — or a name outside the *Branch names* class, which counts as detached, `git -C '<top>' rev-parse HEAD`. Where `<start>` is `<base>`, or a commit, the run **cuts** (steps 2 to 4). Where it is another branch, the run asks, the question's own text naming that branch and `<base>`: `choices: ["Continue on <branch> (Recommended)", "Cut a new branch from <base>", "Cancel"]`. **Where the branch is behind `<base>`, and where the run cannot tell whether `<base>` moved a unit it will work, the question says so.** Before asking, read `git -C '<top>' rev-list --count 'HEAD..<base ref>'` — `<base ref>` being `refs/remotes/origin/<base>` where `git -C '<top>' rev-parse --verify --quiet 'refs/remotes/origin/<base>'` finds it, as last fetched, for nothing here fetches, else `refs/heads/<base>` — the commits `<base>` holds that the branch lacks: where it prints a number above 0, the question's own text says the branch lacks that many commits of `<base>`, as last fetched; at 0 it says nothing of it. Whether `<base>` moved a unit is the answer of the command's `backlog-lines.py moved` read over the units the run will work, which its command says where it makes: that read names the base — `origin/<base>`, or `<base>` where it resolved no `origin/<base>`; and the local `<base>`, named `<base>`, where it holds commits `origin/<base>` lacks — for a unit whose status there changed after this branch left it, and lists it as unreadable where it could not tell. **No unit that read names the base for reaches this question**: the command passes it over before its consent, as `/docs-workflows:docs-write` Phase 1 does, since this branch's backlog, which the run's re-check reads, holds it at its older status, so that continuing here would work it a second time, its page beside, or in conflict with, the one `<base>` holds. Where it lists the base, or the local `<base>`, as unreadable, the question's own text says the run could not tell whether `<base>` moved one of them since this branch left it — in a shallow clone, on an orphan branch, or where a backlog or git could not be read — so that continuing here may work one a second time, and that a cut, or merging `<base>` into the branch before the run, reads any move. There no choice is marked `(Recommended)`, whether to continue being the user's call — `choices: ["Continue on <branch>", "Cut a new branch from <base>", "Cancel"]`; so too where the count's read fails, its text naming git's error in place of the count. Otherwise it keeps the first list, with its `(Recommended)` marker. *Continue on <branch>* adopts it — every unit of the run commits there, on top of what it already holds, and step 3 is then the whole of this section — and *Cut a new branch from <base>* cuts. Where the command resolved no `<base>`, `<base>` is `<start>` itself: the run cuts from where HEAD stands, asks no adopt question, and step 4 switches and pulls nothing.
2. **The name** (a cut only). Where the profile carries `branch_naming.pattern`, fill it as `workflows-core:branch-naming` §1.2 fills a pattern — its identity placeholder from that reference's §2 ladder, and its issue-key segment the pattern's own documented no-issue literal, since a backlog run resolves no key and a unit id never fills a key placeholder; otherwise build it by that reference's §1.4, `<prefix>/<slug>`, `<prefix>` from its §2 ladder with the fallback `docs/`. `<slug>` is the one the command names. A name a local branch already holds — `git -C '<top>' rev-parse --verify --quiet 'refs/heads/<name>'` prints a commit — takes `branch-naming` §3's suffix before it is proposed. A built name outside the *Branch names* class, tested by the program above — a pattern's own text can put one there — is neither proposed nor printed: the run says why and asks `workflows-core:branch-naming` §1.3's question instead, `choices: ["Type a branch name (you'll be prompted)", "Cancel"]`, *Type a branch name* asking for one in plain text. Always confirm, a typed name too: `choices: ["Use proposed branch <name> (Recommended)", "Edit the name (you'll be prompted)"]` — *Edit the name* asks for the name in plain text and confirms it the same way. A typed name outside the *Branch names* class, tested by the program above, or one a local branch already holds, is refused, never printed, and asked for again with the reason said — by the confirmation with the last name it showed, where it showed one, and otherwise by that question, never by anything that shows the refused name.
3. **The clean-tree check**, adopted or cut, before anything is switched or written: `git -C '<top>' status --porcelain -- . ':(exclude).dev-workflows/unfinished'`. The run has written nothing yet, so a non-empty result is pre-existing work, and the run asks `/docs-workflows:docs-init` Phase 2.5 step 2's question, verbatim: `choices: ["Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]`, the question's own text naming each dirty path, one `git -C '<top>' status --short -- . ':(exclude).dev-workflows/unfinished'` line each, since both options turn on them (`workflows-core:epic-picker` *The cap*). The exclusion keeps out every file §6.4 left under `unfinished/`, which blocks nothing. A stash runs `workflows-core:escalation-rules` § *Stashing the user's changes* with `. ':(exclude).dev-workflows/unfinished'` as its pathspec, so it takes the paths the question named and no file under `unfinished/`: named, recorded by commit, never applied by the run, and named with its restore commands wherever the run ends. *Proceed anyway* goes on with those changes in the tree: a file the run then edits for a unit — a placement target, a navigation config — carries its pre-existing change into the unit's commit, as the option says, and keeps it where the unit does not commit (§6.4). An empty result asks nothing.
4. **The switch, the pull and the cut** (a cut only), as `/docs-workflows:docs-init` Phase 2.5 step 2 makes them, by `read-only-repos` §3's **A switch never makes the branch** rule. Where no local `<base>` exists — `git -C '<top>' rev-parse --verify --quiet 'refs/heads/<base>'` prints nothing — make it first, `git -C '<top>' branch --no-track '<base>' 'origin/<base>'`, then `git -C '<top>' branch --set-upstream-to='origin/<base>' '<base>'`, best-effort, whose failure is no failure. Then `git -C '<top>' switch --no-guess '<base>'` and, once that switch has exited 0, `git -C '<top>' pull --ff-only --no-rebase origin '<base>'`; a local `main` or `master` that the chain did not find on `origin` is switched to without the pull, there being no remote branch to bring it up to. Then cut, `git -C '<top>' switch --no-track -c '<name>'`, `--no-track` for the reason `read-only-repos` §3 gives.
   - **Where the pull fails**, ask, the question's own text giving git's message as its reason. Where step 3's read now prints anything, the choices are step 3's three, the text naming each dirty path as there — *Stash* stashing as there, *Proceed anyway* going on — each cutting the branch from `<base>` as it stands; where it prints nothing, `choices: ["Proceed from current base state (Recommended)", "Cancel"]`, *Proceed* cutting from `<base>` as it stands. A stash here records `<start>`, read before the switch, the switch having carried the changes here.
   - **Where the local `<base>` has diverged.** Before asking the failed-pull question, read `git -C '<top>' rev-list --count 'origin/<base>..<base>'`. Where it prints a number above 0, the local `<base>` holds that many commits `origin/<base>` does not, and the branch cut from it, and its pull request, would carry them: the question's own text says so, naming the count, and no choice is marked `(Recommended)`, whether to take those commits along being the user's call — `choices: ["Stash changes and continue", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]` where the tree is dirty, and `choices: ["Proceed from current base state", "Cancel"]` where it is clean; so too where that read fails, its error named in place of the count. Where it prints 0, the lists above stand, each with its `(Recommended)` marker.
   - **A switch onto `<base>` that exits non-zero** — the `--no-guess` switch, or the switch to a local `main` or `master` — has moved nothing: the run pulls nothing and cuts nothing, and ends as *Cancel* does, its report quoting git's message, which names the files in the switch's way. A cut that exits non-zero ends the run the same way, quoting git's message.

**Cancel**, at any question of this section, ends the run with nothing written, by its command's stop route. Where the run had switched onto `<base>` and `<start>` is not `<base>`, its report says the repository is now on `<base>` and names `git -C '<top>' switch '<start>'` — `switch --detach '<start>'` where `<start>` is a commit — to go back, and it names any stash the run took, as `workflows-core:escalation-rules` § *Stashing the user's changes* step 4 says.

### 6.3 One commit per unit

At the unit's commit step, once its command's writes for the unit are made and `backlog-lines.py edit` has exited 0 on the unit's move:

1. **The ignore test.** `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/scaffold-tree.md` §7's commit-time ignore test, over every path of the unit — the paths its command hands this section, `/docs-workflows:docs-write`'s being the page, each placement target and navigation config the run edited for it, and `.dev-workflows/docs-backlog.yml`: `git -C '<top>' check-ignore -v -- './<path>' …`, a printed line whose pattern starts with `!` being no match. `check-ignore` refuses pathspec magic, `:(literal)` included, so each path is written with a leading `./`, which keeps one opening with `:` from being read as magic. Any match ends the unit (§6.4): a backlog run never force-adds a path and never commits a unit in part, so §7's own answer to a match, the path left unstaged and the rest committed, does not apply. The report names the path and the ignoring line, with its line number. A test git cannot run — an exit above 1 — ends the unit too, the report quoting git's message.
2. **The commit.** First `git -C '<top>' diff --cached --name-only -z --no-renames -- ':(literal)<path>' …` over the unit's paths: a path it lists was already staged — somebody's change, under §6.2's *Proceed anyway* — and the `add` that follows replaces that staged state with the working tree's, so the report names each such path and says so. Then `git -C '<top>' add -- ':(literal)<path>' …` over the unit's paths, one `':(literal)<path>'` argument per path, then one `git -C '<top>' commit -F '<msg-path>' -- ':(literal)<path>' …` **by pathspec**, one `':(literal)<path>'` argument per path — never a plain commit, which would carry a change somebody else had staged — and then the index brought back in step as §2 does.
3. **The message** is written first to a `command mktemp -t dw-docs-msg-XXXXXX` file outside any repository, and removed with `command rm -f -- '<msg-path>'` once the commit has been made or has failed. Its subject is `docs: <verb> <unit-id> (<type>, <audience>)`, `<verb>` the command's commit verb, a fixed word and never a value read from data — `draft` for `/docs-workflows:docs-write`. Where `profile.commit_convention` holds `<summary>` and no other placeholder, the subject is that form, `<summary>` replaced by `<verb> <unit-id> (<type>, <audience>)`; where it holds any other placeholder — `<KEY>` among them — the subject keeps the `docs:` form and the report says so, since a unit id never fills a key. After a blank line, its body is two lines, `Unit: <unit-id>` and `Page: <page path>`, the page's path relative to `<top>`. No other value read from the backlog enters it, and `<type>` and `<audience>` have passed `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/coverage-model.md` §3's vocabulary first.
4. **A refused commit** — a hook's rejection, a signature git cannot make — ends the unit (§6.4), the report giving git's error or the hook's output.

### 6.4 A unit that does not commit

A unit that ends without its commit, once the run has written anything for it — a build still failing, a review left unresolved, a *Cancel* while it is in hand, §6.3's ignore test or a refused commit, or any other end its command names — is undone here, a single run's one unit alike. Its command hands this section the unit's **created paths**, `/docs-workflows:docs-write`'s being the page, where the run wrote it, and every other path inside `<top>` that the command's tree comparisons around its writing agents report as created during the unit. In this order:

1. **The `unit:` line.** Where the run wrote the page's `unit: <unit-id>` frontmatter line, that line is removed, and nothing else on the page changes. A page that never reached the commit step carries none, so `/docs-workflows:docs-audit --refresh`, which matches a page to its unit by that line, never finds it.
2. **The index.** A refused commit leaves the paths §6.3 staged still staged, and a backlog left staged is one the next run's §6.1 refuses. So, where §6.3 staged them, the unit's paths git still lists as staged — `git -C '<top>' diff --cached --name-only -z --no-renames -- ':(literal)<path>' …` — are unstaged, `git -C '<top>' restore --staged -- ':(literal)<path>' …`, run only where that list holds one, since one pathspec that matches nothing fails the whole `restore`.
3. **The files the run created** for the unit — its created paths — are moved, never deleted. Where there are none, nothing is made and no directory is named. Otherwise, before anything is made: where `<top>/.dev-workflows/unfinished` is a symbolic link (`test -L`), or exists and is no directory, nothing is moved, and the report names each created path left where it is, and why. Then `command mkdir -p -- '<top>/.dev-workflows/unfinished'`, and `<dir>` is claimed: `command mkdir -- '<dir>'`, `<dir>` being `unfinished/<unit-id>/`. Where that `mkdir` fails and `<dir>` exists (`test -e` or `test -L`), the next of `unfinished/<unit-id>-2/`, `unfinished/<unit-id>-3/`, … is claimed the same way; any other failure moves nothing, and the report names each created path left where it is, with `mkdir`'s message. A claimed `<dir>` is one this run just made, so no file is ever overwritten. Then, for each created path, keeping its path relative to `<top>`: `command mkdir -p -- '<dir>/<its directory>'` and `command mv -- '<top>/<path>' '<dir>/<path>'`. `unfinished/` lies outside every content root but `.`, and so outside every build, and the next run's strict build meets none of them. **Under a content root of `.`** it lies inside that root, and only the site generator's own treatment of dot-directories keeps it out of a build, so the report says so beside `<dir>`. A directory the run made for one stays, empty, which git does not track and no build reads.
4. **The files the run edited** for the unit — the edited paths its command hands this section, `/docs-workflows:docs-write`'s being each placement target, each navigation config and the backlog — are restored from the copy the run took before its first edit of that file for the unit, `command cp -- '<copy>' '<top>/<path>'`: the working-tree content the run read, a pre-existing change included. The copy holds no staged state; §6.3 names each path whose staged state its `add` replaced. The backlog is restored only as `backlog-lines.py edit`, its one writer, left it:
   - **Before `edit` ran**, or **where it exited 3 or 4**, the backlog holds the bytes it held before, and nothing is restored.
   - **Where it exited 2**, which also stops the run, the one line it printed on standard error, matched whole, decides. Only `backlog-lines: not run (the edit was written and its undo failed on its own write, so the backlog still holds the edit, unchecked; restore the backlog from the copy taken before the edit)` has the run restore the backlog from its copy. Every other line — a write that did not read back as written, an undo another writer's change blocked, an exit 2 before any write, a line the run cannot read — leaves the backlog exactly as it is, since restoring there could overwrite another writer's change, and the report names the backlog and the copy for the user to compare.
   - **Where it exited 0** and the unit ended after it — §6.3's ignore test, a refused commit — the run restores the backlog from its copy. A change another writer made to the backlog after the edit is lost with it, so the report names the copy.

   A copy the report names is kept, not removed with the run's other temporary files, so the user can still read it.
5. **Nothing else.** Nothing is deleted, nothing is stashed and no `.gitignore` is edited: the moved files stay in the working tree, visible, and block nothing, since §6.2's clean-tree check reads past `unfinished/`. Only the unit's own paths are moved or restored: a path the command's tree comparison reports as changed, for which the run holds no copy, and any path outside `<top>`, is left as it is, and the report names it. A step above that fails — a `restore --staged`, a `mkdir`, an `mv`, a `cp` — is not retried: the report quotes its message and names each path it left staged, unmoved or unrestored, and the steps after it still run. The report names `<dir>`, where step 3 claimed one. No later unit of the run starts — a batch ends here, its committed units standing — and the command says whether its finish (§6.5, §6.6) or its stop route follows.

### 6.5 Push, once

After the run's last unit, once — and only where this run made a commit by §6.3, did not stop, and HEAD is still on the run's branch, `git -C '<top>' branch --show-current` printing the name §6.2 cut or adopted — the run offers §3's array, `["Push <branch> to origin now", "Skip — I'll push later", "Cancel"]`, and each answer does what §3 says, run against `<top>`: *Push* runs `git -C '<top>' push -u origin '<branch>'` and reports the result, never a force-push and never a REST API. Above the array, where `<k>` is above 0, it prints:

`This push also publishes <k> commit(s) on <branch> that this run did not make.`

`<k>` is `git -C '<top>' rev-list --count '<upstream>..HEAD'` less the number of commits this run made — every commit §6.3 made in it, whatever its verb. `<upstream>` is `origin/<branch>` where `git -C '<top>' rev-parse --verify --quiet 'refs/remotes/origin/<branch>'` finds it, else the base's ref: `origin/<base>` where that exists, else `<base>` — the local branch, or the commit §6.2 cut from. On an adopted branch those commits are what it already held; on a cut one, commits the local `<base>` held that `origin/<base>` did not (§6.2 step 4's diverged-base question). Where the count cannot be read, the run says so above the array in place of that line.

Where HEAD is no longer on the run's branch, nothing is offered, and the report names the branch and each unit committed on it.

### 6.6 The pull-request draft, printed

Where a unit committed, the run's report prints a pull-request draft, for the user to paste into the host's form for the branch against `<base>`, and writes it nowhere: no file — §5's `pr-draft.md` belongs in a PRD folder a backlog run does not have, and the specs repository takes no deliverable from it — and no host footer, since its command would read a file that does not outlive the run. No pull request is opened. The draft holds:

- **a title** in §6.3's subject form, `<summary>` being `draft <unit-id> (<type>, <audience>)` for one unit and `draft <n> units (<unit-id>, …)` for more;
- **the units moved**, each with its page's path;
- **the placement targets edited**, and each navigation config regenerated, per unit;
- **the review verdicts and triage lines** — each unit's verdict, and each finding the triage kept, marked unverified or dismissed, with its reason;
- **the build results**, per build, per unit;
- **the markers left**, per page: each claim marked `[NEEDS CLARIFICATION: <why>]`, with its why, and the page-level marker, which every drafted page carries until it is verified;
- **the deferred items** — a finding deferred, a style violation left;
- **the paths left unstaged** — each path §6.3's ignore test matched, with its ignoring line, and the unit it ended;
- **the `unfinished/` directories** this run made, and the unit each holds.

Where `<top>` carries a pull-request template, the body — every item above but the title — is that template, filled by `workflows-core:phase-handoff` §2.7.1's rules, as §5's body is, which read the template as data: the run fills the template's sections with the draft's content, in the template's order, and appends after the template each item above that no section asks for, in the order above. The body has no required first line. The draft is still printed only: no file, no pull request.

Where no unit committed, the report says there is no pull request to draft.
