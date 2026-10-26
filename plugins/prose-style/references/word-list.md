# Word list

General-English usage: words to avoid, words that are routinely confused, compound
forms, and spelling. Not a glossary of product terms — those live in `terminology.md`.

**Baseline.** These are the shipped, vendor-neutral defaults, chosen because they hold
across organizations. A repo-local or env-var overlay layers on top of them and wins on
conflict — see `prose-style-checker` step 1 ("Resolve the active rule set") and the plugin's
`docs/reference/overlay.md`. The [Entry schema](#entry-schema) at the end of this file shows how to
add your own.

**Grounded in:** Microsoft Writing Style Guide (A–Z word list); Google developer
documentation style guide (word list); Merriam-Webster and The Chicago Manual of Style
for general-English forms; Conscious Style Guide and Google's inclusive-language
guidance for the excluded terms.

---

## Never use

Replace on sight. See `accessibility.md` for why each one is here.

| ❌ Never | ✅ Use instead |
|---|---|
| blacklist | blocklist, denylist, exclude list |
| whitelist | allowlist, safe list, approved list |
| master (technical) | primary, main, source, leader |
| slave | replica, secondary, worker, follower |
| grandfathered | legacy, exempt, pre-existing |
| native (of people) | name the specific group |
| crazy, insane | unexpected, surprising |
| sanity check | confidence check, validation |
| dummy (value) | placeholder, sample |
| cripple | impair, degrade, break |
| manpower | workforce, capacity |
| he/she, (s)he, his or her | they, them, their |

---

## Avoid — patronizing

These words tell the reader the task is easy. For any reader stuck on it, that is
wrong, and deleting the word never costs anything.

| ❌ Avoid | ✅ Use instead |
|---|---|
| simply | (delete) |
| just | (delete, when it means "merely") |
| easy, easily | (delete, or state the actual effort) |
| obviously, clearly, of course | (delete) |
| straightforward | (delete, or describe the steps) |
| merely | (delete) |
| all you have to do is | (delete; start with the verb) |
| as you know | (delete) |
| trivial | (delete, or give the actual cost) |

---

## Avoid — vague, inflated, or filler

| ❌ Avoid | ✅ Use instead |
|---|---|
| utilize, leverage (verb) | use |
| facilitate | help, make easier |
| in order to | to |
| at this point in time | now |
| due to the fact that | because |
| it should be noted that | (delete) |
| prior to / subsequent to | before / after |
| various, numerous, several | the actual number |
| robust, powerful, seamless, cutting-edge | name the capability |
| best-in-class, world-class, next-generation | (delete; marketing, not documentation) |
| please (in an instruction) | (delete) |
| and/or | "A, B, or both" |
| etc. | "and so on", or complete the list |
| e.g. | for example |
| i.e. | that is |
| via | through, by, using |
| out-of-the-box | built-in, included, default |
| deep dive | (delete, or "detailed look") |
| going forward | from now on, in future releases |

---

## Avoid — UI and interaction verbs

Full rules in `ui-interactions.md`.

| ❌ Avoid | ✅ Use instead |
|---|---|
| click, tap (as the default) | select |
| navigate to | go to |
| log in / log into | sign in / sign in to |
| enable / disable (a control) | turn on / turn off |
| toggle (verb) | turn on / turn off |
| type, paste, input (a value) | enter |
| check / uncheck (a checkbox) | select / clear |
| hit (a key or a button) | press / select |
| launch (an app) | open |

---

## Confusable words

### affect / effect
- *affect* = verb, to influence. "The retry policy affects latency."
- *effect* = noun, the result. "The change had no effect."

### after / once
- Use *after* for sequence. "After you install the agent…"
- *Once* means "one time"; do not use it for sequence.

### although / while
- Use *although* for contrast. "Although the API accepts both…"
- Reserve *while* for simultaneity in time.

### because / since / as
- Use *because* for causality. *Since* and *as* are ambiguous with time.

### can / may / might
- *can* = ability. "You can revoke the token."
- *might* = possibility. "The job might time out."
- *may* = permission. Avoid it for possibility.

### comprise / compose
- The whole *comprises* the parts. "The platform comprises three tiers."
- The parts *compose* the whole.
- ❌ "comprised of" is always wrong. Use "consists of" or "is composed of".

### ensure / insure / assure
- *ensure* = make certain. *insure* = financial. *assure* = reassure a person.

### fewer / less
- *fewer* for countable things: fewer hosts, fewer retries.
- *less* for uncountable quantities: less bandwidth, less time.

### that / which
- *that* introduces a restrictive clause, no comma.
- *which* introduces a non-restrictive clause, with a comma. See `grammar.md`.

### then / than
- *then* = time or sequence. *than* = comparison.

### its / it's
- *its* = possessive. *it's* = "it is".

### login / log in
- *login* and *sign-in* are nouns and adjectives.
- *log in* and *sign in* are verbs (and the preferred verb is *sign in*).

### setup / set up
- *setup* is the noun. *set up* is the verb.

### everyday / every day
- *everyday* is an adjective. *every day* is the time expression.

---

## Compound and hyphenation forms

| ✅ Correct | ❌ Incorrect |
|---|---|
| email | e-mail, E-mail |
| website | web site, Web site |
| webpage | web page |
| internet, web (lowercase) | Internet, Web |
| online | on-line |
| checkbox | check box |
| hostname | host name |
| username | user name |
| filename | file name |
| metadata | meta data, meta-data |
| dataset | data set |
| lifecycle | life cycle |
| timestamp | time stamp |
| autodiscovery | auto-discovery |
| microservice | micro-service |
| standalone | stand-alone |
| backward compatible | backwards compatible |
| use case | usecase, use-case (noun) |
| data center | datacenter |
| open source (noun) / open-source (adjective) | open-source phone book (noun use) |
| real time (noun) / real-time (adjective) | real-time as a noun |
| backend (noun) / back-end (adjective) | back end (noun) |
| frontend (noun) / front-end (adjective) | front end (noun) |
| runtime (noun) / run-time (adjective) | run time |
| command line (noun) / command-line (adjective) | commandline |
| on-premises (adjective) | on-premise, on premise |
| sign-in (noun) / sign in (verb) | signin |
| single sign-on (SSO) | single-sign-on |
| third party (noun) / third-party (adjective) | 3rd party |
| read-only | read only (before a noun) |
| machine learning (noun) / machine-learning (adjective) | Machine Learning in prose |
| DevOps | Dev Ops, devops |
| API, APIs | API's |

---

## Spelling variant

The baseline is **American English** (Microsoft and Google both default to it).

| ✅ US | ❌ Non-US variant |
|---|---|
| behavior | behaviour |
| color | colour |
| center | centre |
| catalog | catalogue |
| favorite | favourite |
| license (noun and verb) | licence |
| analyze | analyse |
| organize | organise |
| canceled, canceling | cancelled, cancelling |
| gray | grey |
| dialog (software) | dialogue (software) |

*Overlay point:* an organization writing in British, Canadian, or Australian English
overrides this whole section in its own `word-list.md`. Doing so also switches the
`Prose.WordList.SpellingVariant` rule to flag the opposite set.

*With no overlay settling the dialect*, the checker does not take American English on
trust: it infers the side from the files it checks (`prose-style-checker` step 1e, which
says what settles it, what is counted, and when nothing is raised).
An overlay is still the way to fix the dialect once for every file.

---

## Entry schema

Add your organization's own general-usage entries by creating a `word-list.md` in your
overlay directory (see the plugin's `docs/reference/overlay.md`). Use these table shapes — the
checker reads them structurally, so the column headers matter.

### Replacement table

Any table whose header row is `❌ …` / `✅ …` (or `Avoid` / `Use instead`) is read as a
replacement list. The left cell is the term to flag; the right cell is the suggestion.

```markdown
| ❌ Avoid | ✅ Use instead |
|---|---|
| ticket | issue |
| onboard (verb) | set up, get started |
```

### Table with a reason

Add a third column and the checker puts it in the violation `message`.

```markdown
| ❌ Avoid | ✅ Use instead | Why |
|---|---|---|
| solutioning | design, planning | Not a word outside internal use |
```

### Severity override

Put a severity in a `Severity` column to override the calibration table in
`prose-style-checker`. Valid values: `MAJOR`, `MINOR`, `NIT`. (`BLOCKER` is not
available to this checker.)

```markdown
| ❌ Avoid | ✅ Use instead | Severity |
|---|---|---|
| beta (of a GA feature) | preview | MAJOR |
```

### Allow list — un-flagging a baseline entry

To stop the baseline flagging a term your organization uses deliberately, list it under
an `## Allowed` heading in your overlay `word-list.md`.

```markdown
## Allowed

| Term | Why |
|---|---|
| click | Our product is desktop-only; "click" is accurate. |
| e.g. | House style keeps Latin abbreviations. |
```

### Replacing a whole baseline file

An overlay file layers on top of the baseline by default. To discard the baseline file
entirely and use only yours, put this marker on the first line of your overlay file:

```markdown
<!-- prose-style: replace -->
```
