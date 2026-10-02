# Addressing — Shared Reference

The key grammar, the directory-naming convention, and the folder-resolution rule for **every** folder
under `$SPECS_PATH/specifications/` — a BRD, a PRD, or an Epic alike. This file is where addressing is
defined once rather than reinvented per caller. Design authority:
`docs/superpowers/specs/2026-08-31-specs-native-pipeline-design.md` §§4–5 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-31-specs-native-pipeline-design.md` retrieves it).

**Consumed by every command that addresses a folder in the specs tree.** Each calls `resolve-address`
(§3) and, where it validates a key before touching the filesystem, `key-valid` (§1). Those commands
are what `grep -l resolve-address plugins/*/commands/*.md` returns — re-run it rather than keeping a
list or a count here, since both went stale in this paragraph — and they, with the one shared
authority §7 names, all reach the tree through this file; `product-workflows:brd-format` and
`product-workflows:coverage-ledger-format` cite it for the key grammar and folder resolution neither
of them restates.

## 1. Key grammar

```
^[A-Z][A-Z0-9_]*(-\d+)+$
```

A key is one or more hyphen-numeric segments after a leading alphabetic token. `ACME-90`,
`ACME-90-01` and `ACME-90-01-01` are all valid — the grammar fixes no depth. **Shape is not depth**:
how many segments a key carries says nothing about where its folder sits, which §3 bounds at three
levels below `specifications/` regardless.

**One grammar, one namespace.** There is no second, narrower grammar for a "tracker" key: the plugin
reads no tracker, mints its own keys, and validates every key against this one expression. A caller
that re-states this grammar locally instead of citing this section is the defect family the plugin
source repository's `docs/maintainers/rationale.md` records under `resolve-against-a-known-set` — the
copies drift, and a key that is valid here hard-stops somewhere else.

**Shape only, never checked against anything.** A key names a folder in `$SPECS_PATH`, not a record
in a system that could confirm it exists. Validating shape and validating existence are two different
questions, and this section answers only the first; §3 answers the second.

### Entry point: `key-valid <KEY>`

Returns `valid` when `<KEY>` matches the grammar above, `invalid` otherwise. Takes no other input and
touches no filesystem — a pure string test, safe to call before `$SPECS_PATH` is even resolved.

## 2. Directory naming

```
<KIND>-<KEY>-<slug>/          kind ∈ BRD | PRD | EPIC
```

**Two invariants, and §3's bound is derived from the second:**

1. **Kinds appear in a fixed order down any path** — `BRD` → `PRD` → `EPIC`, each optional at the top.
   An idea-route PRD folder sits directly under `specifications/`; a BRD-route PRD folder is the
   slice folder inside its BRD. Both are `PRD-` folders, both are where the `prd.md` is authored, and
   both hold their Epics one level below. **The `BRD-` folder itself is never one of them**: it is a
   container, and `prd.md`, `ard.md` and `specification.md` are authored in the `PRD-` slice folders
   under it, never beside `brd/` and `coverage-ledger.md`
   (`product-workflows:coverage-ledger-format` §5).
2. **No path holds two folders of the same kind.** Every level is therefore identifiable from its own
   name without reading its parent, and the tree is at most three levels deep.

**Reserved subdirectory names are not folder kinds.** A folder under `specifications/` may hold
fixed-name subdirectories whose names carry no key and that are never resolved by one — `brd/`,
`grounding/`, `interview/`, `dev-workflows/`, `design/` (exported frame sets, one per immediate subdirectory, each
indexed per `references/grounding-format.md` §6.1–§6.2), `attachments/` (the text and markdown sources a run copied
into the folder — `product-workflows:idea-format`, *Vendored sources*), `revisions/` (a document's archived
prior revisions — `/product-workflows:update-prd` and `/product-workflows:create-prd` for a PRD, `product-workflows:proposal-format` for a proposal),
`bundle-<YYYYMMDD>/` (a customer package — `product-workflows:bundle-packaging`), `customer-sent-<YYYYMMDD>/`
(the material a `--sent` run records — `/product-workflows:brd-reconcile`), and `Doc screenshots/` (images `/docs-workflows:document`
stages for a page — that command's own Phase 5.6). None matches §3's `*-<KEY>-*` glob,
so resolution passes over them without a rule of its own, and none carries a `brd-link.md`, so
`/brd-split`'s positive test excludes them by construction rather than by an exclusion list.

**Each reserved name is defined once, elsewhere, and cited here.** This list is the register of names
resolution must pass over; it is not where any of them acquires its meaning. `brd/` is
`product-workflows:brd-format`'s (§1.1 for its `source/` capture, §2 for the inventory inside it),
`grounding/` is `references/grounding-format.md`'s (§2 for the finding files it holds, which
`/product-workflows:prd-ground` Phase 8 writes), `interview/` is `/product-workflows:brd-interview`'s
(Phase 9, which writes each round record, with `product-workflows:interview-tagging` §5 owning what a
round is), `dev-workflows/` is `references/specs-repo-git.md` §2.1's, `design/` is
`grounding-format.md` §6.1's — with §6.2 owning the index every set inside it must carry —
`attachments/` is `idea-format.md`'s, and each other name is the owner cited beside it in the list
above; a name added here without an authority to cite is a name two files will disagree about.

**A user whose own key begins with a kind token gets `PRD-PRD-1234-…`.** That is a documented
consequence of a documented convention, not a defect, and it is not hypothetical: a key like
`EPIC-008` yields `PRD-EPIC-008-01-orders` and `EPIC-EPIC-008-01-01-intake`. We cannot dodge every key
any user might pick, and a convention that can be relied on is worth more than one that bends. The
convention is stated in the README and in `docs/`; a user who then names their work `PRD-…` has chosen
the collision.

## 3. Resolution

### Entry point: `resolve-address <ARG> [<KIND>]`

**The caller-facing entry point.** Every command calls this one. `<KIND>`, when supplied, narrows the
search and refuses a mismatch; a caller that does not yet know the kind must not have to guess, because
the kind is frequently what decides the run's mode.

0. **Where `$SPECS_PATH` is set, run `specs-root-check` (below) first, whichever form `<ARG>` takes.**
   Its `misrooted` is a hard stop; otherwise take the branch `<ARG>` selects.
1. **`<ARG>` begins with `@` → the path branch.** Strip the `@`. A directory resolves to itself; a file
   resolves to its parent directory. Read the folder's `kind:` and `key:` (§4) and return `form: path`.

   **No glob, no tree walk, no ambiguity, and no §5 fallback** — the operator has already answered the
   question resolution exists to ask, and re-deriving an answer they supplied would only introduce a way
   to disagree with them. Past step 0, the one check a path still needs is the kind: a `<KIND>` argument that
   disagrees with the folder's own `kind:` is a stop naming both.

   **A path to a folder with no carrier** — one written before §4's rule, whose artifacts assert no
   `kind:` or `key:` (§5) — returns `kind` and `key` both **empty**: this branch searched for no key
   that could stand in, as §5's does, and none is parsed out of the name. The `<KIND>` check above
   refuses no such folder, since nothing is asserted to disagree. The caller places it by §4.1's
   positive evidence as it would any unprefixed folder, and a caller that needs the key — for an
   artifact's `key:`, a branch, a commit subject or a stop's text — stops, naming the folder and the
   two ways on: give it a carrier (§5), or, where its name is still unprefixed, address it by its
   `<KEY>` instead, which §5's fallback resolves with that key — a prefixed name with no carrier is
   found by no key at all (§5).

2. **Anything else → the key branch.** `key-valid <ARG>`; on `invalid`, return `status: invalid`. On
   `valid`, `resolve-key <ARG> [<KIND>]` and return `form: key`.

### Entry point: `specs-root-check`

**Refuse a `$SPECS_PATH` that points inside the tree.** `resolve-address` runs this as its step 0,
before either branch, so it runs on both address forms. Every folder this file addresses lives under
`$SPECS_PATH/specifications/`. A `$SPECS_PATH` set to `specifications/` itself, to a mount of it, or
to a folder inside it therefore resolves every key `absent`. A caller that creates the folder it did
not find would then create `<that path>/specifications/<KIND>-<KEY>-<slug>/` inside the tree, and
once one has, later runs find folders only in that nested tree.

**Why an `@<path>` is tested too.** A set-but-misrooted variable is a misconfiguration on every run,
whichever form the operator typed. An `@<path>` run that passed Phase 0 untested would meet the same
stop later, at a key resolution taken after its expensive work: `ard-resolution.md`'s, `/release-notes`
Phase 6's, or `/epics` Phase 2.6's. A caller that mapped every status but `found` onto "none" would
instead go on silently without the ARD or specification it should have read.

**What it tests, and where.** It tests only where `$SPECS_PATH` is set. Two signals are tested, (a)
by either of two tests, each against the filesystem and none by parsing a name:

- **(a) `$SPECS_PATH` is, or is inside, the `specifications/` directory.** Either of two tests shows
  it:
  - **`git -C "$SPECS_PATH" rev-parse --show-prefix` prints `specifications/`, or a prefix beginning
    with it**, i.e. it is the `specifications/` directory directly under a git work tree's top level,
    or any directory inside that one, a folder of any name included. **This test runs whether or not
    `$SPECS_PATH/specifications/` exists.** One that does is the damage a run made
    before this check existed, which created its folders at `specifications/specifications/`. A
    precondition that skipped it would keep the plugin reading the nested tree forever, and the
    users it would skip are exactly the ones who already met the misroot.
  - **`[ "$SPECS_PATH/../specifications" -ef "$SPECS_PATH" ]`, where `$SPECS_PATH` is not itself a
    git work tree's top level.** Where `git -C "$SPECS_PATH" rev-parse --show-prefix` succeeds, it
    must print a non-empty prefix. A specs repository cloned into a directory that happens to be
    named `specifications` is a repository root, not a directory inside one, whether or not it holds
    a `specifications/` yet. This test too runs whether or not `$SPECS_PATH/specifications/` exists.
    It catches the same misroot below a directory that is not a repository's top level
    (`<repo>/specs/specifications`), and a `specifications/` directory mounted on its own under that
    name, including one a run already wrote a nested `specifications/` into. Neither has a
    repository prefix for the first test to read.
- **(b) `$SPECS_PATH` is, or directly holds, a specs folder.** Either `$SPECS_PATH` itself has a §4
  carrier, or an immediate subdirectory whose name is not one of §2's reserved subdirectory names has
  one. **A carrier counts only where its directory's name passes §4.1's prefix test**: it begins
  `<KIND>-<key>-`, with `<KIND>` one of §2's three and `<key>` the key read off that carrier.
  **`$SPECS_PATH`'s own name is tested physically** (`cd -P`), so a `$SPECS_PATH` reached through a
  symlink is judged by the folder it reaches, never by the name of the link. **A subdirectory is
  tested by its own name**, and **one whose physical path resolves inside
  `$SPECS_PATH/specifications/` is skipped**. A convenience link at a correct root, such as
  `current -> specifications/PRD-A-1-a`, points into the tree rather than out of it, and must not
  stop every keyed run. The test applies whether or not `$SPECS_PATH/specifications/` exists. Every folder the plugin creates is kind-prefixed (§2), so a
  folder the tree holds passes the test. A carrier that is no specs folder does not: a `templates/`
  or `_templates/` copy of the plugin's own templates, or a `README.md` or `docs/` page carrying
  `key:` and a folder `kind:`. Those never stop a run, at a fresh root or a populated one. A nested
  `specifications/` that a misrooted run already wrote therefore cannot hide this signal. That covers
  a PRD folder an earlier `/idea` wrote `specifications/PRD-…` into, and a `specifications/`
  directory mounted under another name after any run wrote into it. This is the signal for that
  mount, whose parent (a) cannot see, and for a `$SPECS_PATH` pointing at a PRD or Epic folder in the
  tree, with or without keyed folders below it. Reserved subdirectories are skipped because
  `revisions/` holds archived copies of a PRD and `brd/` holds the inventory, and both of those assert
  their parent's key and kind. Stop testing at the first that qualifies; the stray-folder form of the
  stop below finishes the loop and names every subdirectory that qualifies.
  **What neither signal sees, as a class: a `$SPECS_PATH` that is, or holds only, folders not named
  `<KIND>-<key>-`, and that lies outside any work tree's top-level `specifications/`.** Inside a
  repository, (a)'s first test catches every such path by its prefix, a legacy unprefixed folder
  (§5) included. Outside one, a mount of a legacy folder, or of a PRD folder under another name,
  holding no prefixed folder below it, passes unseen. (a)'s second test still catches a mount named
  `specifications`.

A specs repository nothing has been written into yet has no `specifications/` and prints an empty
prefix, so it matches nothing and is never a stop. A `$SPECS_PATH` below its repository's top level
that holds `specifications/` (`<repo>/specs`) prints another prefix and is not stopped here either.
It is the first of the two unsupported layouts below, which `specs-repo-git` §3.1 reports in a
notice, and this check does not try to tell it apart.

**The value to set.** Walk up from `$(cd -P -- "$SPECS_PATH" && pwd)`, starting with that directory
itself and going at most three levels above it (§3's bound). Take the first directory `D` for which
`[ "$D/../specifications" -ef "$D" ]` holds **and** `git -C "$D" rev-parse --show-toplevel` succeeds
and prints the same path as `git -C "$D/.." rev-parse --show-toplevel`. **The value the walk found**
is `$(cd -P -- "$D/.." && pwd)`. Below and in the stop it is always written
`<the value the walk found>`, and `<value>` always means `$SPECS_PATH` as set: the two are different
paths in every case this check stops. **Both halves of the test are required.**
- **`-P`**: a `$SPECS_PATH` reached through a symlink (`H/specs → R/specifications`) resolves `..`
  logically to `H` without it. Setting `SPECS_PATH=H` would then pass this check and send the next
  creating command to `H/specifications/`.
- **The work-tree test**: a `specifications/` directory bind-mounted at `/workspace/specifications`
  has `/workspace` as its parent, which is not a repository. Naming it would send the operator from
  this stop straight to `specs-preflight`'s "not a repository" notice, which is the very symptom
  this check exists to prevent.

The value the walk found is `R` for an ordinary repository, through a symlink too, and for a PRD or
Epic folder inside one. Where `git -C "<the value the walk found>" rev-parse --show-prefix` prints a
non-empty prefix, as it does for `<repo>/specs` when `$SPECS_PATH` is `<repo>/specs/specifications`,
the stop still names it, since that is where `specifications/` sits. It does not present it as a
supported configuration, though: it adds that a specs tree inside a larger repository is
unsupported, so following it ends this stop and draws `specs-repo-git` §3.1's notice instead. Where no
directory on the walk passes, as with a mount of either kind, no path can be established, and the
stop says *the directory that holds `specifications/`* instead.

**Any signal is a hard stop, `status: misrooted`**, issued here as `ambiguous`'s is, so no caller
proceeds past it. A caller that maps the record's statuses onto outcomes of its own names
`misrooted` as a stop, never as `none` or `absent`. **The stop also sets `specs_git: misrooted` for
the whole run**, as `specs-repo-git` §3.3 G0 sets `specs_git: blocked`. A stopped run still runs its
emitter tail (`specs-repo-git` §4), and under that flag every emitter falls to its report-only tier:
cost (`cost-emission` §8), feedback (`feedback-emission` §2), follow-ups (`followup-emission` §2) and
`resume.md` (`session-hygiene` §1). `commit-artifacts` skips with the notice repeated, so the run
writes nothing under `$SPECS_PATH`.

**The stop is one line**, naming the variable, its value, the signal and the value to set, plus the
unsupported-layout clause where it applies. **Where only (b)'s second half fired and the walk found no
value**, that one-line form has nothing true to name, because the folder that fired sits beside `$SPECS_PATH`'s
tree rather than above it. The stop takes one of two other forms instead, chosen in this order. Where
the walk did find a value, `$SPECS_PATH` lies at or below a `specifications/` directory and the form
above is right, whichever signal fired.

- **The stray-folder form**, where `git -C "$SPECS_PATH" rev-parse --show-prefix` succeeds and either
  prints nothing, so `$SPECS_PATH` is a work tree's top level, or `$SPECS_PATH/specifications/` exists.
  The variable names the right directory, and specs folders sit beside `specifications/` rather than
  in it. The stop names no value to set. It finishes (b)'s loop and names every subdirectory that
  qualifies, with `<value>/specifications/` as where they belong, and nothing else, plus the
  unsupported-layout clause where `--show-prefix` is not empty: `<repo>/specs` holding
  `specs/specifications/` and a hand-placed `specs/PRD-S-9-x/` is that case.
- **The two-readings form** everywhere else: where `rev-parse` fails, or where `$SPECS_PATH` is below
  its repository's top level and holds no `specifications/`. Nothing on disk tells the two layouts
  apart. `$SPECS_PATH` may be a specs tree under another name: a `specifications/` directory mounted
  on its own, or a directory in a repository that holds folders the way `specifications/` does. Its
  own nested `specifications/`, where there is one, is then what a misrooted run left. Or it may be a
  specs root whose folders belong in a `specifications/` below it. The stop states both readings and
  what each needs, and the operator chooses. **The first reading always names the `specifications/`
  the folders end up in and sets `$SPECS_PATH` to that directory's parent**, never merely *the
  directory that holds it*: for `R/specs` holding PRD folders directly, that parent is `R`, which
  holds no `specifications/` yet, so every key would come back `absent` and a creating command would
  make `R/specifications/…` unstopped. Where `rev-parse` succeeds, the folders move into a
  `specifications/` beside `$SPECS_PATH` and the value is `$SPECS_PATH`'s parent. Where it fails, the
  path is a mount of some `specifications/` directory, which only the operator can name, and the
  value is that directory's parent, mounted whole. Where `rev-parse`
  fails, the second reading also needs `$SPECS_PATH` made a repository's top level, since
  `specs-repo-git` §3.1 reports a non-repository `$SPECS_PATH` on every run. Where it succeeds, the
  second reading carries the unsupported-layout clause.

**Where a run made while misrooted left anything behind, it adds one more line naming it.** That
covers a nested `$SPECS_PATH/specifications/` and the folders in it, and any of
`$SPECS_PATH/dev-workflows-feedback/`, `$SPECS_PATH/dev-workflows-cost/` and
`$SPECS_PATH/documentation/<slug>/dev-workflows/` that exist. **It is never added in the stray-folder
form**: there `specifications/` and those directories are where they belong. In the two-readings form
it is added under the first reading only, and the line says so, because under the second those
directories are where they belong too.
Each item is named with where it belongs: the nested folders in
`<the value the walk found>/specifications/`, and each bookkeeping directory at the same path under
`<the value the walk found>`. Where the walk found no value, they belong in *the specs repository's
`specifications/`* and at *its top level*.

What each one costs is not the same. `specs-repo-git` §2.1's classifier never stages
`dev-workflows-feedback/` or `dev-workflows-cost/` left at that depth, so G1 fires on every later
run, and a pending cost there never reconciles. **A `documentation/<slug>/dev-workflows/` and a
nested `specifications/` are worse, because part of each is committed in the wrong place.** Seen from
the repository's top level, which is where porcelain prints from, every path under either begins
`specifications/`. Their bookkeeping matches §2.1's `^(specs|specifications|vis)/.+/dev-workflows/`
shape, and an `implementation.md` or another of §2.1's single files in a nested folder matches its
single-file shape, so the classifier takes both for artifacts. **While `$SPECS_PATH` stays
misrooted they are never committed**: `git -C "$SPECS_PATH" add` names a path that does not exist
from there, which fails. **The first run after the variable is fixed commits them, in the wrong
place, unless they are moved first.** A deliverable in a nested folder is OTHER and fires G1 on
every run instead. A nested tree left in place also lies within `resolve-address`'s three-level
search (§3) from the corrected root, so a key whose folder only that tree holds resolves into it.
The line says so for each, and each has to be moved like the rest. **The plugin
moves nothing and gives no commands**: a move has to be right in every state the repository might
be in, and only the operator can see that state:

`SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, which <is itself a specifications/ directory | is inside the specifications/ directory | is itself a specs folder, asserting key <key> | holds the specs folder <subdirectory> directly> — every folder lives under $SPECS_PATH/specifications/, so this run would look for and create folders in the wrong place; it wrote nothing under that path, and its cost and feedback are reported here instead. Set SPECS_PATH to <the value the walk found | the directory that holds specifications/> where it is set, and re-run.[ <the value the walk found> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository.]`
`[stray-folder form: SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, <the top level of its repository | which holds <value>/specifications/>, and holds the specs folder(s) <subdirectory>[, <subdirectory>…] outside <value>/specifications/, where every folder lives. SPECS_PATH names the right directory; move <subdirectory>[, <subdirectory>…] into <value>/specifications/ yourself, commit the move, then re-run — the plugin moves nothing. This run wrote nothing under <value>, and its cost and feedback are reported here instead.[ <value> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository.]]`
`[two-readings form: SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, which holds the specs folder <subdirectory> directly, and nothing on disk says whether <value> is a specs tree under another name or a specs root. If it is a specs tree under another name, its folders belong in a directory named specifications/, and SPECS_PATH names that directory's parent: <move them into <the parent of <value>>/specifications/ yourself, commit the move, and set SPECS_PATH to <the parent of <value>> | set SPECS_PATH to the parent of the specifications/ directory <value> is a mount of, and mount that parent whole rather than the tree alone>, where it is set. If it is a specs root, move <subdirectory> and every other specs folder beside it into <value>/specifications/ yourself and commit the move<, and make <value> the top level of a git repository, which it is not | ; <value> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository>. Then re-run — the plugin moves nothing. This run wrote nothing under that path, and its cost and feedback are reported here instead.]`
`[<in the two-readings form only: If <value> is a specs tree under another name, m|M>isrooted runs left: <value>/specifications/ (<folder>, …), which belongs in <the value the walk found>/specifications/ | the specs repository's specifications/, and which the first run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong place, unless it is moved first; <value>/<bookkeeping directory>/, which belongs at <the value the walk found>/<bookkeeping directory>/ | the same path at the specs repository's top level[, which the first run after SPECS_PATH is fixed commits there in the wrong place unless it is moved first]; … Move them yourself, commit the move, then re-run — the plugin moves nothing.]`

**It offers no "enter the path" option**, unlike *Required path environment variable unset*
(`workflows-core:escalation-rules`). The wrong value lives in the environment, so a per-run override
would leave the next run, and every command that resolves no address, pointed at the same place. A
command that runs `specs-preflight` ahead of resolution (`/idea`) would also already have run it
against the wrong path. No signal holding → the branch `resolve-address` was going to take.

**Two layouts this does not support, each for its own reason.**
- **A specs tree inside a larger repository**: `$SPECS_PATH` below its repository's top level, as
  `<repo>/specs` holding `specs/specifications/` is. **The reason is git.** This plugin switches
  branches and commits in the repository `$SPECS_PATH` belongs to, and in one that also holds
  anything else, that moves the checkout of everything it holds. This check does not stop it;
  `specs-repo-git` §3.1 reports it in a notice and states the rule.
- **A specs root that is itself a subdirectory named `specifications`**: `<repo>/specifications`,
  holding its tree at `<repo>/specifications/specifications/`. **The reason is detection.** It prints
  the prefix `specifications/` and is byte-for-byte the damaged tree that (a)'s first test exists to
  catch, so it stops on every run, with its own `specifications/` or without one.
  `specs-repo-git` §2.1's classifier accepts the shape, but the stop's remedies, setting
  `SPECS_PATH=<repo>` and moving the tree up a level, turn it into the ordinary layout. Being below
  its repository's top level, it is also an instance of the first layout.

`workflows-core:specs-repo-git` §3.1 runs these same signals at run start, exactly as defined here,
sets the same `specs_git: misrooted` flag, and reports them in a notice that never stops the run: one line, plus one more line naming
anything a misrooted run left behind, exactly as the stop's. That notice is how a run that
resolves no address learns the cause.

### Entry point: `resolve-key <KEY> [<KIND>]`

Reached through `resolve-address`, whose step 0 has already run `specs-root-check`.

1. **Glob `specifications/**/*-<KEY>-*`, bounded at three levels below `specifications/`.** Do not
   narrow the glob by `<KIND>`: the folder **prefix** and the asserted **`kind:`** are allowed to
   differ, and on the BRD route they routinely do — `/brd-split` creates a slice as a `PRD-` folder
   whose `brd-link.md` asserts `kind: brd`, so globbing `BRD-<KEY>-*` for `<KIND> = brd` would miss a
   folder that exists, fall through to §5, miss again, and return `absent`. `<KIND>` is applied in
   step 2 instead, against what each candidate asserts.
2. **Filter the candidates by what each one asserts.** A glob matches *names*, and a name is not an
   assertion. Open each candidate and keep only those whose own frontmatter says `key: <KEY>` — and,
   where `<KIND>` was supplied, whose `kind:` equals it. This is §4's read, applied as a filter rather
   than only to the winner, and it is the only place `<KIND>` narrows anything. **This step is not optional and it is not
   tidiness**: `*-<KEY>-*` matches every folder whose key merely *extends* `<KEY>`, and a child keyed
   from its parent is the default wherever a command mints one. `/brd-split` proposes "the parent's key plus the next
   unused two-digit segment" and nests the child inside the parent, so on a tree holding
   `BRD-ACME-90-billing-intake/` with children `PRD-ACME-90-01-invoicing/` and
   `PRD-ACME-90-02-dunning/`, the bare glob returns **three** matches for `ACME-90` — and step 4 would
   hard-stop as `ambiguous` on a tree that is entirely correct, making the parent unaddressable by all
   six `/brd-*` commands and `/prd-ground` from the moment its first child exists. Exactly one of those three asserts
   `key: ACME-90`.
3. **Exactly one surviving candidate** → `status: found`.
4. **No surviving candidate** → apply §5's legacy fallback. Still nothing → `status: absent`. The
   caller decides whether that is a stop or a folder to create; this resolver never creates one.
   **A folder that matched the glob but asserts a different key is not a match**, so a legacy parent
   holding a prefixed child no longer returns the child: before the filter, `ACME-90-billing/` with
   `PRD-ACME-90-01-invoicing/` inside it globbed to exactly one match — the child — and returned
   `found` for it silently, with §5's fallback never reached because the prefixed glob had not missed.
5. **More than one surviving candidate** → `status: ambiguous`, a **hard stop naming every match**. Two
   folders *asserting* one key is a defect in the tree, and choosing between them would pick silently —
   the one failure mode a resolver must never have. Name `@<path>` in the stop as the way through it.

### The resolution record

```yaml
status:  found | absent | ambiguous | invalid | misrooted   # misrooted: specs-root-check's hard stop
path:    <absolute path of the resolved folder>   # found only
kind:    brd | prd | epic                         # found only; empty on a folder with no carrier (§5)
key:     <the folder's asserted key>              # found only; read, never parsed (§4) — on a folder with no carrier, the key searched for (§5), or empty on a path to one (§3 step 1)
form:    key | path                               # which form the caller supplied
legacy:  true | false                             # true when §5's fallback resolved it
matches: [ <absolute path>, … ]                   # ambiguous only
```

**It terminates because the bound is a constant, not a property of the key or of the tree.** Three
levels are scanned, each enumerating a finite set of directories; nothing found on disk can raise
that. So `resolve-key` always answers, and always after a bounded number of scans.

**The key's segment count buys no depth.** The default key `/brd-split` proposes is the parent's key
plus one more numeric segment (`/product-workflows:brd-split` Phase 3), and an operator may supply any key
satisfying §1 instead, including one that adds no segment. Either resolves identically: a segment count
is a naming convention, never a depth declaration, and §1's grammar deliberately fixes no depth.

## 4. The kind and the key are read, never parsed

`resolve-address` returns a folder's `kind` and `key` by **reading frontmatter**, never by splitting the
directory name.

**A directory name is not a safe place to parse from.** `PRD-ACME-90-01-orders` divides into key and
slug only under a rule about where numeric segments stop, and a slug beginning with a numeric segment
falsifies it. More fundamentally, a key re-derived by pattern is a key nothing in the tree ever
asserted — the standing rule `CLAUDE.md` states as *Resolve an identifier against a known set* —
so every match is a guess that a longer or differently-shaped identifier defeats. Reading the field
turns the guess into an assertion.

**Which artifact carries it is not a fixed filename at the folder's top level**, and must not be
written down as one there. The rule is:

> The command that creates a folder writes a keyed artifact into it in the same act, so a folder is
> never keyless — not even between its creation and its first document. (A folder written before
> this rule can be; §5 says what resolving one returns.) A resolver reads `kind:` and
> `key:` off the folder's **carrier**, found in this order:
>
> 1. **The folder's top level.** Take its files in byte-wise order of name, and the carrier is the
>    first whose frontmatter holds `key:` and a `kind:` naming a folder kind — `brd`, `prd` or
>    `epic`, §2's three kinds as the resolution record (§3) spells them.
> 2. **Else `brd/brd-inventory.md`.** Where no top-level file qualifies, the carrier is the
>    inventory inside the reserved `brd/` subdirectory — the one file below the top level that is
>    ever read for this.

**Why a kind outside the three is passed over.** A document's `kind:` names what that document is —
`ard`, `specification`, `design` — and an idea-route PRD folder holding an `ard.md` would otherwise
resolve as kind `ard`, a value the resolution record (§3) has no place for. **Why byte-wise order.**
"The first artifact" meant nothing until an order was fixed, and a slice shows why it matters: its
`brd-link.md` asserts `kind: brd` and its `prd.md` `kind: prd`, and a resolver that read whichever
it had opened anyway — which this rule used to allow — could return either for one folder. Byte-wise
order puts `brd-link.md` first, which is the reading the family's container refusals already give as
their reason for testing a directory prefix rather than an asserted kind: a slice asserts `brd`.

**Why step 2 exists.** `/brd-intake` creates a root BRD folder whose only artifact naming a folder
kind is the inventory it writes inside `brd/` (`product-workflows:brd-format` §2.1), and no command
writes one at a root's top level, so that inventory is a root's only carrier. The
`coverage-ledger.md` `/brd-intake` writes at the top level carries `key:` beside a `kind:` naming its
own document (`product-workflows:coverage-ledger-format` §2), which step 1 passes over — so step 1
alone finds nothing in that folder, and a strict reading of this rule left every root BRD
unresolvable. It is **one named file, not an enumeration of carriers per kind**: such a list would
go stale the first time a command writes a new artifact, and nothing in `scripts/` would catch it,
while this exception names the single place the family's own reserved subdirectory holds the
folder's identity.

**A reserved subdirectory is otherwise not a candidate for this test.** A frame-set index carries its
*parent's* `key:` while sitting in a directory named for the set (`design/checkout-flow/`), so every
frame-set index in the tree presents an apparent disagreement. Testing it there would tell an operator
their tree is broken on the ordinary `@<path>`-to-a-frame-set gesture, where the right answer is the
consuming command's own redirect (`/frames`'s `FRAMES_NOT_A_SPEC_FOLDER`: re-run against the folder
above). §2's reserved subdirectories are passed over by key resolution and are passed over here too,
save the one file step 2 reads — and step 2 reads it for the folder `brd/` sits in, whose key it
carries, never for `brd/` itself.

**A `key:` that disagrees with its folder name is a hard stop naming both.** That is the whole cost of
carrying identity in two places, and it buys the conversion of a hand-rename from a silent divergence
into a message.

### 4.1 A folder is placed by its prefix — or, where it has none, by positive evidence

**The level a run works at — a BRD container, a PRD folder or an Epic folder — is read off the
folder's kind prefix, never off the `kind:` its carrier asserts.** A BRD-route slice is a `PRD-`
folder whose carrier, `brd-link.md`, asserts `brd` (above), so a level taken from the asserted kind
puts every slice at the one level it is not. A `BRD-` folder is a container, a `PRD-` folder is
PRD-level, and an `EPIC-` folder is Epic-level, its PRD folder being the folder above it.

**A folder is prefixed only where its name begins `<KIND>-<key>-`**, `<KIND>` one of §2's three and
`<key>` the key this section read off its carrier — a test against a key the run already holds, so
nothing is parsed out of the name. A name that merely begins with a kind token is not prefixed: §5's
legacy name starts with the key, and a key may itself begin with a kind token (§2), so
`EPIC-008-01-orders/`, keyed `EPIC-008-01`, is a legacy folder and not an Epic folder — it does not
begin `EPIC-EPIC-008-01-`.

**A folder with no prefix is placed by positive evidence, in this order, and never by the absence of
a file.** It is one §5's fallback resolved (`legacy: true`), or an unprefixed folder an `@<path>`
names, which §3 resolves without the fallback and so without the flag.

1. **A BRD container** where it holds `coverage-ledger.md` or `brd/brd-inventory.md` and no
   `brd-link.md` naming a `parent:` — `product-workflows:coverage-ledger-format` §5.1's test, which
   that section owns and argues. It is taken first, as it is there, so that no evidence of a lower
   level can place a container at one.
2. **Epic-level** where the resolved `kind` is `epic`.
3. **PRD-level** where the resolved `kind` is `prd`, or where a `brd-link.md` names a `parent:` — a
   legacy BRD-route slice, whose carrier asserts `brd`.

A folder none of the three places is never guessed at: the caller stops, naming the folder and what
it carries — and, where what it carries is an `idea.md` and no `prd.md`, naming
`/product-workflows:create-prd <KEY>` too, the run whose `prd.md` places it by rule 3 when the caller
is re-run (on an `@<path>`, which returns no key for such a folder, §3 step 1 says how the operator
supplies it). That command is named by a caller for which it is a way on: one working at the PRD
level, which the placing lets re-run, or a BRD-route command refusing the folder, which names it as
the idea route's next step (`/product-workflows:brd-interview`'s and `/product-workflows:brd-split`'s
no-parent stops and `/product-workflows:prd-ground`'s two no-link stops in its Phase 0 step 6 among them). `/product-workflows:brd-intake` names no command for the folder it refuses, and its
own stop says why. **That stop binds a caller that needs the folder placed, and not every caller does:**
one that refuses only the levels it does not work at tests for those and proceeds on the rest, and
where what it writes asserts `kind: prd` beside the key, that file places the folder from then on.
`/product-workflows:create-prd` and `/product-workflows:idea` are two such callers, each stating its
own test. On a folder with no prefix, `/create-prd` refuses only what rules 1 and 2 place and writes
`prd.md`, and `/idea` refuses only what rules 1 and 2 place or a `brd-link.md` naming a `parent:`
marks as a slice, and writes `idea.md`. A legacy folder holding an `idea.md` and nothing any rule above
reads — where the idea route handed off before the prefixes, an `idea.md` then asserting no `kind:`
or `key:` (§5) — is the ordinary case: it is placed by none of the three until one of them writes
its file into it, and by rule 3 from then on.

**What a caller does at each level is its own, and so is its refusal of a level it does not work
at.** Where a refusal names the slices under a container, it finds them by
`/product-workflows:brd-split` Phase 0 step 9's positive test — each immediate subdirectory carrying
a `brd-link.md` whose `parent:` names the container — and never by a name match.

## 5. The legacy layout

A specs repo written before the kind prefixes existed holds `specifications/<KEY>-<slug>/`, with a BRD
slice, or a per-Epic subfolder, one level inside its parent. `resolve-key` therefore falls back to the **unprefixed** form —
matching `<KEY>{-|_}<slug>/` directly under `specifications/` first and one level inside a folder there
only where the top level kept no candidate, tolerating a human-adjusted slug and a stray extra `-`/`_`
immediately after the key, exactly as the pre-prefix resolution did.

**It matches on the folder name, and §3 step 2's filter drops only a candidate that asserts a
different key.** The pre-prefix resolution read no frontmatter at all — `brd-addressing.md` §2 and
each command's own feature-folder step matched the directory name alone
(`git show 8e2ec7b9^:plugins/dev-workflows/references/brd-addressing.md`) — and the artifacts a
pre-prefix folder holds usually assert nothing: `idea.md` gained `kind:` and `key:` on 2026-09-01
(7c1e19f7), a day after the prefixes (8e2ec7b9), and a PRD still named `<KEY>_<slug>.md`, or a
`brd-link.md` of that time, carries no `key:` either. So a fallback candidate is kept where §4 finds
it a carrier asserting `key: <KEY>` (and, where `<KIND>` was supplied, that kind), **or where §4
finds it no carrier at all**; one whose carrier
asserts another key is dropped, exactly as §3 step 2 drops it. Filtering out a folder that asserts
nothing would make unaddressable every folder this section exists to reach.

**What the record carries for a folder with no carrier.** `key` is the `<KEY>` the caller searched
for — a key the run already holds, which the name match tested the folder against, never one parsed
out of the name — and `kind` is empty. (An `@<path>` to such a folder searched for nothing, so both
are empty there; §3 step 1 says what its caller does.) The caller places the folder by §4.1's positive evidence, never
by a kind nothing asserted, and §4's hard stop on a key that disagrees with its folder name does not
fire, because nothing is asserted to disagree. A `<KIND>` argument refuses no such folder, for the
same reason. Once a command writes a keyed artifact into it — `/product-workflows:create-prd` writing
`prd.md` into a legacy folder holding only an `idea.md` is the ordinary case — that artifact is its
carrier from then on.

**The fallback is reached only after the prefixed glob has already missed**, so a prefixed tree resolves
exactly as it would if this section did not exist. A run that resolves through it sets `legacy: true`
and reports it **once per run** as deprecated. `@<path>` bypasses it along with §3's glob and filter.

**No migration command ships.** A user's specs repo is theirs, it is a git repository they review, and a
renaming script that cannot be tested against their tree is a liability. Renaming a folder is one
`git mv`, and the fallback above means they need never do it — **but a folder with no carrier is
renamed only together with the edit that gives it one**, in the same commit: add `key: <KEY>` and
its folder kind to the artifact §4 will read as its carrier — `prd.md`, or `idea.md` where the folder
holds no `prd.md` (`kind: prd`), `epic.md` (`kind: epic`), a slice's `brd-link.md` or a root's
`brd/brd-inventory.md` (`kind: brd`). Keeping a candidate that asserts nothing is this fallback's
exception alone: renamed without a carrier, the folder is found by §3's glob and dropped by its step
2 filter, which keeps only a folder asserting the key, while this fallback no longer matches its name
— so no key resolves it, and only an `@<path>` reaches it.

**The fallback covers the folder name and nothing inside it, which is a narrowing of what this
paragraph used to claim.** It said the fallback meant a user need never rename, unqualified — and that
covered filenames it never reached. Every command resolves an artifact by its **current** name and none
carries a fallback of its own, so a folder written before the artifact filenames lost their keys still
needs its `<KEY>_<slug>.md` renamed to `prd.md` and its `<KEY>_ARD.md` to `ard.md`. Two more `git mv`s,
and unlike the folder nothing resolves them for you: a command meeting the old filename reports the
artifact absent and stops on that, with a remedy written for a folder that never had one. **Each
renamed file also takes the `kind:` and `key:` its format now carries** — `kind: prd` and
`key: <KEY>` on `prd.md`, `kind: ard` and the key on `ard.md` — because those fields arrived in the
same commit as the keyless filenames (1da74804), so no file written under the old names carries
them. A `prd.md` asserting no `kind:` is no carrier and no PRD: §4 passes over it, so a folder holding
nothing else keyed is placed by nothing in §4.1, and every command that gates on `prd.md`'s own
`kind: prd` — `/product-workflows:epics`, `/product-workflows:prd-ground`,
`/product-workflows:brd-split` — reads the folder as holding no PRD. **The
unqualified claim was load-bearing in the wrong direction** — a resolver for the legacy artifact names
is derivable from it, and was derived in full, before anyone measured how many trees it would serve.
State the boundary here so the derivation stops at this paragraph.

## 6. Nesting

A PRD folder produced by `/brd-split` is not a sibling of its BRD — it lives **inside** it, and its Epics
live inside it in turn:

```
specifications/BRD-<PARENT-KEY>-<slug>/PRD-<CHILD-KEY>-<slug>/EPIC-<EPIC-KEY>-<eslug>/
```

`resolve-address <CHILD-KEY>` finds the middle folder through §3's glob without the caller ever supplying
the parent key — resolution alone locates a PRD folder from its own key.

**The folder `/brd-split` creates for a slice *is* the folder its PRD is authored in.** A slice exists
precisely to become a PRD, so giving it a directory of its own with a PRD directory nested inside bought a
level of tree for nothing. The merged folder holds the slice's own bookkeeping — `brd-link.md`,
`coverage-ledger.md`, `decisions.md` — beside the documents authored from it, which is what the idea route's
PRD folder already does with `idea.md`.

**Nothing is created below a PRD folder except its Epics** — invariant 2 of §2 says so, and this is the
path it forbids:

```
specifications/BRD-<KEY>-<slug>/PRD-<KEY>-<slug>/PRD-<KEY>-<slug>/     # never created
```

**Why, rather than a second inheritance rule.** A slice inherits `brd/source/` and its **requirement**
defect log from its BRD (`product-workflows:brd-format` §2.1, §4 — the route's separate code-defect log is
slice-owned and inherits nothing). A slice of a slice would have a parent holding neither: its
inventory header would name a `source:` path that does not exist, and a `rejected: [DEF#n]` disposition
taken against it would cite a defect log that is not there. Chasing every inheritance up to the
source-owning root would fix that, but nothing in practice needs it, and one rule beats two. **Every "its
parent's" in this route is therefore literal**: a PRD folder's parent is always a BRD that owns the source
document — which is what makes its one live inheritance, the parent's defect log behind a
`rejected: [DEF#n]`, a single hop.

**The cap is on nesting, never on allocation.** A folder whose ledger could not be walked would keep every
row `unallocated` forever and could never become PRD-eligible
(`product-workflows:coverage-ledger-format` §4, §5) — which would make slicing pointless, since a slice exists
precisely to become a PRD. Refusing a further child, not the walk, is the whole of the cap.

## 7. The shared fallback for existing commands

Every command outside the `/brd-*` family, `/prd-ground` and `/prd-proposal` that addresses a PRD
directory once resolved it as the flat form `specifications/<KEY>-<slug>/`, which on its own cannot see
a nested PRD (`/create-prd` on the BRD route authors into the `PRD-` slice folder one level inside a
BRD). **Every command that addresses a folder now reaches the tree through `resolve-address` (§3)**,
which searches every level §3 bounds and carries §5's fallback — so the fallback is reached by calling
§3, and a caller cites §3 (and §5 for the fallback itself), not this section. One shared rule, defined
here once rather than reinvented per caller.

**Re-derive the set; do not read it off this section.** `grep -l resolve-address plugins/*/commands/*.md`
returns every command that resolves a folder in the specs tree. No total is kept here, deliberately:
this section once carried two — *"twelve files"*, *"eleven commands cite this section"* — and both went
false, the second because no command cites it to reach the fallback (each cites §3; `/brd-split`
cites only its *Adoption is additive* rule) and both because the set grew past the table below
(`/implement`, `/vuln` and `/brd-proposal` resolve through §3 and are in no row of it).

**The table is a finding aid, not the set.** It names the resolving step, and what the resolved
directory is for, for eleven of those commands — all but the five `/brd-*` route commands,
`/prd-ground`, the proposal pair, `/implement` and `/vuln`. For `/frames` the directory is a folder of
any kind whose frame sets it indexes. A command absent from the table is not absent from the fallback.
The eleven rows:

| Command | Step (by name) | What the resolved directory is for |
|---|---|---|
| `/create-prd` | *Feature folder*, Phase 0 — Resolve inputs | the PRD it authors, and its rung-1 `idea.md` |
| `/update-prd` | *Feature folder*, Phase 0 — Resolve inputs | the frozen draft, any ARD, and the spec it grounds on |
| `/create-ard` | *Feature folder*, Phase 0 — Resolve input | the PRD it reads and the ARD it writes |
| `/epics` | *Resolve the PRD dir*, Phase 2.6 — PRD-level spec enrichment (optional) | the optional PRD-level spec |
| `/specify` | *Resolve the feature folder*, Phase 0 — Resolve input | the spec it authors, and each Epic subfolder under it |
| `/design` | *Map onto the specs repo + require the spec on main*, Phase 0 — Resolve input | the merged spec it takes over |
| `/ready` | *Map onto the specs repo (PRD dir + optional Epic subdir)*, Phase 0 — Resolve input | every artifact it judges |
| `/idea` | *Resolve the address*, Phase 0 step 1 | the folder `idea.md` is written into on the first write |
| `/release-notes` | *Resolve `run_phase`*, Phase 6 — Render the draft | the `run_phase` signal |
| `/document` | *Resolve the address*, Phase 0 step 1 | the `specs` files it grounds documentation in |
| `/frames` | *The address (mandatory)*, Phase 0 step 1 | the folder whose `design/*/` frame sets it indexes |

**One shared authority calls it too, and it is not a command:**

- `references/ard-resolution.md`, from step 1 of its *Resolution (most-specific first)*. It is where the
  fallback reaches an **ARD**: `/create-ard`, `/design`, `/implement`, `/specify`, `/epics` and `/ready`
  delegate ARD lookup to it rather than resolving an ARD path themselves, so their own resolution of a
  folder would not have found an ARD in a nested directory. `/implement` in particular reaches an ARD
  solely through it, though it resolves its own positional address with §3 on a keyed run.

**Where a handoff crosses two callers, both must resolve through §3.** `/create-prd` redirects to
`/update-prd` on finding an existing PRD (its *Prior PRD* step), including one found through this
fallback; `/idea` writes `idea.md` into the folder `/create-prd` then reads, resolving it with this
file's §3 on its first write and **never relocating it afterwards** (D7). A redirect, or a first write
into a folder a command with a narrower resolution then has to find again, is a dead-end handoff, which
is why neither was deferred as low-risk.

**Adoption is additive, for every caller.** §5's fallback is reached only where the prefixed glob already
returned nothing, so a key whose folder resolves at the first attempt resolves exactly as it did before
the fallback existed — and where a command creates the folder it did not find, it still creates it
with the §2 prefix: the fallback honors a legacy folder that exists, it never proposes one. The one shared authority creates nothing at all — `ard-resolution.md` is a reader, so for it the additive
claim is simply that a resolvable key returns what it returned before: the same `found` / `none` /
`unmerged`.
