# Voice and tone

How the writing should sound: clear, direct, and on the reader's side.

**Baseline.** These are the shipped, vendor-neutral defaults. A repo-local or env-var
overlay layers on top of them and wins on conflict — see `prose-style-checker` step 1
("Resolve the active rule set") and the plugin's `docs/reference/overlay.md`. Voice is the most
organization-specific topic in this plugin: if your brand voice differs, override this
file first.

**Grounded in:** Microsoft Writing Style Guide ("Brand voice: above all, simple and
human", "Top 10 tips for Microsoft style and voice"); Google developer documentation
style guide ("Voice and tone", "Write in the second person", "Use active voice");
Apple Style Guide (audience and directness); plainlanguage.gov guidelines.

---

## Clarity

Say the thing. Do not decorate it.

- **Be direct.** State the fact; drop the hedge.
  - ❌ We believe this may potentially affect performance.
  - ✅ This affects performance.
  - Hedge words to catch: *we believe, we think, arguably, it seems, perhaps, somewhat,
    fairly, quite, rather, basically, essentially, actually, generally speaking.*
- **Be concrete.** Use specific numbers, names, and limits.
  - ❌ The endpoint supports numerous concurrent requests.
  - ✅ The endpoint supports up to 200 concurrent requests.
  - Vague quantifiers to catch: *various, numerous, several, a number of, many, a lot
    of, some, robust, powerful, seamless, leverage, cutting-edge.*
- **Be concise.** Cut words that carry no information.

| ❌ Wordy | ✅ Concise |
|---|---|
| in order to | to |
| at this point in time | now |
| due to the fact that | because |
| it should be noted that | (delete) |
| has the ability to | can |
| in the event that | if |
| for the purpose of | to, for |
| a large number of | many, or the number |
| utilize | use |
| leverage (verb) | use |
| facilitate | help, make easier |
| prior to | before |
| subsequent to | after |

---

## Directness

- **Use active voice** by default: *[actor] + [verb] + [object]*.
  - ✅ The scheduler retries the job.
  - ❌ The job is retried by the scheduler.
- **Address the reader as "you."** Second person, present tense.
  - ✅ You can restrict access per project.
  - ❌ The user can restrict access per project.
  - ❌ One can restrict access per project.
- **Use the imperative for instructions.** "Select **Save**." — not "You should select
  **Save**." and not "The user selects **Save**."
- **Put the condition before the action.** "To export a report, select **Export**." —
  so the reader knows whether the step applies before reading it.
- **Do not say "please" in instructions.** It adds a word and implies the step is
  optional.

---

## Respect

- **Never patronize.** Words that call the task easy are wrong for every reader who
  finds it hard.
  - Avoid: *simply, just, easy, easily, obviously, of course, clearly, merely, all you
    have to do is, it's trivial, straightforward.*
  - ❌ Simply run the migration script.
  - ✅ Run the migration script.
- **Do not blame the reader.** Describe the state, not their mistake.
  - ❌ You entered an invalid token.
  - ✅ That token isn't valid. Generate a new one in **Settings > Tokens**.
- **Be honest about limits.** Name what does not work, in the same voice as what does.
  Do not bury a limitation in a hedge.
- **Avoid exclamation marks** in reference and instructional content.
- **Avoid ALL CAPS** for emphasis; it reads as shouting and hurts screen-reader output.

---

## Helpfulness

- **Say why, not only how.** One sentence of purpose before a procedure earns its space.
- **Write from the reader's outcome.** ✅ "You can monitor up to 100 hosts." —
  ❌ "The product supports monitoring of up to 100 hosts."
- **Lead with the answer.** First sentence states the conclusion; details follow.
- **One idea per paragraph.** Front-load the keyword in the first clause.
- **Define jargon on first use, or delete it.** If a term needs a definition and the
  page is not the place for one, choose the plainer word.

---

## Contractions

Contractions are allowed and preferred — they keep the tone conversational
(Microsoft, Google).

- ✅ it's, don't, you're, we're, can't, isn't, doesn't, won't, let's, that's
- ❌ Awkward or ambiguous contractions: it'll, it'd, they'd, there'd, mustn't, shan't,
  would've, could've, should've, needn't, who'd
- **Spell out negatives in warnings, alerts, and stated limitations**, where a missed
  "n't" changes the meaning:
  - ✅ Do not delete the volume before the snapshot completes.
  - ❌ Don't delete the volume before the snapshot completes.
  - ✅ Deletion cannot be undone. — ❌ Deletion can't be undone.

---

## When passive voice is right

Passive voice is a tool, not an error. Use it when the actor is unknown, irrelevant, or
deliberately de-emphasized (Google, Microsoft both allow this).

- ✅ The file was deleted. (actor unknown)
- ✅ Deletion cannot be undone. (warning — the action is the point)
- ✅ Nested transactions are not supported. (stated limitation)
- ❌ An error was encountered by the parser. (actor is right there; use active)

Flag passive voice only where naming the actor would make the sentence shorter or
clearer, not on sight.

---

## Anti-patterns to watch for

| Pattern | Problem | Fix |
|---|---|---|
| "We believe that…" | Hedge | State the fact |
| "It should be noted that…" | Filler | Delete |
| "In order to…" | Wordy | "To…" |
| "Utilize" / "leverage" | Inflated | "Use" |
| "Please" in a step | Unneeded | Delete |
| "Simply" / "just" / "easily" | Patronizing | Delete |
| "Various" / "numerous" | Vague | Give the number |
| "Powerful" / "seamless" / "robust" | Marketing filler | Name the capability |
| "!" in reference content | Overenthusiastic | Use a period |
| "As you know" / "obviously" | Assumes prior knowledge | Delete |
