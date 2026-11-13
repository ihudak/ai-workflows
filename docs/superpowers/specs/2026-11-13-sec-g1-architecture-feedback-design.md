# SEC-G1 — the architecture feedback loop (security sub-project E)

**Date:** 2026-11-13. **Status:** revision 2.1, for the maintainer's approval. It applies a Fable design review's findings and the controller's rulings on the draft's five open questions (revision 2), then the four minors from Fable's re-check. Nothing here is implemented. **Roadmap:** row E of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md:101`, read with its non-goal at `:151`, D2 at `:208`–`:210`, the accepted-risk claim at `:395` and the free-text rule at `:475`. **Branch:** `feat/sec-g1-arch-feedback`.

**my call** marks a choice the roadmap leaves open and no ruling settled. **ruled** marks one the controller settled; §12 gives each ruling's reason.

## 1. The decisions

| # | Decision | |
|---|---|---|
| E1 | **One reader, in `workflows-core`.** A standard-library script, `scripts/weakness-classes.py`, reads `register.json` and the team records by format. It prints structured fields and finished follow-up lines only. A new skill, `workflows-core:weakness-classes`, which users cannot invoke, is the only way any caller runs it, and every caller is a command. `register.py` does not change | ruled (Q5) |
| E2 | **A weakness class is a register plus the finding's primary CWE**, validated as `^CWE-\d{1,6}\Z`. `other_cwes` is not used, and CWEs are not rolled up into parent classes | my call |
| E3 | **The repositories a piece of work touches** are the repo-slugs of the `components` each consumer already passes to `architecture-grounder` | my call |
| E4 | **Part 1.** At dispatch, the command calls the skill with its component slugs. When the result holds at least one class, the command hands the JSON to the grounder, which returns at most three `known-weakness` challenges, ranked after `contradicts-*`. When it holds none, everything happens as it does today | ruled (review item 2) |
| E5 | **What counts for Part 1.** Live findings count: `open`, `fix`, `fixing`, `reopened` and `accepted-risk`. A `fixed` finding closed in the last 180 days adds context only. A false positive never counts | my call |
| E6 | **Part 2: a class "recurs"** when its register holds two or more findings at `accepted-risk` that were accepted in distinct runs. A Dev's unconfirmed acceptance counts, and so does a risk past its review date | ruled (Q1, Q4) |
| E7 | **"Prevented."** For Parts 1 and 2, a class is prevented when a live team record meets two conditions: its frontmatter `components` holds the register's slug, and its `**Prevents:**` names the CWE. Part 3 counts any live record that names the CWE | ruled (item 1) |
| E8 | **Part 2's emitter is the scan.** The script prints the line, and the line lands in the PRD folder's `follow-ups.md`. `/create-ard`'s grill also offers the `[AD#N]` directly. No decision is written without the PA | ruled (Q3) |
| E9 | **E writes every CWE as a link to its CWE page**: in an ARD's Prevents, in a specification question and in a design line | my call |
| E10 | **Part 3: a "team" is a register.** A class recurs when two or more registers hold a judged-real finding of it. User-facing wording says "registers" and never "teams" | ruled (Q2) |
| E11 | **No E consumer is given, or told to read, a register.** Commands and agents see only the script's JSON | ruled (item 6) |
| E12 | **Plugins.** `workflows-core`, `product-workflows`, `dev-workflows` and `security-workflows` each take a minor bump. Nothing new depends on `security-workflows` | — |

## 2. What exists today

- **The register.** Each code repository has one register at `$SPECS_PATH/security/<repo-slug>/`, made of `runs/`, `scans/` and the derived `register.json` and `register.md` (`security-register-format.md:16`–`24`).
  - A finding carries `cwe`, `severity`, `path`, `line`, `status`, `units`, `owner`, `review_by` and `confirmed`, plus `history` entries of the form `{status, at, …, run}` (`:87`–`:96`).
  - The `cwe` value is the scan's own `cwe_id` (`register.py:444`). It is validated only when a follow-up line is built (`:151`, `:473`).
  - The derived files exist "for people and for the readers §6 names" (`security-register-format.md:33`), and §6 names those readers by a grep recipe (`:158`).
- **`register.py`** is the register's only writer.
  - Its six verbs are `plan`, `ids`, `commit`, `rebase`, `rebuild` and `verify-scope` (`register.py:4722`). None of them is a read-only query, since `rebuild` writes (`:1501`–`1505`).
  - Another plugin cannot reach it (CLAUDE.md, *Internal reference convention*).
  - "Active" means `open`, `fix`, `fixing`, `reopened` or `accepted-risk` (`:143`).
  - Every status change is a decision in a run record, automatic closures included (`:1282`–`1285`, `:1317`). `_apply` is the only code that writes a status (`:715`). It appends a `history` entry carrying the record's `at` and `seq` (`:725`–`726`). So every `fixed` finding has a dated entry, which the 180-day window relies on.
- **Free text.** `register.md` prints a finding's title under `## Scan output`, labelled as data (`register.py:1488`–`1489`). A follow-up line is built only from a closed list of structured fields (`security-register-format.md:98`–`103`).
- **Accepted risk.** An accepted risk has an owner and a review-by date, 90 days by default. E learns from accepted risks, and false positives teach it nothing (roadmap `:395`). A Dev's decision takes effect at once, with `confirmed: false` (`security-register-format.md:126`).
- **`architecture-grounder`** reads an organisation root and a team root (`architecture-grounder.md:11`–`13`). It skips `own_sources` and promoted records (`:42`), caps challenges at eight, of six kinds (`:49`, `:72`), and may use Bash only to list files and for read-only `git` (`:85`).
  - It is dispatched only when `arch_grounding` or `team_grounding` is ON (`architecture-grounding.md:45`), and `--no-arch` turns both roots off (`:9`, `:39`).
  - Its challenges are ranked into the grill's gap list and never appended (`:70`). It is advisory only (`:83`).
- **The grounder's consumers.** `/create-ard` passes the confirmed `components` (`create-ard.md:620`). `/specify` and `/design` pass the ARD's components, or else the slugs they scanned (`specify.md:906`, `design.md:304`). `/update-spec` makes `/specify`'s dispatch (`update-spec.md:94`).
- **The team knowledge base.** `decisions/<id>.md` carries frontmatter `status`, `source`, `components` (an inline list) and `tags`, and the promotion keys once marked. Its `**Prevents:**` is verbatim from the ARD (`architecture-kb.md:26`–`35`, `:60`, `:81`). `architecture-harvest.py` implements the format (`:3`).
- **Decisions and promotion.**
  - An `[AD#N]` has Binds, Prevents, Rule and Alternatives (`ard-format.md:68`); wording that leaves a Rule's meaning unchanged is not a change (`:107`); breaking a decision without a deviation record is a reviewer BLOCKER (`ard-resolution.md:109`–`117`).
  - `/promote-decisions` stops with "Nothing to promote" when no record is a candidate and no artifact has friction (`architecture-promotion.md:98`). Groups are PRDs (`promotion-scout.md:30`). Other teams are other specs repositories (`architecture-promotion.md:56`).
- **Follow-ups.** The scan's run key set includes the parent PRD's key (`scan.md:93`). A caller can name a folder per item (`followup-emission.md` §2, §8, the `/conformance` precedent). The scan persists follow-ups only "where 7.2 built any", and returns a cancelled line's finding to `fix` (`scan.md:566`).
  - `register.py` takes any task line naming ``repository `<slug>` `` and carrying `[SEC#n]` as that finding's own line (`register.py:882`–`885`).
  - `/implement` reads back only lines with a `/dev-workflows:implement <unit_key>` span and that same repository form (`implement.md:266`).
- **Pre-lint.** Pre-lint's autolink grep runs over PRDs, ARDs and Epics (`pre-lint.md:44`). It discards a hit inside a markdown link (`:56`), and reports `CWE-89` as a MINOR (`:63`).

## 3. The data path

### 3.1 The reader and its skill (E1)

**Decision.** Add `plugins/workflows-core/scripts/weakness-classes.py`. It uses only the standard library and has a `--selftest`. It has two verbs, prints one JSON object, and exits 0 whenever it could run; exit 2 means a usage error.

- `classes --specs <root> --repo <slug>… [--component <id>…] [--origin <origin>…] [--prd-key <KEY>] [--today <date>]` reads the named registers and the working tree's team records. It serves Part 1, Part 2 and the review-due annotation.
- `across --specs <root> --ref <ref> [--today <date>]` reads every register and every team record at `<ref>` with `git ls-tree` and `git show`, as every promotion input is read (`architecture-kb.md:85`). It serves Part 3.

**The skill.** `plugins/workflows-core/skills/weakness-classes/SKILL.md` (`user-invocable: false`, `allowed-tools: Bash`) runs the script. It writes the JSON to a `mktemp` file, under the rule in `workflows-core:run-flags` §7, and prints that file's path. This follows `specs-git` (`skills/specs-git/SKILL.md:1`–`14`).

**Who calls it.** Five commands call the skill: the scan, `/create-ard`, `/specify`, `/design` and `/promote-decisions`. Each passes the file's path to its agent, if it has one, as `/promote-decisions` already does with `signals` (`architecture-promotion.md:96`–`116`). No agent runs the script.

**Why.** `register.py` cannot be reached from another plugin and has no read verb; the rule has three consumers but must have one implementation; and the copied-scripts rule (`.claude/rules/workflows-core-bounded-run.md:17`) suits small utilities, not a domain rule.

**Two formats, so two authorities.** The script reads two formats:
- **The register.** The rule goes into a new §7 of `workflows-core:security-register-format`, *Weakness classes*. §6 then names the reference's loaders and the skill's callers.
- **The knowledge base.** This makes the script `architecture-kb`'s second implementer, beside `architecture-harvest.py`. `architecture-kb.md:3` names both, so a change to the format changes both scripts in one commit. `.claude/rules/docs-grounding.md:60` gains that note.

### 3.2 Output

`classes` lists only classes with at least one live finding:

```json
{ "format": 1, "today": "2026-11-13", "kb_skipped": 0,
  "registers": [ { "repo": "api", "state": "ok", "last_at": "2026-11-02T09:14:00Z",
                   "findings": 14, "dropped": 0, "unclassified": 1 } ],
  "classes": [ { "repo": "api", "cwe": "CWE-89", "cwe_url": "https://cwe.mitre.org/data/definitions/89.html",
                 "live": 3, "accepted": 2, "accepting_runs": 2, "awaiting_review": 1, "review_due": 0,
                 "fixed_recent": 1, "top_severity": "HIGH", "in_component": true, "recurs": true,
                 "decided": true,
                 "prevented_by": [ { "id": "ACME-17-AD3", "source": "specifications/PRD-ACME-17-x/ard.md",
                                     "promotion": null, "promoted_to": null } ],
                 "findings": [ { "id": 3, "status": "accepted-risk", "severity": "HIGH",
                                 "path": "src/orders/Repo.java", "line": 88,
                                 "review_by": "2027-01-10", "confirmed": false } ],
                 "pa_line": null, "pa_next_step": null } ] }
```

- **`findings`** is the evidence. It holds at most five entries: live findings first, by severity, then by id.
- **`decided`** appears only with `--origin`. It is true on each class holding a finding whose `origin` was passed.
- **`pa_line`** is set only when the class is `decided`, `recurs` and has an empty `prevented_by`. With `--prd-key` it holds the finished task line of §5.3, and `pa_next_step` stays null. Without `--prd-key`, `pa_line` stays null and `pa_next_step` holds the finished report sentence.

`across` has the same envelope, plus `ref`. Its classes are the ones held in two or more registers:

```json
{ "cwe": "CWE-89", "cwe_url": "…", "real": 5, "accepted": 4, "fixed_recent": 1,
  "registers": [ { "repo": "api", "real": 3, "accepted": 2, "fixed_recent": 1, "last_at": "2026-11-02T09:14:00Z" } ],
  "prevented_by": [ { "id": "ACME-17-AD3", "promotion": "proposed", "promoted_to": "ADR-0031" } ] }
```

**Fields shared by both verbs.**

| Field | What it holds |
|---|---|
| `state` | `ok`, `absent`, `unreadable`, `unknown-format` (a `format` other than `1`) or `malformed` (the top-level shape is wrong) |
| `dropped` | Findings that failed a field check (§8) |
| `unclassified` | Counted findings whose CWE failed its check |
| `kb_skipped` | Team records whose frontmatter could not be read |
| `last_at` | `register.json`'s own `last_at`, the last run, which shows when a register has gone quiet |

### 3.3 What it reads, and when a register is missing or bad

- **The register.** The script reads only `security/<slug>/register.json`. It never reads `register.md`, `runs/` or `scans/`, because replaying run records is `register.py`'s job.
  - `<slug>` must match `register.py`'s slug pattern, and must not be `.` or `..`.
  - For `classes`, each slug is the part of a `components` id before its first `:`, which is exact (`components.md:11`–`14`). It is then resolved against the directories under `security/` that hold a `register.json`.
  - Any `state` other than `ok` is shown in a report line and never stops a run. `absent` is silent.
- **Team records** are read with the standard library only, from the frontmatter of `architecture/decisions/<id>.md` and not from `index.yaml`:
  - Read line by line between the first two `---` lines.
  - Take `status`, `source`, `promotion` and `promoted_to` as scalars, stripping one pair of quotes.
  - Take `components` as a flow list, parsed with `json.loads`, in the shape the harvest writes (`architecture-kb.md:34`).
  - Take the body paragraph that opens `**Prevents:**`, up to the next blank line.
  - A record that fails any of these is skipped and counted in `kb_skipped`.
- **Staleness.** `register.json` is derived, and may lag records still on unmerged `session/*` branches (`security-register-format.md:33`, `:61`). The output is advice, so a lag of one rebuild is acceptable.

### 3.4 The class and the rule (E2, E5, E6, E7)

| Use | What counts |
|---|---|
| Part 1, live | `open`, `fix`, `fixing`, `reopened`, `accepted-risk` (`register.py:143`), and a transient `new` |
| Part 1, context | `fixed`, where the `at` of its last `history` entry falls within 180 days of `--today` |
| Part 2, recurs | `accepted-risk`, in at least 2 findings with distinct **accepting runs** |
| Part 3, judged real | `fix`, `fixing`, `reopened`, `accepted-risk`, and `fixed` within 180 days |
| Never | `false-positive` (roadmap `:395`). Part 3 also excludes undecided `open` |

- **The accepting run.** A finding's accepting run is the `(run, at)` of the earliest entry in the unbroken run of `accepted-risk` entries that ends its `history`.
  - Pairing `run` with `at` matters because two runs can share a `seq` (`security-register-format.md:43`).
  - Taking the earliest entry means a security engineer's confirmation, made later in one batch, does not merge two acceptances made in separate runs into one.
- **Prevented.**
  - A record prevents a class when its `status` is `accepted` and its Prevents paragraph holds the CWE as a whole token, so that `CWE-89` does not match `CWE-890`.
  - For `classes`, the record's `components` must also hold an id whose slug is the register's (item 1).
  - The test matches a token the script already holds. It never extracts one (`.claude/rules/workflows-core.md:36`).
  - A promoted record still prevents the class, because its organisation artifact covers it.
- **Ranking**, in order:
  1. recurring and not prevented;
  2. on a run that passes `--component <slug>:<path>`, a finding under that path (`in_component`);
  3. the highest live severity;
  4. the live count;
  5. the slug;
  6. the CWE number.

## 4. Part 1 — the `known-weakness` challenge

### 4.1 The configure-time line

`resolve-architecture-grounding` gains a step 5a, inside the one resolution the run already makes (`architecture-grounding.md:85`). Where `$SPECS_PATH/security/` exists, it prints a line next to the team line:

```
security registers: ON <specs>/security (<n> registers; read for the repositories the work touches)
security registers: OFF (disabled with --no-arch)
security registers: OFF (no findings register under <specs>/security — it holds only cost or feedback entries, or other files)
security registers: OFF (<specs>/security is not readable)
```

**No line at all when `security/` does not exist (my call).** Registers come from an optional plugin, so a tree that has never run a scan prints exactly what it prints today. The team line, by contrast, always prints (`:39`).

### 4.2 Dispatch (E4)

- **When the command calls the skill.** Only when the line said ON, and at the point where it builds `stack_facts`:

  ```
  Skill(workflows-core:weakness-classes, "classes --repo <slug>… --component <id>…")
  ```

  - `/create-ard` calls it at `create-ard.md:620`, `/specify` at `specify.md:906` and `/design` at `design.md:304`.
  - `/update-spec` follows `/specify` (`update-spec.md:94`).
- **What triggers a dispatch.** A result with at least one class is a trigger in its own right. The dispatch condition at `architecture-grounding.md:45` and in those three steps becomes: `arch_grounding: ON`, or `team_grounding: ON`, or a non-empty `classes`.
- **What the grounder receives.** A new input, `weakness_classes: <absolute path of the JSON> | null`, set only when classes exist.
- **What changes in the agent.**
  - "At least one root is set" (`architecture-grounder.md:13`, `:20`) widens to "at least one of the two roots, or `weakness_classes`".
  - A new method step 5a reads that file and raises one `known-weakness` per class, taking the script's order.
  - Hard rule `:85` does not change. A new hard rule says never to open a file under `<specs>/security/`.
- **When the skill fails.** The command keeps grounding exactly as it would have run without the call, and writes one line in the final report: `security registers: not read — <the skill's error>`.

### 4.3 Shape

```yaml
arch_challenges:
  - kind: known-weakness
    subject: CWE-89 in api
    evidence: "security/api/register.md — [SEC#3] accepted-risk HIGH src/orders/Repo.java:88; [SEC#7] fixing MEDIUM src/search/Query.java:41"
    governing: { id: ACME-17-AD3, title: …, root: team, path: architecture/decisions/ACME-17-AD3.md, url: null, rule: "<quoted>", prd: ACME-17, source: … }   # null where nothing prevents the class
    weakness: { repo: api, cwe: CWE-89, cwe_url: "https://cwe.mitre.org/data/definitions/89.html", live: 2, accepted: 1, awaiting_review: 1, review_due: 0, fixed_recent: 1, recurs: false, register: security/api/register.md }
```

**`governing` follows the standing rules, with two exceptions, each stated where its rule is:**
- **Own source.** Where the record's `source:` is in `own_sources`, `governing` gives the record's `id` and `source` only. The caller holds that decision's live text. This is an exception to `architecture-grounder.md:42`.
- **Promoted.** Where the record's `promotion` is `accepted` or `covered`, `governing` names its `promoted_to` artifact instead of quoting the record. It is `{ id: <promoted_to>, title: null, root: organisation, path: null, url: null, rule: null }`, with `prd` and `source` omitted as for any organisation artifact, so the shape stays fixed. This is an exception to `architecture-grounder.md:42` and to "A promoted team record is not read" (`architecture-grounding.md:71`). Only the promotion keys are taken.

### 4.4 Rank and cap

At most **three** `known-weakness` challenges, inside the existing cap of eight. The order becomes `contradicts-*`, then `known-weakness`, then the radar kinds (my call). A triaged weakness in code the work touches is measured evidence, while a radar ring is policy.

### 4.5 How each command presents it

**What every command shares.** The challenge competes for a question slot (`architecture-grounding.md:70`). The command never opens a register: it builds the question from the JSON fields only, meaning `[SEC#n]`, the CWE link and the register link. The question asks how the work avoids adding to the class.

- **`/create-ard` (the PA).**
  - Where `recurs` is true and `governing` is null, the question offers `choices: ["Record an [AD#N] that prevents CWE-89 (Recommended)", "Not in this ARD"]`.
  - A yes is grilled like any other decision, and `ard-reviewer` gates it.
  - The grill also checks the Prevents lines of the ARD's own unharvested decisions (`:72`).
- **`/specify`, and `/update-spec` for the items it revises.** A challenge the grill cannot settle becomes a `- [ ]` open question that:
  - names `[CWE-89](https://cwe.mitre.org/data/definitions/89.html)` and links the register;
  - says what settles it: a Security / privacy acceptance criterion, or, where the class recurs unprevented, an ARD decision whose Prevents names the CWE, made with `/product-workflows:create-ard <PRD-KEY>`.

  The CWE must be a link here too, because `/epics` copies specification text into Epics, which pre-lint reads.
- **`/design` (the Dev).** `design-format` § Architecture governance gains a line under `## Risks & mitigations` (`design-format.md:176`) (my call). It is advisory, and `design-reviewer` never gates on it:

  ```
  - Known weakness: [CWE-89](https://cwe.mitre.org/data/definitions/89.html) in api ([register](<link>)) — <how this design avoids adding to it, or why it accepts it>
  ```

- **The final report** adds `registers read: api; skipped: billing (malformed)` to its `architecture grounding:` line.

### 4.6 When there is no register

- **No `security/` directory.** Nothing prints and nothing is called.
- **Registers exist but the work touches no class.** The dispatch and the digest are exactly today's. The one addition is the configure-time line.
- **No run waits on a register.** No register state stops a run, asks a question or makes a command unavailable.

## 5. Part 2 — recurring accepted risks become a decision

### 5.1 Recurs (E6)

A class recurs when its register holds at least two findings at `accepted-risk` with distinct accepting runs (§3.4).

- **One run is one judgement.** One triage that accepts two SQL injections in a single batch is one decision, not a pattern.
- **There is no separate window.** A risk that is fixed, or ruled a false positive, at its review-by date stops counting at once.
- **Some risks still count.** A review-due risk stays accepted until someone decides again. A Dev's unconfirmed risk is in effect now (`security-register-format.md:126`). The line says how many still await security review.

### 5.2 Prevented (E7)

- **What the test sees.** Only harvested records. Between the PA recording a decision and the next `/harvest-decisions`, the class still reads as unprevented. A further accepted risk in that gap can raise a second line, which dedupe catches while the first stays open.
- **An existing decision that covers the class in words.** Where one of the ARD's decisions already prevents the class in words, without naming the CWE, the PA can answer by adding the CWE link to that decision's Prevents. The new `ard-format` sentence (§5.5) says outright that adding a CWE link to a decision's Prevents is not a change to the decision. A decision that would also need its Rule to require more is a new `[AD#M]`.

### 5.3 Who raises it (E8)

**The scan raises it.** An accepted risk is decided only in the scan's triage.

**When the scan calls the skill.** Only on a run that recorded at least one `accepted-risk` decision, after 7.2's commit. The call passes each such finding's `origin` and, on a key run, the run key set's PRD key (`scan.md:93`):

```
classes --repo <repo-slug> --origin <origin>… [--prd-key <PRD-KEY>]
```

- **A key run with no PRD key.** Where the unit is under no `PRD-` folder, the run key set holds no PRD key, so the scan omits `--prd-key`. The sentence then goes to the report, as on a path run.
- **Where an origin comes from.** For an existing finding, the answered plan's `origins` holds it (`register.py:939`). For a new finding, it is `<scan id>:<plugin id>` (`security-register-format.md:85`).
- **Why origins and not numbers.** A number can move between the plan a person answered and the rebuilt register (§2 there). An origin never changes.
- **What it misses.** A new finding whose allocation gave way has another origin, so it is missed. The next accepted risk of that class raises the line instead.
- **Not a state read.** The read decides no register change, so it does not read the register's state (§10, item 3).

The script prints the finished line, so the line is deterministic and covered by the selftest:

```
- [ ] Run `/product-workflows:create-ard ACME-17` to record an [AD#N] whose Prevents names [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — 2 accepted risks of CWE-89 in the api register (security/api/register.md), accepted in 2 runs, 1 awaiting security review, and no team decision for api prevents it — raised by /security-workflows:scan
```

- **No `[SEC#n]` and no ``repository `<name>` ``.** The line carries neither, so `register.py` does not take it for a finding's line (`:882`–`885`), and `/implement` does not read it back (`implement.md:266`).
- **It lands in the PRD folder's `follow-ups.md`.** The scan passes that item with its own `unit_folder` and `key`, the PRD's, as `/conformance` does (`followup-emission.md` §2, §8). The decision belongs in the PRD-level ARD.
- **The key run is the main source.** In practice the written line comes from a Dev's key run. A path run has no folder, so its `pa_next_step` sentence goes in the report's `### Next step` only (`followup-emission.md:44`). There, `/create-ard`'s grill (§4.5) and Part 3 are the backstop.

### 5.4 Phase 7.6 mechanics in the scan

- **The persist step runs when the PA line is the only follow-up.** Today it runs only "where 7.2 built any" (`scan.md:566`).
- **The line is written exactly as the script printed it**, beside the lines `commit` printed.
- **Cancelling the PA line records nothing.** Cancelling a finding's line writes a second run record that returns the finding to `fix`. The PA line has no finding, so no decision is cancelled. The class is raised again by its next accepted risk.
- **Dedupe matches open lines only.** The identity is the PRD key, the CWE and the register path. A ticked line does not suppress the next one, so a later accepted risk raises the class again.
- **`followup-emission` declares the identity.** §6 gains the predicate: a decision another role must record, here the scan's line for the PA. §5 gains the identity and its open-only match, beside *A security finding's line* (`:86`).

### 5.5 The decision's form (E9)

`**Prevents:**` names the CWE as a link built from the validated digits, for example `[CWE-89](https://cwe.mitre.org/data/definitions/89.html)`. Pre-lint discards a hit inside a link (`pre-lint.md:56`), and the coverage test finds the token in the link text. `ard-format` § Architecture governance gains one sentence saying so, and saying that adding such a link to an existing decision's Prevents is not a change to the decision (§5.2). The pre-lint grep itself is not touched (CLAUDE.md, *One key namespace*).

### 5.6 Downstream

From here on, nothing new is involved:

1. The ARD merges through `handoff-to-main`.
2. `/harvest-decisions` records the decision (`architecture-kb.md:60`).
3. The class's `prevented_by` now names that record, so Part 2 goes quiet and Part 1 shows the record as `governing`.
4. `/promote-decisions` offers the record (§6).
5. `ard-resolution` makes breaking it a reviewer BLOCKER (`ard-resolution.md:117`).

### 5.7 Review-by interaction

1. **A new decision changes no accepted risk.** No status, owner or date moves when a decision lands. `ard-resolution` binds the artifacts that consume the ARD, not code someone has already accepted.
2. **The review date is when a decision reaches existing code (my call).**
   - On a scan run whose triage holds at least one review-due row, Phase 5 calls `classes --origin <each review-due finding's origin>`, after its rebuild (`scan.md:300`). No other run makes that call.
   - Each such row then names the live team record that prevents its class, so re-accepting the risk means choosing against that record in the open.
   - Phase 5 reads only `prevented_by` from that call, and ignores `pa_line` and `pa_next_step`. Passing `--origin` sets `decided`, so a recurring unprevented class would otherwise raise the PA line on a run that accepted nothing.
   - The suggestion is unchanged: the row still offers the finding's current status.

## 6. Part 3 — recurrence across registers

### 6.1 What a team is (E10)

A team is a register: one code repository.
- **Why not the specs repository.** One `/promote-decisions` run sees one specs repository, and other teams are other specs repositories (`architecture-promotion.md:56`).
- **Why not a PRD group.** A PRD group (`promotion-scout.md:30`) loses every finding raised by a path run, because those carry no `units` (`register.py:521`).
- **Coverage is still checked organisation-wide.** The scout reads the shared architecture repository.
- **Wording.** User-facing text says "recurs in N registers".

### 6.2 Signal and threshold

A class recurs across registers when **two or more registers** each hold at least one judged-real finding of it (§3.4).

### 6.3 Where it surfaces

1. **§5 signals.** `/promote-decisions` calls the skill with `across --ref <default-ref>`, and keeps the JSON beside the signals file. "Nothing to promote" now also requires no classes (`architecture-promotion.md:98`).
2. **§6 comparison.** `promotion-scout` gains the input `weakness_classes`, the path of that file.
   - For each class it returns `relation: covered | uncovered`, together with the `accepted` ADR or `active` standard that names the CWE or states a rule implying it. It reads every artifact it cites.
   - `EMPTY` and `ERROR` (`promotion-scout.md:58`) take the classes and their file into account.
   - The command builds rows from the JSON fields only. It never opens a register.
3. **§7 shortlist.**
   - **A candidate row whose record is in `prevented_by`** gains the reason `prevents CWE-89, which recurs in 3 registers (api, billing, web)`, and ranks on it right after cluster size (`:123`) (my call).
   - **An uncovered class that no record prevents** is listed, unnumbered, under *Reported only* (`:132`), with each register's last run date:

     ```
     CWE-89 — recurs in 3 registers: api (last run 2026-11-02), billing (2026-06-30), web (2026-10-19); 4 accepted risks, 2 fixed — no team decision prevents it, and no ADR or standard covers it — record one with /product-workflows:create-ard
     ```

   - **Covered classes** get one count line.
4. **With classes but no candidate.** The scout is still dispatched, and the classes are listed. No row is numbered and nothing is drafted, so the run goes to §11.2 with §4's marks, or stops where there are none. A decision always starts in an ARD (§5).

## 7. Plugin boundaries

| Plugin | Changes |
|---|---|
| `workflows-core` | New: `scripts/weakness-classes.py` and `skills/weakness-classes/`. `security-register-format`: §1, §6 and a new §7. `architecture-grounding`: step 5a, the line, the dispatch condition, §Consumption and its exception at `:71`. `architecture-grounder`: the input, step 5a, `known-weakness`, the exception at `:42` and the new hard rule. `architecture-promotion` §5–§7. `promotion-scout`. `followup-emission` §5 and §6. `architecture-kb`: its second implementer |
| `product-workflows` | `create-ard.md`, `specify.md` (which `update-spec` follows), `promote-decisions.md`, and the Prevents-link sentence in `ard-format.md` |
| `dev-workflows` | `design.md`'s skill call and dispatch condition; the *Known weakness* line in `design-format.md` |
| `security-workflows` | `scan.md` Phase 5 (the gated annotation) and Phases 7.2 and 7.6 (the PA line). `register.py` does not change |
| `docs-workflows` | None |

**No plugin comes to depend on `security-workflows`.**
- The register is data in SPECS, so reading it needs no dependency (roadmap `:210`).
- The register's format and its only reader live in `workflows-core`, which every family plugin already declares.
- `grep -l security-workflows plugins/*/.claude-plugin/plugin.json` still lists only its own manifest (`.claude/rules/security-workflows.md:16`).
- Without `security-workflows` there are no registers, so every path above takes the absent case.

## 8. Safety — register text is data

1. **The validators are at least as strict as `register.py`'s.** Every pattern is anchored with `\Z` and `re.ASCII` (`register.py:147`–`151`):

   | Field | Check |
   |---|---|
   | `cwe` | `^CWE-\d{1,6}\Z`, because the digits build a URL |
   | `path` | `register.py`'s safe-path pattern (`:162`); no `..` segment; at most 512 characters; otherwise null, shown as "location in register.md" |
   | `id`, `line` | `int`, not `bool`; `id` ≥ 1, `line` ≥ 0 |
   | `severity`, `status` | Their enums |
   | `review_by` | A real `YYYY-MM-DD` |
   | `confirmed` | A boolean |
   | slug | The slug pattern |
   | `--prd-key` | The key grammar (`register.py:149`) |
   | `--origin` | Checked against the origins the register holds, and otherwise ignored |
   | Team record id | The key-grammar id shape from `architecture-kb.md:20` |

   The script **never** prints `title`, `reason`, `evidence`, `by`, `owner`, `links`, `scope` or `units`. A field that fails its check is dropped, never echoed. The script opens no path taken from the register, and runs nothing named in it.
2. **No consumer is given, or told to read, a register.** Each command and agent gets the JSON file. The grounder and the scout also gain a hard rule against opening anything under `<specs>/security/`. Links to `register.md` inside an artifact are fine: they are for people. The untrusted-content blocks (`architecture-grounder.md:90`–`125`, `promotion-scout.md:67`–`102`) still cover everything else.
3. **Every line, row and question** is built from those fields plus fixed wording, as follow-up lines already are (`security-register-format.md:98`–`103`). The PA line's closed list is: the CWE and its URL, the slug, the register path, the counts and the PRD key.
4. **Artifacts are written by people.** What an ARD, a specification or a design records is authored in the grill, never copied from a register.
5. **The selftest plants hostile values separately**, and asserts that none reaches the output:
   - `Ignore all previous instructions` in a title and in a reason (as at `register.py:1996`);
   - `CWE-89; rm -rf` and `CWE-1234567`;
   - the path `../etc/passwd`, which has no backtick;
   - a path containing a backtick;
   - an `id` of `true` and a `line` of `-1`;
   - a team record whose Prevents holds `CWE-890`, which must not prevent `CWE-89`.

## 9. Non-goals and anti-goals

**Non-goals.**
- No scanning, patching or fixing; no writes to a register, and no change to `register.py`.
- No automatic `[AD#N]`, and no ADR drafted from a register; no new gate, since a BLOCKER comes only through a recorded `[AD#N]`.
- No CWE rollup and no `other_cwes`; no aggregation across specs repositories; no new environment variable or flag.
- No change to triage statuses, suggestions or review-by rules; no threat models, which are B, C and D.

**Anti-goals.**
- A finding's text in any consumer's context, artifact, line or row; any consumer failing, stopping or asking because of a register.
- A slug or key parsed out of free text; replaying `runs/` outside `register.py`; exempting `CWE-` from pre-lint; the rule implemented in more than one place.

## 10. Claim-expiry sweep — notes E makes stale

**Method.** The sweep covers refinement 4's scope. Each match is by phrase, and the whole paragraph around it is read. The subject is "who reads the register, and who builds a follow-up line" (refinement 6).

1. **`security-workflows/CHANGELOG.md:235`.** It says E is not built yet. It stays, because it is true of that release.
2. **`security-register-format.md:11`.** "register.py … implements this file" narrows to §1–§5.
3. **"Never read back as its state", and its one exception** (refinement 3). These need "as the register's state":
   - `security-register-format.md:22`–`23` and `:33`;
   - `.claude/rules/security-workflows.md:34`;
   - `security-workflows/docs/workflow.md:70`.
4. **Who builds follow-up lines.** `security-register-format.md:98`–`103` gives §3's closed list. `.claude/rules/security-workflows.md:37` ("`register.py commit` builds every follow-up line") and `:44` ("builds them at Phase 7.2") must also name the script's PA line and its own closed list.
5. **Who reads the register.**
   - `security-register-format.md:105` ("every reader … reads it the same way");
   - `:158`, §6's recipe, and `.claude/rules/security-workflows.md:22`. Both become the reference's loaders plus the skill's callers, each found by a grep on its execution phrase.
6. **`architecture-grounding.md`:**
   - `:3`, `:39` and `:45`;
   - `:71`, which gains its exception;
   - `:81`, and `:82` ("every miss is OFF"), which gains the line for a failed skill call;
   - the Consumers line, and § Consumption, which gains "never opens a register".
7. **`architecture-grounder.md`:** `:3` and `:7` (the description and the purpose); `:13` and `:20` (the roots); `:42`, which gains its exceptions; and `:49`, `:72` and `:79`, since `EMPTY` can no longer occur when classes are present.
8. **The dispatch steps.** `create-ard.md:620`, `specify.md:906` and `design.md:304` change. `update-spec.md:94` must be re-read, not edited.
9. **`scan.md`.**
   - `:300` gains the gated call.
   - `:566` changes in three places: the persist condition, "written exactly as `commit` printed it", and cancel-to-`fix`, which must not apply to the PA line.
10. **`followup-emission.md`.** §5 and §6. The caller list at `:7`–`9` does not change.
11. **Promotion.** `promotion-scout.md:3`; `:58`, both its `EMPTY` and its `ERROR` half; and `architecture-promotion.md:98`.
12. **`architecture-kb.md:3`** ("The script implements it"), and **`.claude/rules/docs-grounding.md`**: `:58`, `:60`, `:64`, and `paths:`, which gains the skill and the script.
13. **The skill count.** `.claude/rules/workflows-core.md:18` and `plugins/workflows-core/docs/README.md:32` both say "three bundled skills".
14. **`CLAUDE.md`.** The Shared-authorities bullet for `security-register-format` ("the rules `register.py` applies"), and its `workflows-core` paragraph.
15. **The CI step.** A new `weakness-classes.py --selftest` step goes in `.github/workflows/validate-catalog.yml`, next to `register.py`'s at `:242`. **That file is GIT-G1's to edit**, so this is a coordination point for the pull request. No edit is planned without its owner.
16. **The roadmap** at `:151` and `:208` ("E's consumers …") is outside the sweep's scope. The scan joins those consumers, so D2 can take an amendment line.

## 11. Docs, versions, coupling

**Pages.**
- **`workflows-core`:** `docs/reference/grounding.md`, `agents.md`, `references.md#skills` (a new skill without its entry fails `check-docs.sh`), `README.md:32`, and `family-map.md`'s security lane.
- **`product-workflows`:** `docs/commands/create-ard.md`, `specify.md`, `update-spec.md` and `promote-decisions.md`.
- **`dev-workflows`:** `docs/commands/design.md`.
- **`security-workflows`:** `docs/commands/scan.md`, `workflow.md`, `reference/security-register.md` and `roles-and-phases.md`, which says the PA receives the line.

**Workflow-map lines.** `.claude/rules/product-workflows.md:42`, `:44` and `:45`, `security-workflows.md:27`, and the `/design` line in `dev-workflows.md`.

**Versions.** Each plugin takes its next minor at merge, from today's `workflows-core` 1.85.0, `product-workflows` 3.79.4, `dev-workflows` 4.63.0 and `security-workflows` 0.11.3, each with a dated `CHANGELOG.md` entry.

**Coupling.** One bullet naming all four plugins, covering both directions:
- **Older dependents with the newer core.** They never call the skill, so grounding is today's and no PA line is written.
- **Newer dependents with the older core.** The skill is missing, so each call fails and leaves one report line (§4.2), and no run breaks.

## 12. Review rulings, and checks made after review

**Rulings.** No question is left open.
- **Q1: the threshold is 2 for both Part 2 and Part 3**, with Part 2's two accepted risks coming from distinct runs. Each acceptance is a deliberate decision with an owner, and the distinct-runs rule keeps one batch from counting as a pattern.
- **Q2: a team is a register.** A PRD group loses every finding raised by a path run, and a specs repository is out of reach from one run.
- **Q3: the scan raises the follow-up.** The accepted risk is decided there, and the row says "a follow-up for the PA". The grill alone would wait until a PA happened to refine an ARD that touches the repository.
- **Q4: unconfirmed acceptances count.** They are in effect at once, an overrule removes them at the next read, and the line says how many await security review.
- **Q5: one script, reached through a skill.** That gives one implementation of a domain rule, and `specs-git` shows the route works.

**Checked after review.**
- **Automatic closures carry a dated `history` entry.** `_apply` is the only status write (`register.py:715`). Automatic closures are recorded decisions (`:1282`–`1285`, `:1317`). Each decision appends `at` and `run` (`:725`–`726`).
- **`/implement`'s read-back ignores the PA line.** It takes only lines whose span is `/dev-workflows:implement <unit_key>` and that carry ``repository `<name>` `` (`implement.md:266`). The PA line has neither.
