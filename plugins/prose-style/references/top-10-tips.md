# Top 10 tips

The highest-impact rules, as a quick checklist. Every one is stated in full elsewhere in
this directory; this file is the pass you make before you publish.

**Baseline.** These are the shipped, vendor-neutral defaults. A repo-local or env-var
overlay layers on top of them and wins on conflict — see `prose-style-checker` step 1
("Resolve the active rule set") and the plugin's `docs/reference/overlay.md`.

**Grounded in:** Microsoft Writing Style Guide ("Top 10 tips for Microsoft style and
voice"); Google developer documentation style guide ("Highlights"); plainlanguage.gov
federal plain-language guidelines; W3C WCAG 2.2.

---

## 1. Lead with the answer

Put the conclusion in the first sentence and the details after it. Readers scan the top
of a page and leave. → `voice-and-tone.md`

## 2. Write in the second person, present tense, active voice

"You configure the retention window." Not "the retention window can be configured", and
not "the user will configure". → `grammar.md`, `voice-and-tone.md`

## 3. Use the plainest word that is accurate

"Use", not "utilize". "Help", not "facilitate". Define a technical term at first use or
choose a different one. → `word-list.md`

## 4. Cut the words that carry nothing

"In order to" → "to". "It should be noted that" → delete. If the sentence survives
without the word, the word was not doing anything. → `voice-and-tone.md`

## 5. Delete every "simply", "just", and "easily"

The task is not easy for the reader who is stuck on it, and the word never adds
information. → `word-list.md`

## 6. One term per concept, everywhere

Never vary the word for variety's sake. Two words read as two things. Declare the
canonical term so the checker can enforce it. → `terminology.md`

## 7. Make headings sentence case, structural, and honest

Sentence case, no closing period, no gerund, no skipped levels, no acronym defined for
the first time in a heading. → `formatting.md`

## 8. Write link text that works out of context

Name the destination. Never "here", "this page", or "read more" — a screen reader reads
the links as a list with no sentence around them (WCAG 2.4.4). → `accessibility.md`

## 9. Write language that includes every reader

No blacklist/whitelist, no master/slave, no ableist metaphors, singular "they", diverse
examples, and alt text that carries the information rather than describing the picture.
→ `accessibility.md`

## 10. Be specific about numbers, dates, and versions

Give the actual limit instead of "numerous". Write "January 31, 2026", not "1/31/26".
Name the version instead of "the new release" — documentation outlives the word "new".
→ `formatting.md`, `terminology.md`

---

## Bonus: the pre-publish pass

- Front-load the keyword in each heading and first sentence.
- Keep list items grammatically parallel.
- One idea per paragraph; one action per procedure step.
- Read the procedure and do it. If a step is missing, you will find it there.
- Check every instruction against the interface it describes — a rule can only be as
  accurate as the product it documents.
