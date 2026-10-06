# Branch Naming (shared)

Single source of truth for how a command that creates a git branch in a **code or docs repository** decides the branch name. A branch the family creates in `$SPECS_PATH` is outside it: `phase-handoff.md` §2.2 names that one, under the prefix authority of its §1 rule 3.

**The repository's own documented convention always wins.** This doc's job is to find that convention, fill its placeholders, and supply a name only when the repo documents none.

Commands that consume this: `/implement`, `/document` (keyed mode only — a direct-mode run creates no branch), `/docs-profile`, `/docs-init`, `/docs-brand` (standalone only — an `--inline` run writes on its caller's branch and creates none), `/upgrade`, and `/vuln` (applied by the orchestrator, once per CVE in its Step 1, per the `/vuln` "Git Workflow" spec — `vuln-fixer` creates the branch it is handed and never derives a name).

---

## 1. Resolution order

### 1.1 Read the repo's documented convention (always first)

In priority order, look at the **target repo's** root for `CONTRIBUTING.md`, `CONTRIBUTION.md`, `README.md`, `DOCUMENTATION-GUIDELINES.md`, and `CLAUDE.md` (plus `.claude/`). Grep each for a branch-naming section — case-insensitive, patterns like "Branch name", "Branch naming", "naming your branch".

Extract both the **pattern** and any surrounding **guide** prose; real conventions often state the rule in prose the pattern alone does not capture.

**Every pattern below is quoted from a repository's own file, not written by this plugin.** A real
convention frequently names the tracker its team uses, and this file's job is to *recognise* what it
finds — so a token like `<JIRA-ISSUE-KEY>` appears here as foreign text being matched, never as this <!-- vendor-token-ok: quoted from a repository's own convention file, not this plugin's vocabulary -->
plugin's own vocabulary, and never as something a run emits on its own. The rule this file supplies
when a repository documents nothing (§1.4) names no vendor at all. Example, quoted verbatim from one
repository's `CONTRIBUTING.md`:

```text <!-- vendor-token-ok: verbatim quote of one repository's own CONTRIBUTING.md -->
<your-name-or-initials>/<JIRA-ISSUE-KEY>-<short-branch-name>
<your-name-or-initials>/noissue-<short-branch-name>
```

> Start the branch name with your name or initials. Choose an identifier and stick to it for all branch names.

If a convention is found it defines the name's **shape**. Do not reshape it, do not add segments it does not have, and do not drop segments it requires. If several patterns are documented, offer them all to the user.

### 1.2 Classify the pattern's segments

For each placeholder in the documented pattern, decide where its value comes from:

**The tokens below are quoted, not used** — the same rule §1.1 states, applied to the recognition
table. They are what a repository's own `CONTRIBUTING.md` may literally write, including a tracker's
name, and this file's job is to match them. Genericising the list would not make the plugin more
vendor-neutral; it would stop the reference recognising the files it reads, and a repo whose
convention says `<JIRA-ISSUE-KEY>` would silently fall through to §1.4's no-convention branch and <!-- vendor-token-ok: quoted from a repository's own convention file, not this plugin's vocabulary -->
get a branch name its team does not use.

| Segment kind | Recognised as | Filled from |
|---|---|---|
| **Identity** | `<your-name-or-initials>`, `<user>`, `<username>`, `<name>`, `<initials>`, `<prefix>` — or guide prose telling you to start with your name/initials | the **identity ladder** in §2 |
| **Issue key** | `<JIRA-ISSUE-KEY>`, `<JIRA-TICKET-KEY>`, `<KEY>`, `<TICKET>`, or a literal `noissue` / `NOISSUE` alternative |  <!-- vendor-token-ok: these are tokens a repo's OWN convention file may literally contain, not this plugin's vocabulary --> the run's already-resolved key; its no-issue literal (matching the documented capitalisation) when the run has no key |
| **Description** | `<short-branch-name>`, `<slug>`, `<name>`, `<rest>` | this command's own slug rule (§3) |
| **Literal** | anything not a placeholder (`feat/`, `docs/`, separators) | used verbatim |

**A pattern with no identity segment gets no identity segment.** Never inject initials into a convention that does not ask for one — a repo documenting `feat/<slug>` must produce `feat/add-oauth`, not `iv-gu/add-oauth`. The identity ladder runs **only** to fill an identity placeholder, or in the §1.4 no-convention case.

### 1.3 Assemble and confirm

Fill every segment, then confirm the result with the user — identity strings and slugs are subjective, so this confirmation is required even when the name came straight from a documented convention:

```
choices: ["Use proposed name: <name>", "Edit name (you'll be prompted)", "Cancel"]
```

### 1.4 No documented convention

Only when §1.1 finds nothing: build **`<prefix>/<key>-<slug>`** on a keyed run — the key the run resolved, so the branch name carries the key for a **person** reading the log or the branch list (`references/implementation-format.md` §3); it is no recovery path for that file's §4 commit scan, which matches a token only as a whole key and so never reads one out of a branch name — or `<prefix>/<slug>` where there is no key. `<prefix>` comes from the identity ladder in §2 (falling back to this command's default in §2.4) and `<slug>` from §3.

---

## 2. Identity ladder

Used to fill an identity placeholder (§1.2) or the whole prefix (§1.4). Apply in order; **stop at the first check that yields a non-empty value.**

### 2.1 `$GIT_USER_INITIALS`

```bash
echo "$GIT_USER_INITIALS"
```

If set and non-empty, use it **verbatim** (never append a trailing `/` — the caller inserts separators). This is the recommended way to lock one identifier across every workflow and every repository, which is exactly what conventions like example-docs' "choose an identifier and stick to it" ask for. Examples: `GIT_USER_INITIALS=iv-gu` → `iv-gu`; `GIT_USER_INITIALS=ivgu` → `ivgu`.

### 2.2 `git config user.initials`

```bash
git -C <repo_path> config --get user.initials
```

Same semantics as §2.1. Set once per repo, or globally with `git config --global user.initials <initials>`.

### 2.3 Inferred from existing branches

```bash
{ git -C <repo_path> for-each-ref --format='%(refname:lstrip=2)' refs/heads
  git -C <repo_path> for-each-ref --format='%(refname:lstrip=3)' refs/remotes; } 2>/dev/null \
  | grep -vx 'HEAD' | sort -u | head -200
```

Local branches as they are, and remote ones with the remote's name taken off, so `origin/iv-gu/x` counts as `iv-gu/x`, once — `sort -u` makes a branch that is both local and pushed one branch of the sample, not two. `branch -a --format='%(refname:short)'`, which this listing replaced, printed `origin/…` for every remote branch and `origin` for the remote's `HEAD`, so a repository with many pushed branches adopted `origin` as an identity.

Scan for `<identity>/<rest>` where `<identity>` is **2–8 characters matching `[a-z0-9][a-z0-9-]*`** — so hyphenated forms (`iv-gu/`, `john-smith/`, `a-hue/`) count alongside unhyphenated ones (`ivgu/`, `jdoe/`, `mz23/`) and the generic prefixes (`feat/`, `docs/`, `fix/`, `chore/`, `feature/`, `bugfix/`, `hotfix/`, `release/`, `story/`).

**The nine prefixes of the plugin's own specs-repository branches — `idea`, `prd`, `ard`, `spec`, `design`, `ready`, `brd`, `frames` and `kb` (`specs-repo-git.md` §2.2) — are never a candidate.** They name branches the plugin cuts for its deliverables, not a person or a team's convention. Counted, they gave a code branch cut inside the specs repository — a direct `/implement` run from there — one of those prefixes, and the plugin then treated the user's code branch as its own.

Adopt a candidate when it accounts for **≥ 30 %** of the sample **and** occurs **≥ 3** times.

Tie-breaking:

- When filling an **identity** placeholder, ignore the generic prefixes entirely — they are not identities.
- Otherwise prefer a **short non-generic** candidate (≤ 6 chars) with ≥ 3 occurrences over a generic one; that is the team convention, and generic prefixes are usually older or external contributions.
- Among equally-ranked candidates of the same kind, prefer the **alphabetically first** for determinism.

### 2.4 Per-command fallback (§1.4 case only)

| Command | Fallback prefix |
|---|---|
| `/implement` | `feat/` |
| `/document` (keyed mode) | `docs/` |
| `/docs-profile` | `docs/` |
| `/docs-init` | `docs/` |
| `/docs-brand` (standalone) | `docs/` |
| `/vuln` | `fix/` |
| `/upgrade` | `chore/` |

A fallback is never valid for an **identity** placeholder — `feat/` is not a name. When §2.1–§2.3 yield nothing and an identity is required, go straight to §2.5.

### 2.5 Mandatory escalation

When the ladder yields nothing, the command MUST ask before creating the branch (canonical wording in `escalation-rules.md` → "Branch prefix undetected"):

```
"I couldn't infer a branch prefix from $GIT_USER_INITIALS, `git config user.initials`, or existing branches. This command's default is `<fallback>`. What prefix should I use?"
choices: ["Use `<fallback>` (default for this command)", "Use my initials — I'll enter them"]
```

When an **identity** placeholder is being filled, the fallback choice is omitted — the documented convention requires a real identity, so ask for it directly:

```
"This repo's documented convention starts the branch with your name or initials, and I couldn't infer one. What should I use?"
```

Either way, prompt for the value with:

```
"Enter your initials (lowercase; 2–8 characters from [a-z0-9-], starting with a letter or digit, e.g. `iv-gu` or `ivgu`):"
```

Then surface, once, without persisting anything:

> Tip: set `GIT_USER_INITIALS=<initials>` in your shell profile, or run `git config --global user.initials <initials>`, to skip this prompt next time.

---

## 3. Slug (owned by each command)

Used for the description segment (§1.2) or the §1.4 `<slug>`:

- `/implement` — derived from the description: lowercase kebab-case, max 40 chars, punctuation and special characters stripped
- `/document` (keyed mode) — first 4–6 content words of the PRD summary, kebab-case
- `/docs-profile` — `docs-profile`
- `/docs-init` — `docs-init`
- `/docs-brand` (standalone) — `docs-brand`
- `/vuln` — `<CVE-ID>`
- `/upgrade` — `upgrade-<component>-to-<version>`, or `upgrade-<first>-and-<N>-more` for a batch

When the documented pattern has **no** issue-key segment but the run has a key, the commands that are keyed (`/document` keyed mode, `/implement` with a resolved key) prepend it to the slug — `<KEY>-<slug>` — matching their pre-existing behaviour. In the §1.4 no-convention case the same applies.

If the assembled name already exists, append the first 7 chars of HEAD's SHA: `<name>-<short-sha>`.

---

## 4. Identity-resolution snippet

```bash
# Resolve the identity / prefix per §2
identity="${GIT_USER_INITIALS:-}"
if [ -z "$identity" ]; then
  identity="$(git -C "<repo>" config --get user.initials 2>/dev/null || true)"
fi
if [ -z "$identity" ]; then
  identity="$( { git -C "<repo>" for-each-ref --format='%(refname:lstrip=2)' refs/heads
                 git -C "<repo>" for-each-ref --format='%(refname:lstrip=3)' refs/remotes; } 2>/dev/null \
    | grep -vx 'HEAD' | sort -u | head -200 \
    | awk -F/ -v skip='^(feat|feature|fix|bugfix|hotfix|docs|chore|release|story|idea|prd|ard|spec|design|ready|brd|frames|kb)$' '
        { total++ }
        NF>=2 && length($1)>=2 && length($1)<=8 && $1 ~ /^[a-z0-9][a-z0-9-]*$/ && $1 !~ skip { n[$1]++ }
        END { for (c in n) if (n[c] >= 3 && n[c] * 10 >= total * 3) print n[c], c }' \
    | sort -k1,1nr -k2,2 | head -1 | awk '{print $2}')"
fi
# Empty here → §2.4 fallback (prefix case only) AND the §2.5 escalation before branching.
```

`skip` drops the generic prefixes, per §2.3's identity rule, and the plugin's nine, which are never a candidate. When resolving a §1.4 prefix rather than an identity, take the generic names out of `skip` and keep the nine. The `END` block is §2.3's threshold — at least 3 occurrences and at least 30 % of the sample — and the `sort` is §2.3's tie-break for an identity, the most frequent first and then alphabetical; a §1.4 prefix also takes §2.3's preference for a short non-generic candidate, which this snippet does not apply. A snippet that printed the most frequent name with no threshold adopted a name seen once.

---

## 5. Hard rules

- ALWAYS run §1.1 before anything else. NEVER hard-code `docs/`, `feat/`, `fix/`, `chore/` or any other prefix as the only option.
- NEVER add an identity segment to a documented pattern that has none, and never drop one the pattern requires.
- NEVER append a trailing `/` to a `$GIT_USER_INITIALS` or `user.initials` value; the caller inserts separators.
- NEVER uppercase an identity, and never use characters outside `[a-z0-9-]`; the first character must be a letter or digit (matching §2.3's inference pattern). Issue keys keep the documented capitalisation — usually upper-case.
- NEVER silently persist initials supplied through the §2.5 escalation — suggest the env var or git config instead.
- ALWAYS confirm the assembled name with the user (§1.3), even when it came from a documented convention.
