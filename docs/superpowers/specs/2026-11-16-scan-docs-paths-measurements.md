# DOCS-IN-CODE-REPO-SCAN — measurements

Tree: `git archive b45b66d6` of `/workspace/.worktrees/ladder-order-b3`, extracted to `scan-measure/tree/`. Every `file:line` below is a line of that tree. Paths are repo-relative. KD = `plugins/docs-workflows/scripts/key-discovery.py`, KDM = `plugins/docs-workflows/references/key-discovery.md`, DOC = `plugins/docs-workflows/commands/document.md`, RN = `plugins/docs-workflows/commands/release-notes.md`, IF = `plugins/workflows-core/references/implementation-format.md`.

## 0. Where the to-fix entry, or the brief, is wrong or incomplete

Each item is established in the section named.

1. **`/release-notes` is affected too, and in both directions. The entry names only `/document`.** Its docs root is never lifted to a top level: RN:23 `--docs <path>`; `workflows-core:docs-grounding` steps 1–2, `docs_root = ${DOCS_PATH:-/workspace/docs}`. KDM §1 passes `--exclude` only where the path "is a git checkout's top level". So `$DOCS_PATH=<product>` (the product's top level) leaves the product's code out of every grounded run whose record names no repository, and no question is asked. `$DOCS_PATH=<product>/website` leaves nothing out, so `/document`'s earlier key-bearing squash commits in that product repository are read as code, as unrecorded work. That is the false positive the exclusion exists to prevent (§2, §3, §7).
2. **A record that names the documentation-holding repository has an unacknowledged false positive today.** KDM:23: "documentation kept inside a code repository that `implementation.md` names is that code's, and the code stays scanned". That repository is scanned whole, including `/document`'s own squash commits there, which name the key (`finish-and-handoff.md`:57–61). Those commits come back `via: message`, are reported as unrecorded work and are handed to `diff-summarizer` as code refs. KDM:23 gives the exclusion's reason as "read as code they would verify a requirement by its own text". No sentence in `plugins/`, `.claude/` or `docs/maintainers/` says this case is accepted (§2).
3. **For `/document` the "top level" condition never protects anything.** `docs_repo_path` is always lifted to its top level (DOC:242, since `docs-workflows` 1.2.0, CHANGELOG:1284). So for `/document` the exclusion reduces to "the whole repository, unless `implementation.md` names it". The exclusion itself shipped later, in 1.13.0 (CHANGELOG:651), whose entry claims "each only where it is a repository's own top level … so documentation kept inside a code repository never takes the code out". That claim was already untrue for `/document` when it was written. The defect therefore dates from 1.13.0 (2026-10-07), not 1.40.0. Before 1.40.0 a no-block run dropped those code commits silently and wrote "no diff content stands behind these pages". 1.40.0 only made the loss visible, by asking the question.
4. **"Nothing the run holds tells the two apart" is false in two of the layouts.** The sentence is at KDM:23 and rationale.md:690.
   - On rung (a.5), and on a path entered at (c), the run holds `docs_repo_resolved` (DOC:242), the site's own directory below the top level.
   - With an in-repo profile, or the built-in one, the run can read `spaces[].content_root` and `snippet_root` at step 3a.
   - The claim holds only for a site at the top level with no profile: rung (a), rung (b), and *Use cwd anyway* (§3).
5. **Rung (a) reaches more than "`mkdocs.yml`, a `docs:*` script".** The signal set (DOC:222–224) also counts:
   - any `package.json` script matching `*:start`, `*:build` or `*:lint`;
   - a `_snippets/` directory "at any level under the repo root";
   - *Use cwd anyway* (DOC:240), which takes a repository with no signal at all, write context `non_docs_repo` (DOC:331).

   So a plain code repository is taken as the docs repository, and then left out whole, whenever `/document` runs from inside it and one of those signals holds (§3).
6. **The specs repository has the same blind spot.** The specs exclusion is computed as `git -C <PRD folder> rev-parse --show-toplevel` (KDM:23), so its "top level" condition is always met. Two setups reach it:
   - A specs tree inside a product repository. This is unsupported but never fatal: `specs-repo-git.md`:316 sets `specs_git: misrooted` and the run continues.
   - An `@<path>` run, with `$SPECS_PATH` unset, on a specs tree inside a code repository.

   In both, the product repository's code is left out whole (§7).
7. **The pull-request layer is coupled to the exclusion in ways the entry does not mention.**
   - It drops pull requests by bare repository *name* in every searched owner, not by `owner/name` (KD:1128–1130). Excluding `docs` also drops `partner/docs`.
   - Under a path rule, a merge-commit landing of `/document`'s docs pull request would return the branch's own commits. That includes the inline-profiling commit `docs: add/refresh .dev-workflows/docs-profile.yml`, which names no key, so it comes back `via: pull-request` unless the landed commits are path-filtered too (§1, §4, §5).
8. **Adding a pathspec silently changes git's walk.** Two flags matter:
   - `--full-history`. Without it git turns on history simplification and prunes side branches whose net effect on the pathspec is zero. Measured: a branch's two key-naming commits vanished (§5).
   - The probe, which exists to show merge commits. Under a pathspec it needs `--full-history`, and then it also shows a docs-only merge wherever the mainline moved on code meanwhile (§5).
9. **Of what the family commits into a docs repository, only `/document`'s Phase 6.3 and 8.5 commits can carry the key.** The commits made by inline `/docs-profile`, `/docs-init` and `/docs-brand` have fixed, keyless subjects. No commit carries a trailer or any other marker (§4).

## 1. The script, as it is

**CLI** (KD:1247–1290; usage KD:4–7):
- `scan` takes these flags:
  - `--key` (repeatable, required). Rejected if empty or holding whitespace or `"`, KD:1264; deduplicated.
  - `--repo` (repeatable, required). Must be a directory; realpath taken; deduplicated, KD:1269–1274.
  - `--scope head|default` (required). `default` reads `origin/HEAD`, else `origin/main`, else `origin/master`, else `HEAD` (KD:859–870). No caller uses `default`: KDM:12 passes `--scope head`.
  - `--probe`.
  - `--no-github`.
  - `--exclude` (repeatable; must be a directory).
  - `--owner-of` (repeatable; must be a directory, KD:1275–1278).
- `--selftest` must be the whole argv (KD:1248).
- Exit 0 means it ran. Exit 2 means `Unrunnable`, or any exception, as one stderr line (KD:1284–1289).

**JSON** (KD:1244; pinned by `case_cli`, KD:756–757):
- top level: `keys`, `scope`, `excluded`, `repos`, `commits`, `github`
- `repos[]` (KD:895–896): `path`, `ref`, `scanned`, `matched`, `github`, `error`, `probe`, `probe_error`
- `commits[]`: `repo`, `sha`, `date`, `subject`, `keys`, `via` (`message` | `pull-request`), `prs`
- `probe[]`: `sha`, `date`, `subject`
- `excluded`: the slugs (or basenames, where a repository has no `origin`) of the `--exclude` paths that are a repository's own top level
- `github` (KD:1081): `status`, `detail`, `owners`, `queries`, `dropped_loose`, `prs[]`
- each pull request (KD:1073–1076): `url`, `owner`, `repo`, `number`, `title`, `state`, `keys`, `clone`, `head_ref`, `base_ref`, `head_oid`, `merge_commit`, `cross_repository`, `landed_as`, `landed`, `reason`

**`--exclude` in `discover()`** (KD:1183–1198):
```python
    for path in excludes:
        rc, out, _ = _git_in(path, "rev-parse", "--show-toplevel")
        top = os.path.realpath(out.strip()) if rc == 0 and out.strip() else None
        if top is None or top != os.path.realpath(path):
            continue  # only a repository's own top level is a repository to leave out
        excluded_paths.add(top)
        slug = remote_slug(top)
        if slug:
            lowered.add(slug.lower())
        ...
    if excludes:
        clones = [c for c in clones
                  if os.path.realpath(c) not in excluded_paths and (remote_slug(c) or "").lower() not in lowered]
```
- **Path match.** An exclude acts only where its realpath equals its own `--show-toplevel`. A subfolder, or a non-git directory, excludes nothing (`case_an_exclude_that_is_no_repository_top_excludes_nothing`, KD:729–736).
- **Slug match.** `remote_slug` (KD:953–960) takes the last path segment of `origin`, so every `--repo` whose `origin` ends in that name is dropped too. That includes a second clone, and any other owner's repository of the same name.
- **A `--repo` that matches** gets no `repos[]` entry at all: no `scanned`, no probe. It appears only in `excluded`.
- **`--owner-of` is not filtered by `--exclude`** (KD:1210: `[github_slug(c) for c in owners_of]`). An excluded clone's owner is searched only if another scanned clone or an `--owner-of` clone shares it, because the excluded clones are removed before `github_slug` runs (KD:1206).
- **The GitHub layer drops every hit whose repository name is excluded** (KD:1128–1130): `repo = str(hit.get("repository", {}).get("name", "")).lower()` / `if repo in excluded: continue`. This compares the bare name, not `owner/name`.

**How commits are found** (KD:873–886, 901):
```python
    argv = ["log", ref, "-z", "--date=iso-strict-local", "--extended-regexp", "--regexp-ignore-case", "--format=" + FMT]
    if not merges:
        argv.append("--no-merges")
    argv += ["--grep=" + g for g in greps]
    rc, out, err = _git_in(clone, *argv, "--")
```
- `FMT = "%H%x1f%cd%x1f%B"` (KD:51). There is one `--grep` per key, `EDGE_L + ere_escape(k) + EDGE_R` (KD:905), so git ORs them. Python then re-checks each key whole (KD:906).
- The ref is `HEAD` under `--scope head`.
- **No pathspec is ever passed.** The argv always ends in a bare `--` (KD:878).
- `scanned` is `git rev-list --no-merges --count <ref> --` (KD:901).
- Each `_git_in` call runs under `GIT_TIMEOUT = 60` s (KD:42) with `GIT_NO_LAZY_FETCH=1` (KD:843–847).

**The probe** (KD:918–921, 1237–1243): `_log(clone, ref, [ere_escape(k) …], merges=True)`. It uses bare tokens, keeps merges, runs only where `error is None and matched == 0`, and leaves out every `(clone, sha)` a found pull request accounts for, whether a merge commit or a landed commit (KD:1217–1226).

**The pull-request layer** (KD:1079–1167, `landing` KD:1025–1058):
- It runs `gh search prs --owner … -- "K1" OR …`, six keys per query (`BATCH`, KD:45).
- It keeps a hit only where its title or body names a key whole (KD:1125–1126).
- `gh pr view` runs only for a hit whose `owner/repo` is a scanned clone (KD:1141–1151).
- For a `MERGED` pull request with a merge commit, `landing()` does the following:
  1. It checks that the merge commit is in the clone and on the ref (`merge-base --is-ancestor`).
  2. For two parents, it refuses a range that brings in other branches' merges. Otherwise `rev-list --reverse --no-merges M^1..M^2` gives `merge`.
  3. For one parent with n>1 pull-request commits, it matches the first-parent headlines to give `rebase`.
  4. Otherwise it gives `squash` with `[M]`.
- `discover()` turns each landed SHA not already found into a `via: pull-request` commit (KD:1225–1233).
- **No path is consulted anywhere.**

**Does anything look at paths?** No. The only paths the script handles are clone directories. `_commit` (KD:90–96) writes to `name` at the repository root and makes no subdirectory. The one fixture with a `docs/` folder (KD:732) tests that excluding it excludes nothing.

**`--selftest`** (KD:794–813):
- There are 42 `case_*` functions. Each gets a fresh `tempfile.TemporaryDirectory`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and `GIT_CEILING_DIRECTORIES=<tmp>`.
- Fixtures are real git repositories built at run time. Fake `gh` and `ssh` executables first on `PATH` answer by rule and log their argv (`_stub`, KD:104–126).
- The run from `tree/`, `python3 -I plugins/docs-workflows/scripts/key-discovery.py --selftest`: **exit 0, `selftest: 42/42 passed`, 1.21 s wall clock.**
- CI step: `.github/workflows/validate-catalog.yml`:251–256, "Self-test the key discovery", `run: python3 plugins/docs-workflows/scripts/key-discovery.py --selftest`.

## 2. Who calls it, with what

The script has two callers, both through KDM. The other files that name it only describe it: `agents/diff-summarizer.md`:37, `docs/reference/references.md`:25 and IF:309. No other script calls it.

- **`/document`, Phase 0 step 3a** (DOC:256): "build the slug→clone map over `$REPOS_PATH` by Phase 3's recipe … and run the commit scan as … `key-discovery.md` §1 says for a record that names no repository: every clone in the map, one per slug; the tokens Phase 3's step *The scan* takes for this run's scope … and `--exclude` the specs repository and `docs_repo_path`."
- **`/document`, Phase 3 step 2** (DOC:526–541). On a run whose record holds a block it runs the scan here. On a no-block run it takes step 3a's `early_scan` and runs again only over a base named at *Revise plan*, with "the same tokens, the same exclusions" (DOC:539).
- **`/document`, Phase 4 step 5** (DOC:609, 629, 632, 634). It runs again after *Use another clone*, *Mount the missing repo(s) now* and *Specify a different absolute path*, "rebuild the map and run the script again over the new set" (KDM:27).
- **`/release-notes`, Phase 3 step 2** (RN:392–403), "only when diff grounding is ON" (RN:389).
- **The arguments**, from the KDM:12–14 template, `scan --scope head --probe`:
  - `--key`: each token, as IF §4 gives them, read off the folders in scope.
  - `--repo`: the clones `implementation.md` names, resolved through the map. Where it names none, "every clone in the map, one per slug", the chosen or preferred clone for each slug (KDM:17).
  - `--owner-of`: every other clone in the map (KDM:17).
  - `--exclude`: the specs top level and the docs repository.
  - No GitHub token is passed; `gh` uses its own login. The `--no-github` retry is used only after a failure (KDM:25).
  - The Bash timeout is 600000 ms (KDM:9).
- **When the docs repository is passed: KDM §1, "Never code", whole (KDM:23):**
  > **Never code: the specs repository and the docs repository.** Pass `--exclude <the specs repository>` — the top level of the PRD folder's repository, `git -C <PRD folder> rev-parse --show-toplevel` — and `--exclude <the docs repository>`: `/document`'s resolved `docs_repo_path`, and `/release-notes`' docs root, the one its documentation grounding resolved (`--docs <path>`, else `${DOCS_PATH:-/workspace/docs}`). Pass either only where it is a git checkout's top level and not a repository `implementation.md` names: documentation kept inside a code repository that `implementation.md` names is that code's, and the code stays scanned. Where `implementation.md` does not name it, a code repository that also holds the documentation is left out as the docs repository, its code with it — nothing the run holds tells the two apart — and on a `/document` run whose record holds no block, that command's Phase 0 step 3a names it above the nothing-built question, among the repositories the script's `excluded` names. `--exclude` leaves out nothing for a path inside a repository, or outside any. The script leaves out every clone whose `origin` slug is one of theirs, a second clone of either included, and drops every pull request in a repository of that name: their commits and pull requests carry the run's tokens by the family's own conventions — the specs repository's artifact commits and handoff pull-request titles, the docs repository's squash subjects — and read as code they would verify a requirement by its own text.
- **Where `implementation.md` names the repository that holds the docs.** That repository is scanned whole, with no pathspec (§1). Its `/document` squash commits name the key (§4), come back `via: message`, and Phase 3 hands them to `diff-summarizer` as unrecorded work: "a commit only the scan found … `{branch_from: <its sha>, branch_to: <its sha>^}`" (DOC:569–570). The text never calls this an accepted false positive. KDM:23 states only the opposite principle, "is that code's, and the code stays scanned". On such a run the nothing-built question is never put, because the block suppresses it (DOC:248), so the harm is docs diffs read as code, not a wrong answer to the question.
- **Gaps in the rule as written:**
  - In a no-block run, the docs exclusion matters only because every clone in the map is a `--repo`.
  - In a with-block run, an unnamed docs repository is not scanned anyway. Its exclusion then only hides its pull requests from the "found but not read" list.
  - With `/release-notes --no-docs`, docs grounding returns before resolving `docs_root` (`docs-grounding.md`:24–26), so "the one its documentation grounding resolved" names nothing. Whether `${DOCS_PATH:-/workspace/docs}` is still passed is unstated.

## 3. How the docs repository and its content are known, and when

- **Docs signals** (DOC:221–224), checked at the git root on rung (a):
  > - `package.json` with any script matching `*:start`, `*:build`, `*:lint`, `docs:*`, or
  > - any of `.docstack/`, `mkdocs.yml`, `docusaurus.config.js`, `antora.yml`, a Vale configuration file under any of the five names Vale reads (`.vale`, `_vale`, `vale.ini`, `.vale.ini`, `_vale.ini` …), `DOCUMENTATION-GUIDELINES.md`, or
  > - a `_snippets/` directory at any level under the repo root.
- **The rungs**:
  - (a) DOC:228: "Run `git rev-parse --show-toplevel` from cwd … If it succeeds **and** ≥ 1 docs signal is present there → `docs_repo_path` = that git root".
  - (a.5) DOC:229: `${DOCS_PATH:-/workspace/docs}` "carries ≥ 1 docs signal … or an in-repo `.dev-workflows/docs-profile.yml`".
  - (b) DOC:230: a git root under `${REPOS_PATH:-/workspace}` with a profile or a signal.
  - (c) DOC:231–240: ask. *Use cwd anyway* "sets `docs_repo_path` = the git root of cwd".
- **The lift** (DOC:242): "Record the directory the rung answered with as `docs_repo_resolved`, and set `docs_repo_path` to its git work-tree top level … `$DOCS_PATH` at (a.5) and a path entered at (c) can name a site below one — a monorepo's `website/` … `docs_repo_resolved` is kept for what the site's own directory decides: step 4(c) hands it to inline profiling, step 6's `.obsidian/` walk starts from it, and step 7's preflight and Phase 6.4's style check look there". **So the pre-lift path is kept, as `docs_repo_resolved`, and is in hand at step 3a.** It differs from the top level only on (a.5) and on an entered path at (c). Rungs (a) and (b) and *Use cwd anyway* "already answer with a top level".
- **Write context `non_docs_repo`** (DOC:331, step 6) is a git repository with no docs signal that the operator confirmed at (c). It is computed after step 3a, but its inputs are known at step 2.
- **The profile** (DOC:279–282): (a) the in-repo `<docs_repo_path>/.dev-workflows/docs-profile.yml`; (b) the built-in one, where `is_known_docs_repo` (step 3, DOC:246); (c) generated by inline `/docs-profile`, which "cuts its branch, writes … commits it". Step 3a stands deliberately before (c): "before step 4 because step 4(c)'s inline profiling cuts a branch and commits in that repository" (DOC:248).
  - An in-repo profile is a plain file and is readable at step 3a. The built-in profile is decided at step 3, also before step 3a.
  - **A generated profile does not exist yet at step 3a.** That is the case of a first run in a repository with no profile.
- **What the profile says about where docs live** (`docs-profile-schema.md`:16–19, 99, 103, 123): "Every path the profile records is relative to that top level — `spaces[].content_root` and `snippet_root`, `builds[].config` and `out`, `announcement_pages[].path`, `images.root`."
  - `spaces[]`: "A page belongs to whichever entry's `content_root`/`snippet_root` prefixes its path, and is written there and nowhere else."
  - `source_repos[]`: "the code repositories this portal documents", written by `/docs-init` and `/docs-audit` and optional.
  - `commit_convention` is optional.
  - No field names navigation or sidebar files.
- **The built-in default's roots** (`docs-profile.default.yml`): `cloud/_content` and `self-hosted/_content`; snippet roots `cloud/_snippets` and `self-hosted/_snippets`. It applies only when the repository has that exact layout.
- **`/release-notes`**:
  - Its docs root comes from `resolve-docs-grounding` in Phase 2 (RN:349): `--docs <path>` else `${DOCS_PATH:-/workspace/docs}` (`docs-grounding.md`:24–29).
  - It is never lifted to a top level.
  - **There is no profile anywhere in `release-notes.md`**; `grep -n profile` matches only the usage line.

## 4. What `/document`'s own commits look like

| Writer | Paths staged | Subject | Key? |
|---|---|---|---|
| `/document` Phase 6.3 (DOC:997) | `git -C <docs_repo_path> add -- <each path in files_written that lies under docs_repo_path>`, then committed by pathspec | message file "as `finish-and-handoff.md` §2 writes and removes it"; its content is not stated separately | squashed at 8.5 whenever 8.5 runs |
| `/document` Phase 8.5 squash (DOC:1369–1371; `finish-and-handoff.md`:44–61) | every path under the docs repository the run wrote or edited (pages, snippets, images, cross-link and nav edits, Agent 1's edits), "save a path of Agent 1's that Phase 8 reported", squashed onto `merge-base` or onto `profile_commit` | "follows `profile.commit_convention` when present (example-docs: `<KEY> <summary>`); for a repo with no such field, infer from recent `git log` / `CONTRIBUTING` (a ticket-key prefix, or a conventional-commits `docs:` prefix), else fall back to `<KEY> <summary>`. The key carries traceability" | yes, normally |
| inline `/docs-profile` (`docs-profile.md`:193, 215, 219) | `git -C <repo-root> add .dev-workflows/docs-profile.yml CLAUDE.md`, on branch `dev-workflows/docs-profile-bootstrap`, which Phase 6.2 renames | `docs: add/refresh .dev-workflows/docs-profile.yml` | no, and it stays a distinct first commit (DOC:1370) |
| `/docs-init` (`docs-init.md`:223) | "the scaffold's own paths, enumerated": the `scaffold-tree.md`:15–69 tree | `docs: scaffold the documentation portal (docs-init)` | no; it never writes into a code repository (`docs-init.md`:370) |
| `/docs-brand` (`docs-brand.md`:260) | "only the remaining files Phase 8 wrote or Phase 9 edited" (theme config, `docs/assets/`, `docs/stylesheets/extra.css`) | `docs: apply brand colours and logo (docs-brand)` | no |
| Phase 8.6 applied proposals (DOC:1426) | `CLAUDE.md`, `.claude/memory/` | left uncommitted, "deliberately" | — |

- **Branch.** It is named by repo convention, with fallback `<prefix>/<key>-<slug>` and prefix fallback `docs/` (DOC:965, 973). The run only offers a push (DOC:1378). `/document` never opens the pull request. The title is "per `commit_convention` (e.g. `<KEY> <summary>`)" (`finish-and-handoff.md`:96). The GitHub footer hands the user `gh pr create … --title '<title>'` (DOC:1390).
- **The merge method is the host's and the user's choice.** A squash makes one commit whose subject is the pull-request title, which is the case KDM:23 calls "the docs repository's squash subjects". A merge commit keeps the branch's own commits: the keyless profile commit and the keyed squash. A rebase keeps them too.
- **Can a documentation commit be told by anything but paths? No.**
  - The subject follows a per-repository convention, or is inferred.
  - The plugin writes no trailer: `finish-and-handoff.md` §2 names none, and IF:181 gives `/implement` a `Work-Item:` trailer only.
  - The author is the operator's git identity.
  - The branch name disappears on a squash, and appears in a merge commit's subject, which the scan never reads (`--no-merges`).
  - Writer- and reviewer-made commits with keys look the same as a developer's.
- **`/release-notes`' own commits.**
  - It appends to `release-notes.md` in the PRD folder, which is in the specs repository.
  - It hands off through `handoff-to-main` in `$SPECS_PATH` (RN:702, 717).
  - It writes nothing in a docs repository: RN:322 "NEVER write into a docs repo, a code repo…", and RN:688.

## 5. Could a path rule work? Measured in scratch repositories (git 2.43.0)

**Fixture `lab/mono`.** Each commit appends to the files listed.

| commit | message | files |
|---|---|---|
| `base` | — | `src/app.py`, `docs/index.md`, `mkdocs.yml` |
| C1 | `code only [ACME-7]` | `src/a.py` |
| C2 | `ACME-7 Document intake` | `docs/intake.md` |
| C3 | `mixed [ACME-7]` | `docs/x.md`, `src/b.py` |
| C4 | `ACME-7 nav only` | `mkdocs.yml` |
| C5 | `ACME-7 profile+CLAUDE` | `.dev-workflows/docs-profile.yml`, `CLAUDE.md` |
| C6 | `ACME-7 README only` | `README.md` |
| C7 | unrelated code | — |
| C8 | `ACME-7 image only` | `docs/img/shot.png` |
| C9 | `[ACME-7]` | `src/d.py`, on branch `feat`, merged `--no-ff` as `Merge feat [ACME-7]` |
| C10 | docs on main | — |

**(a)** `G='--grep=(^|[^A-Za-z0-9_-])ACME-7([^A-Za-z0-9_-]|$)'`:
```
git log --no-merges -E -i "$G" --          → C9 C8 C6 C5 C4 C3 C2 C1          (today)
… -- . ':(exclude)docs' ':(exclude)mkdocs.yml'  → C9 C6 C5 C3 C1                (C2, C4, C8 dropped; C3 mixed kept; C1 kept)
… + ':(exclude).dev-workflows' ':(exclude)CLAUDE.md' ':(exclude)README.md' → C9 C3 C1
… -- ':(exclude)docs' ':(exclude)mkdocs.yml'  (no '.') → same as with '.' (git ≥2.13 implies it)
```
Yes, the rule does exactly that: a docs-only commit is dropped, and a mixed commit and a code-only commit are kept. Anything the exclusion list misses counts as code: C5 and C6 here.

**(b)** The script's own argv with the pathspec after its trailing `--` works unchanged. `git log HEAD -z --date=iso-strict-local --extended-regexp --regexp-ignore-case --format=%H%x1f%cd%x1f%B --no-merges "$G" -- . ':(exclude)docs' ':(exclude)mkdocs.yml'` returns the same five records, parseable by `_log`. **Do not add `--name-only`, which is not needed.** With `-z` it emits each path as its own NUL-separated record after the commit: `c69a5f9^C9…|\nsrc/d.py|49fe545^…`. `_log` happens to discard those, because they hold no `\x1f`. `--name-only` under a pathspec also lists only the matching paths: C3 shows `src/b.py` and not `docs/x.md`.

**(c)** `rev-list --no-merges --count HEAD --` gives 11. With `-- . ':(exclude)docs' ':(exclude)mkdocs.yml'` it gives 7, and `--full-history` also gives 7: base, C1, C3, C5, C6, C7 and C9. **Under a pathspec, `scanned` means "non-merge commits on HEAD that touch at least one non-excluded path"**, not the clone's history. DOC:262's `<slug>: <scanned> commits on HEAD … none names <tokens>` would need to say so.

**History simplification. This is a trap.** Fixture `lab/simp`:
- A `side` branch adds `src/e.py` `[ACME-9]` and then reverts it `[ACME-9]`.
- `main` gets a docs commit, then merges `side`.
```
no pathspec:                         S2 S1
pathspec (default):                  (nothing)
pathspec + --full-history:           S2 S1
```
A pathspec turns on git's default simplification, which prunes a side branch whose net effect on the pathspec is zero. **The scan must add `--full-history` wherever it adds a pathspec**, for `rev-list`, for the scan's `log`, and for the probe.

**The probe under a pathspec** (merges kept, bare token), on `mono`:
- With the default walk it **drops `Merge feat [ACME-7]`**, the very commit the probe exists to show.
- `--full-history` restores it.
- `--full-history` also shows a docs-only merge, `Merged in docs/ACME-7-intake (pull request #12)`, whose second parent touched only `docs/`. It is shown wherever the mainline moved on code meanwhile (fixture `mono2`), because a merge that differs from either parent is shown.
- A probe that should ignore documentation merges needs a first-parent test per merge, for example `git diff --quiet M^1 M -- <pathspec>`. The probe is report-only, so this costs only noise.

**Filtering a given SHA set**, which the pull-request layer's `landed` list needs:
```
git log --no-walk=unsorted --format='%h %s' C2 C3 C5 C8 -- . ':(exclude)docs' ':(exclude)mkdocs.yml' ':(exclude).dev-workflows' ':(exclude)CLAUDE.md'
→ e5dd639 C3 mixed docs+code [ACME-7]
```
That is one call per clone. `git diff-tree --no-commit-id --name-only -r <sha> -- <pathspec>` per commit works too.

**(d) Cost**, as wall clock, each figure stable over two runs:

| history | `rev-list --count`, without → with pathspec + `--full-history` | grep `log`, without → with |
|---|---|---|
| synthetic, 100,000 commits, 3-level tree, built with `fast-import` | 0.20 → 0.66 s | 0.23 → 0.70 s |
| a local 59,094-non-merge-commit documentation clone, 25k files, excluding its largest top-level directory | 0.07 → 0.30–0.37 s | 0.29 → 0.52 s |

- The second row is the same with `core.commitGraph=false` (0.35 → 0.56 s). The cost is one tree diff per commit, and Bloom filters do not help a `:(exclude)` pathspec.
- It stays well inside `GIT_TIMEOUT = 60` s per call (KD:42).
- The pull-request layer's 300 s budget (KD:53) is unaffected.

**(e) A squash-merged docs pull request that also touched a code file** (C3's shape) is kept as work. That is correct for a commit a person made: it changed code and named the key. It cannot come from `/document`, which writes only in the docs repository's documentation paths. The one route is a human doc-comment fix, a false "built" no worse than the same commit in any code repository today.

**(f) A repository where the documentation is everywhere** (README-driven, `**/*.md`). Note that `*` crosses `/` in a pathspec without `glob` magic.
```
… -- . ':(exclude)*.md'          → C9 C8 C5 C4 C3 C1     (image, nav, profile still kept)
… -- . ':(exclude)*.md' ':(exclude)*.png' ':(exclude)mkdocs*.yml' ':(exclude).dev-workflows' → C9 C3 C1
```
- An extension class alone misses `/document`'s image, navigation and profile commits.
- An anchored name such as `mkdocs*.yml` does not match `website/mkdocs.yml`; that needs `**/` with `glob`, or `:(top,glob)`.
- **An extension rule is wrong for a product whose code is markdown**, such as this marketplace. There every commit would be excluded, which gives a false "nothing built". That failure is visible, because the question is asked.

## 6. The second-run case this must not break

R1 (`docs/superpowers/plans/2026-11-16-ladder-order-b3-document-asks.md`:43): "In the default layout the docs clone lies under `$REPOS_PATH` and its squash subjects carry the key: without the exclusion a second run on a key whose first run answered *Go on* finds 'commits' and never asks". Under a path rule, a first-run commit is found again exactly where it touched one path outside the exclusion set. The keyed commits are the 8.5 squash, or a host squash, which holds the union of everything below, and on a merge-commit landing also the profile commit, via the pull-request layer. **Every path the family can commit into a docs repository:**

- **`doc-writer`** (`doc-writer.md`:40–50):
  - pages at `target_path` "under whichever `profile.spaces[]` entry's `content_root`/`snippet_root` prefixes it";
  - new snippet files "in the repo's idiomatic `_snippets/` location", with any extension;
  - local images at `dest`: "typically `<page-dir>/img/` or the detected idiomatic directory", or `images.root`, default `docs/assets`;
  - edits to `cross_links.from` pages, which `doc-planner` "extend[s] with sidebar/nav files if the repo has them" (`doc-planner.md`:99; `doc-location-finder.md`:53, "a sidebar/nav file that enumerates sect…"). These can be `mkdocs.yml` `nav:`, `sidebars.js`/`.ts`, `_category_.json`, `SUMMARY.md`, `nav.adoc` or `.pages`. No profile field records them;
  - `announcement_pages[].path`.
- **`doc-fixer` and the style check** edit the same files.
- **Phase 8 Agent 1** (DOC:1292–1296) edits "README.md, CHANGELOG.md, docs/, or any .md files at its top level or in the docs tree … an index/sidebar entry". In a monorepo that is the product's own `README.md` and `CHANGELOG.md`.
- **Inline `/docs-profile`**: `.dev-workflows/docs-profile.yml` and the root `CLAUDE.md`. These are keyless, but a merge-commit landing would bring them back.
- **`/docs-init`**, keyless: `mkdocs.yml`, `mkdocs.internal.yml`, `.gitignore`, `.vale.ini`, `requirements-docs.txt`, `styles/config/vocabularies/Project/accept.txt`, `docs/**`, `.dev-workflows/docs-profile.yml`, `.github/workflows/docs.yml` (`scaffold-tree.md`:15–68).
- **`/docs-brand`**, keyless: the theme keys of the mkdocs configs, `docs/assets/`, `docs/stylesheets/extra.css`.
- **`/release-notes`**: nothing (§4).

**So the set a path rule must cover**, for the second-run case to hold, is: the content and snippet roots; image directories; the navigation and sidebar files of every generator in use (the long tail is the residual risk); `.dev-workflows/`; the top-level `CLAUDE.md`, `README.md` and `CHANGELOG.md`; and, for a merge-commit landing, the profile commit's two paths. A miss is silent and permanent for that key, because no question is asked again.

## 7. The other blind spots of the same class

- **The specs repository.**
  - KDM:23 excludes `git -C <PRD folder> rev-parse --show-toplevel`, so the top-level condition is always met.
  - IF:208–210: "never the specs repository or the docs repository, whose commits carry the tokens by the family's own conventions".
  - Code in the specs tree's repository is unsupported but reachable. `specs-repo-git.md`:316: "**A specs tree inside a larger repository is unsupported** … emit one notice line, **set `specs_git: misrooted` for the whole run**, then continue". Rule 1 makes the notice "never fatal".
  - `/document`'s step 1 "runs on an `@<path>` run with `$SPECS_PATH` unset too" (DOC:218), so a specs tree committed inside a product repository and addressed by `@<path>` also excludes that product whole.
  - Same defect, same mechanism. No text names it.
- **`/release-notes`** shares KDM §1 (RN:392–396). It has no nothing-built question. Its effects:
  - **`$DOCS_PATH` = a code repository's top level, and the record names no repository.** The code is left out. The note is grounded without those commits, and the report line names it, `left out as never code: <slug>` (RN:760).
  - **`$DOCS_PATH` names a subfolder.** Nothing is excluded, so `/document`'s squash commits there are read as unrecorded work, enter the provisional read set, and are written into the note's `read:` scope comment (RN:417–428).
  - **The record names the repository.** It is scanned whole, as for `/document` (§2).
- **No third caller.** See §2.

## 8. What a run prints about it today (the sweep population)

Commands:
- DOC:256: step 3a's call with `--exclude the specs repository and docs_repo_path`.
- DOC:262: `Left out as never code: <the excluded slugs> — the scan did not look there.`, "a code repository that also holds the documentation among them, which `key-discovery.md` §1 leaves out on a record naming no repository". Also the four `Commit scan:` forms, the last of which is `Commit scan: no clone to read under <$REPOS_PATH> — every clone there was left out as never code; it did not look in any repository.`
- DOC:264: the last line's three forms. The middle one is `…or in a repository the scan did not read (<the not-read and left-out slugs>)`.
- DOC:269: the question's text, which is that last line.
- DOC:383: the Readiness row, `the commit scan did not look — <reason>`.
- DOC:527: "never the specs or the docs repository".
- DOC:539: "the same exclusions".
- DOC:541: *A later scan that finds none*, `it read none of <the not-read and left-out slugs>`.
- DOC:1388: the `pr-draft.md` clauses, `it read none of <the not-read and left-out slugs>`.
- DOC:1484: Phase 9, `- Left out as never code: [the excluded slugs | none]`.
- DOC:1486: Phase 9, "or ran and left every clone in the map out as the specs or the documentation repository".
- DOC:1559: Assumptions, which carries the same clauses.
- RN:393: "never the specs or the docs repository".
- RN:760: `left out as never code: <the excluded slugs> | none`.

References and script:
- KDM:14: the template's `--exclude` lines.
- KDM:23: the whole of "Never code", including "nothing the run holds tells the two apart".
- KDM:33: `excluded` — the slugs `--exclude` left out.
- KDM:58: §5, `Left out as never code: the excluded slugs.`
- IF:208–211.
- KD:19–21: the docstring, "--exclude names a clone whose repository is never code -- a specs or a docs repository: every --repo with its origin's slug is left unscanned, and every pull request in a repository of that name is dropped."

Pages:
- `plugins/docs-workflows/docs/commands/document.md`:71: "The scan leaves out the specs repository and the documentation repository, so the pages an earlier run published are never taken for the work they describe."
- The same page, :73: "each it left out as the specs or the documentation repository — a code repository that also holds the documentation site among them — as places the scan did not look", and "or it left out or could not read every clone there".
- `plugins/docs-workflows/docs/reference/references.md`:25, which does not state the exclusion.
- `docs/commands/release-notes.md` does not state it either (its :55).

Instruction tiers:
- `docs/maintainers/rationale.md`:690: "where the documentation site lives in a code repository and `implementation.md` names no repository, nothing the run holds tells the two apart, so that repository is left out as the documentation repository, its code with it", and "and, added in review, every clone left out as the specs or the documentation repository".
- `.claude/rules/*`: nothing states the exclusion. `docs-workflows.md`:39's map line names "the commit scan" only.

History and planning files:
- `plugins/docs-workflows/CHANGELOG.md`:42 (1.40.0, "A known limit, logged") and :651 (1.13.0, the exclusion's origin). Both are exempt as history.
- `docs/superpowers/to-fix.md`:281–287, the entry itself.
- `docs/superpowers/to-test-on-real-project.md`:214, a live check expecting today's behaviour.

Search used: `grep -rn -i 'left out\b\|did not look there\|--exclude\|excluded\b\|never the specs\|tells the two apart'` over `plugins/docs-workflows`, `plugins/workflows-core/references/implementation-format.md`, `docs/maintainers`, `.claude/rules`, `CLAUDE.md` and `README.md`, then reading each hit. The other hits, about the scaffold, conformance or the session cost, are unrelated.

## 9. Constraints a fix must meet

- **Copied scripts.** `key-discovery.py` is not one of them.
  - The CI step "Every plugin's copied scripts are the same" loops over `bounded.py tree-snapshot.py` only (`validate-catalog.yml`:290–309). `workflows-core-bounded-run.md`:17 lists the same two.
  - `check-docs.sh`:184 has `VENDORED_COPIES=""` in this edition. `gates-check-docs-late.md`:13: "The internal Claude edition lists the two scripts one of its plugins ships as copies of another's". Which two is not in this tree. Whether the internal editions carry `key-discovery.py` at all is the maintainer's knowledge.
- **The selftest** is a CI step (`validate-catalog.yml`:251–256). New cases go into the script's own `case_*` set. `_commit` needs a `makedirs` before it can write `docs/x.md`.
- **No rule binds a script and its reference to change in one commit.** I searched `CLAUDE.md` and `.claude/rules/` and found none. The "Prose is executed" rule (`CLAUDE.md` § Editing discipline) and `plugin-authoring.md`'s *Surgical Changes* make the reference, the commands and the script one change in practice.
- **Budgets** (`LC_ALL=C.UTF-8 wc -m`):

  | file | characters |
  |---|---|
  | `CLAUDE.md` | 35,989 (warns at 36,000) |
  | `.claude/rules/docs-workflows.md` | 19,998 (warns at 20,000; no room) |
  | `docs-workflows-gates.md` | 4,323 |
  | `release-notes.md` rules | 11,618 |
  | `plugin-updates-coupling.md` | 18,293 |

  A statement about this scan belongs to `plugins/docs-workflows/**`.
  - `docs-workflows.md` is full.
  - `docs-workflows-gates.md` shares its `paths:` but is titled "gate authorities".
  - The `release-notes.md` rules file's `paths:` do not include `key-discovery.*`.
  - So the options are a new split rules file with `paths: plugins/docs-workflows/**`, as `docs-workflows-gates.md` was split, or the rationale alone.
- **Versions.** `docs-workflows` 1.40.0 and `workflows-core` 1.95.1 (their `plugin.json`).
- **Does the change touch `workflows-core`? Yes, if the semantics change.** IF:208–211: "over the repositories this file names — or, when it names none, the repositories resolved from `$REPOS_PATH`, never the specs repository or the docs repository, whose commits carry the tokens by the family's own conventions — with one `--grep` for each key and each `workitem_key` below; git lists a commit that matches any of them anywhere in its message". IF:309 describes the pull-request layer, and the scan is "a commit … names a token whole".
  - A path rule turns "never the docs repository" into "never a documentation commit". That needs a `workflows-core` bump and a bullet in `plugin-updates-coupling.md`.
  - The family meaning, "the scan takes … non-merge commits whose message names a token", gains a path condition, which IF §4 must state.

## 10. Approaches, as I see them from the code

**(A) A path rule in the script: scan the docs-holding repository, ignoring documentation-only commits.**
- **Script.** It gains a per-repository exclusion set, for example `--docs-repo <top>` with a repeatable `--docs-path <pathspec>`, used in place of a whole-repository `--exclude` for the docs repository. For that clone:
  - `rev-list` and the scan's `log` take `--full-history -- . ':(top,exclude)<p>'…`;
  - `scanned` is redefined (§5c);
  - the probe takes the same pathspec with `--full-history`, plus a first-parent test for merges;
  - the pull-request layer stops dropping that repository's pull requests by name and filters each `landed` set by `git log --no-walk=unsorted … -- <pathspec>`, recording a docs-only landing with a `reason`;
  - the JSON gains, per repository, `docs_paths` and a count of the commits dropped as documentation-only.
- **Where the paths come from.**
  1. A fixed set stated once in KDM, of what the family writes: `.dev-workflows/`, the top-level `CLAUDE.md`, `.claude/`, doc-type extensions (`*.md`, `*.mdx`, `*.adoc`, `*.rst`, images), the docs-signal config names anywhere, the common navigation files, and `_snippets/` anywhere.
  2. `docs_repo_resolved` relative to the top level, where it lies below it, on `/document`; and the docs root relative to its top level on `/release-notes`.
  3. The profile's content and snippet roots, `images.root`, `builds[].config` and `announcement_pages[].path`, where a profile is readable at step 3a (in-repo or built-in). `/release-notes` has no profile.
- **Applied to the docs repository whether or not `implementation.md` names it.** That also fixes §0 item 2 and `/release-notes`' subfolder false positive.
- **Gets wrong.**
  - False "built": a `/document` commit touching a navigation file outside the set (the long tail: `_category_.json`, `.pages`, `toc.yml`…), or a snippet with a code extension under a non-`_snippets` root on a first run with no profile; a human change to the docs site's own code naming the key, such as Docusaurus `src/`; and, for a dedicated docs repository, any tooling commit naming a key, which today's whole exclusion ignores.
  - False "nothing built": a product whose code is markdown or images, if the extension class is global. That failure is visible, because the question is asked.
- **Size.** About 100 script lines and 6–8 selftest cases; KDM §1, §2, §3 and §5; DOC lines 256, 262, 264, 527, 1388, 1484 and 1486; RN:393 and 760; IF §4, with a `workflows-core` bump and a coupling bullet; the two pages; rationale:690; to-fix and to-test.

**(B) A marker rule: ignore the commits `/document` itself marks.**
- **Changes.** `finish-and-handoff.md` §2 writes a trailer into the 8.5 squash, and the profile commit's message gains one too. The script drops, in the docs-holding repository only, a commit whose body carries the marker.
- **Needs** nothing about paths.
- **Gets wrong.**
  - Every squash made before the marker's release is unmarked, so a dedicated docs repository cannot move off whole-repository exclusion without losing R1's guard for every existing first run. So (B) applies only where something else says the repository holds code.
  - A host squash-merge, or a reviewer's edited squash message, can drop a trailer. GitHub's and Bitbucket's default squash bodies are unverified here.
  - **A writer's own hand commit `ACME-7 document intake` that touches only docs pages carries no marker and counts as built.** I think this is decisive against (B) alone.
- **Size.** Small: one filter in the script and two message rules, plus the same sweep as (A).

**(C) No script change: treat a docs repository showing code as not left out, or ask.**
- **The run already holds evidence that the docs repository holds code:**
  - write context `non_docs_repo` (DOC:331);
  - `docs_repo_resolved` ≠ `docs_repo_path` (a site in a subfolder);
  - an in-repo profile whose `source_repos[]` names the repository itself by `origin`.
- **The ask variant** is a third option on the nothing-built question, "Scan <slug> too — it holds code", shown only where `excluded` names the docs repository, followed by a re-run without that `--exclude`.
- **Gets wrong.** Exactly R1's failure. After a first run that answered *Go on*, the second run's scan of that repository finds the first run's `<KEY> <summary>` squash and never asks again. In the ask variant, the operator's answer turns it into "built". It also keeps §0 item 2 and the `/release-notes` false positives.
- **Size.** Smallest: DOC step 3a, KDM §1 and the pages. No script, no `workflows-core`.

**(D) A's machinery, but show rather than count.**
- In the docs-holding repository, the path-filtered matches are not counted as work until the operator takes them. They are listed above the nothing-built question, which gains *Go on — read the <n> commits found in <slug>*.
- Where another clone found work, nothing is asked. So the docs-holding repository's path-filtered commits must then be read anyway, as in (A), or listed and lost.
- **Gets wrong.** Nothing silently, on the question path. That trades one more option on every such run for removing the silent false "built" in (A)'s long tail.
- **Size.** (A), plus the question's option and its wiring through Phase 3.

**(D′) Record what `/document` wrote and exclude exactly that.** Phase 8.5 knows the squash's path set. Its brittleness:
- `pr-draft.md` is overwritten per run, and its last line is reserved for `/ready` (`finish-and-handoff.md`:111–127);
- reviewers add files in the pull request;
- there is nothing for runs made before the change.

Not recommended.

**What I would build.** (A), applied to the docs repository always, named or not, on both callers. Its exclusion set is: the fixed family write-set in KDM, plus `docs_repo_resolved`'s subtree, plus the profile's roots where readable at step 3a. It uses `--full-history` throughout, a first-parent test for merges in the probe, and path-filtered `landed` sets in place of the drop by name. It fixes all three populations (§0 items 1–3) with one mechanism, needs no state, and is cheap (§5d). (C) and (B) each reintroduce R1's failure. (D) is the safer variant if the maintainer will not accept a silent false "built" from a missed navigation file.

**For the maintainer to decide:**
1. **Always, or only with evidence of code?** A dedicated docs repository's non-doc commits naming a key would start counting as work. I have not measured that population. Today it is ignored by design.
2. **The extension class: global (`*.md` anywhere) or confined to documentation directories?** Global is safe for R1 but wrong for a product whose code is markdown, such as this marketplace. Confined needs a site directory, which a top-level site with no profile does not give at step 3a.
3. **(A) or (D)** for the long-tail navigation files no profile field records. Alternatively, add a profile field such as `nav_files`.
4. **The specs twin.** Keep whole exclusion (the layout is unsupported) and state the limit in KDM §1 and IF §4, or path-rule it with `specifications/` and the bookkeeping directories.
5. **What `scanned` and the `Left out as never code:` line say** for a repository scanned outside its documentation paths. That is the wording of every line in §8.
