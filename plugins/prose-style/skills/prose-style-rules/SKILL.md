---
name: prose-style-rules
description: >
  Prose style rules for writing product documentation, Epics, PRDs, ARDs, release
  notes, and other planning documents. Load this skill when writing or editing
  content that must follow a consistent terminology, voice, grammar, and formatting
  standard. Ships a vendor-neutral baseline and picks up an organization's own style
  guide when one is configured. Triggers on: style guide, house style, writing style,
  terminology, voice and tone, inclusive language, write epic, write PRD, write ARD,
  documentation style, prose review.
allowed-tools: Read, Bash
---

# Prose style rules

This skill gives any writing agent the active prose style rules, so content comes out
correctly styled instead of being corrected afterwards.

## How to use

### 1. Resolve the active rule set

Same mechanism as `prose-style-checker` step 1, in short form. **Every miss is a silent
fall-through — never an error, never a prompt.**

**Baseline (always read):**

```
${CLAUDE_PLUGIN_ROOT}/references/
```

This is also the path `/prose-style-refresh` asks this skill to resolve on its behalf, so that the command takes the baseline's location from the file that states it together with the rule that nothing writes into it, rather than restating either. When a caller asks for the baseline directory, hand back this expanded absolute path. It is read-only: nothing ever writes into it, because a plugin update replaces it.

**Overlay (read the first that resolves, then stop):**

1. `<repo-root>/.prose-style/rules/` — where `<repo-root>` is
   `git rev-parse --show-toplevel` for the content being written, falling back to the
   working directory's repository, falling back to no overlay. `prose-style-checker`
   step 1b ends the same ladder at the deepest common parent of the files it was handed;
   this one cannot, and the difference is the input rather than the rule — a checker is
   given a file list, and content being written has no path yet to take a parent of.
2. `$PROSE_STYLE_PATH` — an absolute path to a rules directory.
3. Nothing — the baseline alone.

A candidate resolves only when it is a readable directory holding at least one `.md`
file.

### 2. Merge

The overlay **augments and overrides** the baseline, per file name. Both are in force;
on any conflict about the same term or rule, **the overlay wins**. A term listed under
an overlay's `## Allowed` heading is not a violation. An overlay file whose first line
is `<!-- prose-style: replace -->` replaces the same-named baseline file outright. An
overlay file with a name no baseline file uses is an additional rule source.

### 3. Write

Apply the rules below while writing. The reference docs carry the full tables and
examples; this checklist is the subset that changes the most sentences.

**When the overlay and this checklist disagree, the overlay wins.** This checklist
restates the *baseline*, which an organization's overlay is entitled to override.

---

## Quick checklist (apply while writing)

### Terminology
- One term per concept, on every page. Never vary a term for variety.
- Write product names exactly as their owners write them: `GitHub`, `PostgreSQL`,
  `npm`, `Kubernetes`, `macOS`.
- Never pluralize or possessivize a product name — use it as an adjective.
- Lowercase a capability described in prose; capitalize only a declared mark or a
  visible UI label.
- Name the version instead of writing "new", "latest", or "currently".

### Excluded words (never use)
- blacklist → blocklist / denylist
- whitelist → allowlist / safe list
- master (tech) → primary / main
- slave → replica / secondary
- grandfathered → legacy / exempt
- native (of people) → name the specific group
- crazy, insane → unexpected / surprising
- sanity check → confidence check
- blind to → unaware of
- cripple → impair / degrade
- dummy → placeholder / sample

### Voice and tone
- **Active voice** by default: actor + verb + object.
- **Second person, present tense**: address the reader as "you".
- **Imperative for steps**: "Select **Save**." — not "You should select **Save**."
- **No hedging**: we believe, arguably, it seems, perhaps.
- **No patronizing**: simply, just, easy, easily, obviously, straightforward.
- **No filler**: in order to → to; it should be noted that → delete; utilize → use.
- **Be specific**: give the number instead of "numerous".
- **Contractions are fine**: it's, don't, you're — but not it'll, would've, mustn't.
- **Spell out negatives in warnings**: "do not", "cannot".

### Grammar
- Singular noun as adjective: "metric browser", not "metrics browser".
- Transitive verbs need an object: "Wait until the image is rendered."
- Singular "they" for a person of unspecified gender.
- "that" restricts (no comma); "which" adds (with comma).
- Keep list items grammatically parallel.

### Formatting
- **Sentence case** in headings and titles.
- **No closing punctuation** in headings (a question mark for an FAQ heading is fine).
- **No gerund (-ing)** in task headings: "Create", not "Creating".
- **Serial comma** always.
- **Spell out 0–9** in prose; numerals from 10 up. Never open a sentence with a numeral.
- **No ampersands** — write "and".
- **Dates**: "January 31, 2026". No ordinals, no `1/31/26`.
- **Acronyms**: expand on first use; never define one in a heading.
- **Space between numeral and unit**: `100 ms`, not `100ms`.
- **No emoji** in reference documentation or UI copy.

### UI interactions (product docs)
- select (not click / tap / press, unless the device is known)
- go to (not navigate to)
- open (files, apps, terminals) / close
- enter (not type / paste / input)
- sign in (not log in); "sign in **to**"
- turn on / turn off (not enable / disable / toggle)
- select and clear (not check / uncheck)
- name the label, not the control: "Select **Save**", not "the **Save** button"

### Accessibility
- **Link text** names the destination and works out of context — never "here",
  "click here", "read more", or a bare URL.
- **Alt text** carries the image's information, not a description of the picture; empty
  alt for decorative images.
- **No sensory-only instructions**: not "the button on the right", "the button below".
- **No color-only signals**: pair color with a label.
- Real heading, list, and table markup — never bold text posing as a heading.
- Expand abbreviations on first use.

### Spelling
- American English by default: behavior, color, center, catalog, analyze, license.
- Where you are adding to an existing document and no overlay sets the dialect, match the
  spelling and dash style that document already uses — British spelling, spaced dashes —
  which is what the checker infers from it and holds the rest of it to.

---

## When NOT to enforce

- Code blocks and inline code — never flag terms inside backticks.
- UI labels — they are quotations of the product; reproduce them exactly.
- Third-party product names — use their official capitalization.
- Direct quotations — preserve the original wording.
- URLs, file paths, identifiers, and CLI flags.

---

## Reference docs (for full details)

Read these from the resolved rule set — overlay first where a file exists in both.

| File | Content |
|---|---|
| `terminology.md` | Naming rules, trademarks, third-party names, and the schema for declaring your own terms |
| `word-list.md` | Excluded and discouraged words, confusables, compounds, spelling, and the entry schema |
| `voice-and-tone.md` | Clarity, directness, respect, helpfulness, contractions, passive voice |
| `grammar.md` | Sentences, tense, person, agreement, verbs, modifiers, parallelism |
| `formatting.md` | Headings, numbers, punctuation, lists, dates, acronyms, links, code, emoji |
| `ui-interactions.md` | Select, go to, open, enter, sign in, turn on/off, control naming |
| `accessibility.md` | WCAG prose criteria, inclusive language, internationalization |
| `top-10-tips.md` | The pre-publish checklist |

Each file opens with the public authorities it is grounded in.
