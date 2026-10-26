# Grammar

Sentence structure, verbs, pronouns, and agreement.

**Baseline.** These are the shipped, vendor-neutral defaults. A repo-local or env-var
overlay layers on top of them and wins on conflict — see `prose-style-checker` step 1
("Resolve the active rule set") and the plugin's `docs/reference/overlay.md`.

**Grounded in:** The Chicago Manual of Style (general-English rules — agreement,
restrictive vs. non-restrictive clauses, fragments); Microsoft Writing Style Guide
("Grammar and parts of speech"); Google developer documentation style guide
("Grammar and parts of speech", "Second person", "Present tense").

---

## Sentences and fragments

- A sentence has a subject and a predicate and ends with a period (rarely a question
  mark; almost never an exclamation mark).
- Shorter sentences read faster and translate better. Split any sentence carrying two
  independent ideas.
- A sentence used as a heading or a title takes no closing punctuation.

### Fragments

Fragments are correct in definitions, glossary entries, and table cells, and take no
closing period when they are not full sentences.

- ✅ **Connect time**: the time taken to establish the TCP connection
- ✅ **Connect time**: the time taken to establish the TCP connection. If there are
  multiple connections, this is the total. (second part is a full sentence, so it takes
  a period)

---

## Active voice

Structure: *[actor] + [verb] + [object]*.

- ✅ The scheduler retries the job.
- ❌ The job is retried by the scheduler.
- ✅ All three formats accept the same payload.
- ❌ The same payload is accepted in all three formats.

See `voice-and-tone.md` for when passive voice is the right choice.

---

## Tense

- **Present tense** for how the system behaves and for instructions.
  - ✅ The service restarts after the update.
  - ❌ The service will restart after the update.
- **Past tense** for things that already happened: release notes, changelogs, incident
  write-ups.
- Avoid future tense unless the event is genuinely in the future relative to the
  reader's action.

---

## Person

- **Second person** ("you") for the reader.
  - ✅ You can configure the retention window.
  - ❌ The user can configure the retention window.
  - ❌ Users should configure their retention windows.
- **First person plural** ("we") only where the organization is genuinely the actor
  ("We deprecated the v1 endpoint"). Never as a substitute for the reader.
- **Imperative** for procedure steps: "Select **Save**."

---

## Pronouns

- **Singular "they"** for a person of unspecified gender (Chicago 17th ed. accepts this;
  Microsoft and Google require it).
  - ✅ their, them, they — ❌ he, she, his or her, (s)he
- **Every pronoun needs an unambiguous antecedent.** If "it" or "this" could refer to
  two nouns, repeat the noun.
  - ❌ The job calls the webhook, and it retries on failure.
  - ✅ The job calls the webhook, and the job retries on failure.
- Avoid starting a sentence with a bare "This" or "That"; add the noun.

---

## Agreement

- Subject and verb agree in number, across intervening phrases.
  - ✅ The list of failed jobs **is** long. — ❌ The list of failed jobs **are** long.
- Collective nouns (team, group, set) take singular verbs in American English.
- "Data" is treated as singular in technical writing (Microsoft, Google both do).
  - ✅ The data is stale. — ❌ The data are stale.
- "None" takes a singular verb when it means "not one".

---

## Nouns used as adjectives

Keep the noun **singular** when it modifies another noun.

- ✅ metric browser — ❌ metrics browser
- ✅ user permission model — ❌ users permission model
- ✅ root cause analysis — ❌ root causes analysis
- ✅ credential vault — ❌ credentials vault

**Exception:** a UI element whose visible label is plural keeps its label exactly.
- ✅ the **Services** page, the **Locations** tab

Do not stack more than two nouns as modifiers. Break the chain with a preposition.
- ❌ the account team resource quota policy page
- ✅ the policy page for account team resource quotas

---

## Verbs

### Transitive verbs need an object

- ❌ Wait until the image renders.
- ✅ Wait until the image is rendered. / ✅ Wait until the browser renders the image.
- ❌ Wait until the software installs.
- ✅ Wait until the software is installed.

### Do not make nouns into verbs

- ❌ Action the request. — ✅ Act on the request.
- ❌ Solution the problem. — ✅ Solve the problem.
- ❌ Architect a system. — ✅ Design a system.

### Do not bury the verb in a noun (nominalization)

- ❌ Perform an installation of the agent. — ✅ Install the agent.
- ❌ Make a determination. — ✅ Determine.
- ❌ Provide protection for. — ✅ Protect.

---

## Modifiers

- Put the modifier next to what it modifies.
  - ❌ You can only run the migration once. (only what?)
  - ✅ You can run the migration only once.
- Avoid dangling participles: the subject of the participle must be the subject of the
  sentence.
  - ❌ After deleting the volume, the snapshot is unavailable.
  - ✅ After you delete the volume, the snapshot is unavailable.
- Hyphenate a compound modifier before a noun; do not hyphenate it after (Chicago).
  - ✅ a read-only mount / the mount is read only
  - ✅ a well-known port / the port is well known
  - Never hyphenate an *-ly* adverb: ✅ a fully managed service — ❌ a fully-managed service

---

## Restrictive vs. non-restrictive clauses

- **that** introduces a restrictive clause — no comma; the clause identifies which one.
  - ✅ The service that failed is in the EU region.
- **which** introduces a non-restrictive clause — with a comma; the clause adds detail.
  - ✅ The billing service, which runs nightly, failed.

---

## Parallel structure

Items in a list, a heading set, or a coordinated series take the same grammatical form.

- ✅ Create a token, configure the endpoint, and run the import.
- ❌ Create a token, configuring the endpoint, and the import runs.
