# Formatting

Headings, numbers, punctuation, lists, dates, acronyms, link text, code, and emoji.

**Baseline.** These are the shipped, vendor-neutral defaults. A repo-local or env-var
overlay layers on top of them and wins on conflict — see `prose-style-checker` step 1
("Resolve the active rule set") and the plugin README. Where two public authorities
disagree, the split is named below so an overlay can pick the other side deliberately.

**Grounded in:** Microsoft Writing Style Guide (headings, capitalization, numbers,
punctuation, lists, dates); Google developer documentation style guide (same topics,
plus code-in-text); The Chicago Manual of Style (serial comma, hyphenation, dashes,
general punctuation); AP Stylebook (named where it diverges from Chicago); W3C WCAG 2.2
(link text, heading structure).

---

## Headings and titles

### Sentence case

Capitalize the first word and proper nouns only. Microsoft and Google both use
sentence case for headings; Apple uses title case for UI element names, which is a
separate rule (see `ui-interactions.md`).

- ✅ Configure retention policies for audit logs
- ❌ Configure Retention Policies for Audit Logs

*Overlay point:* an organization that follows title case for headings overrides this
rule in its own `formatting.md`.

### No closing punctuation

- ✅ Set up single sign-on
- ❌ Set up single sign-on.
- Exception: a question-style heading keeps its question mark — "What is a workspace?"

### No gerund (-ing) forms in task headings

- ✅ Create an alert rule — ❌ Creating an alert rule
- ✅ Migrate from v1 to v2 — ❌ Migrating from v1 to v2

### Heading structure

- One H1 per page — the page title.
- Do not skip levels (H2 → H4). Headings carry document structure for assistive
  technology (WCAG 1.3.1).
- A heading describes the section that follows; it is not a sentence and not a link.
- Do not define an acronym in a heading — define it in the first paragraph below.
- Do not put the only instance of a critical term in a heading; body text must stand
  alone when headings are collapsed.

### Subtitles

- Use a colon, and capitalize the first word after it.
- ✅ Capacity planning: forecast demand before you buy
- ❌ Capacity planning — Forecast demand before you buy

---

## Numbers

### In sentences

- Spell out zero through nine; use numerals for 10 and above.
  - ✅ The cluster has three nodes. ✅ The cluster has 12 nodes.
- Never start a sentence with a numeral — rewrite, or spell it out.
  - ✅ Twelve jobs failed. — ❌ 12 jobs failed.
- Use numerals for all numbers in a comparison series, even below 10.
  - ✅ The set contains 3, 12, and 40 entries.
- ✅ More than 10 — ❌ 10 or more (when you mean strictly greater)

### In headings, tables, and UI

Numerals are fine at any value, including 0–9: "5 ways to cut query cost".

### Measurements, currency, and percentages

- Always numerals: 8 GB, $100, 3.5 lb, 75 °F, 250 ms.
- Insert a space between the numeral and the unit: ✅ 100 ms — ❌ 100ms.
- No space before `%`, `$`, or a degree sign attached to a scale: ✅ 100%, $100.
- Use the digit for a version number exactly as the product prints it.

### Separators and large numbers

- Comma as the thousands separator at four digits and above: 3,450 — 1,200,000.
- No comma in years, page numbers, addresses, or port numbers.
- For round numbers at a million or above, use numeral + word: 8 billion events,
  $3 million per year.

### Ranges

- Use "from X to Y" or "between X and Y" in prose; an en dash (–) in tables and
  headings: 10–20 requests.
- Never mix: ❌ from 10–20.

---

## Punctuation

### Serial (Oxford) comma — required

Chicago, Microsoft, and Google all require it; AP omits it.

- ✅ ingest, transform, and query
- ❌ ingest, transform and query

*Overlay point:* an AP-following organization overrides this rule.

### Comma after an introductory phrase

- ✅ After the migration completes, restart the service.
- ❌ After the migration completes restart the service.

### No comma in a compound predicate

- ✅ The agent collects metrics and forwards them to the gateway.
- ❌ The agent collects metrics, and forwards them to the gateway.
- A comma **is** correct between two independent clauses with different subjects:
  ✅ The agent collects metrics, and the gateway stores them.

### Ampersand

- ❌ Support & services — ✅ Support and services
- Exception: a space-constrained UI label, or a name that officially contains one
  (AT&T, Procter & Gamble).

### Dashes (Chicago)

- **Em dash (—)** for a break in thought. This baseline sets them **closed** (no
  spaces) — Chicago's convention. AP and several house styles space them.
  - ✅ Processes are host-scoped—usually tied to one machine—while services are not.
  - *Overlay point:* flip to spaced em dashes, or to spaced en dashes, in your overlay.
    With no overlay restating this rule, the checker infers spaced or closed from the
    files it checks and flags the minority (`prose-style-checker` step 1e).
- **En dash (–)** for ranges and for compound adjectives with an open element.
- **Hyphen (-)** for compound modifiers only. See `grammar.md` for hyphenation.

### Quotation marks

- Double quotes for quoted text; single quotes only inside a quotation.
- In American style, commas and periods go inside the closing quote.
- Do not use quotation marks for emphasis or for UI labels — use bold for UI labels.

### Colons and semicolons

- A colon introduces a list, a definition, or an explanation. The clause before it must
  stand alone as a sentence.
- Use semicolons sparingly; prefer two sentences.

### Slashes

- Avoid `and/or` — say what you mean ("A, B, or both").
- Avoid a slash for alternatives in prose; write "or".

### Parentheses for acronyms

- Full term first, acronym second: ✅ service level objective (SLO)
- ❌ SLO (Service Level Objective)

---

## Acronyms and abbreviations

- Expand on first use per page, then use the acronym consistently (WCAG 3.1.4).
- Do not capitalize the expansion unless it is a proper noun.
  - ✅ software-defined networking (SDN)
  - ❌ Software-Defined Networking (SDN)
- Do not define an acronym you use only once — use the full term.
- Do not add an apostrophe to a plural acronym: ✅ APIs — ❌ API's.
- Spell out Latin abbreviations in prose: "for example" not "e.g."; "that is" not
  "i.e."; "and so on" not "etc.".

---

## Lists

### Bulleted lists

- Introduce with a lead-in. Use a colon when the lead-in is a complete sentence.
- Keep items parallel in grammatical form (see `grammar.md`).
- If the items are complete sentences, each ends with a period.
- If the items are fragments of three words or fewer, use no terminal punctuation.
- If the items complete the lead-in sentence, punctuate the last one with a period and
  the rest with nothing.
- Aim for two to seven items. A longer list usually wants a table or subheadings.

### Numbered lists

- Only for ordered content: sequential procedures or ranked items.
- One action per step. Each step is a complete imperative sentence with a period.
- State the location before the action within a step: "In **Settings**, select **Users**."

### Tables

- Every column has a header. Do not leave cells empty — use an em dash or "None".
- Do not use a table for layout; tables are for tabular data (WCAG 1.3.1).

---

## Dates and times

- **Dates:** month day, year — "January 31, 2026". Spell the month; do not abbreviate
  it in prose.
  - ❌ 31 January 2026 (non-US order), ❌ 1/31/26 (ambiguous across locales)
  - Use ISO 8601 (`2026-01-31`) for machine-readable or log content only.
  - No ordinals: ❌ February 21st — ✅ February 21.
- **Times:** 12-hour clock with AM/PM in prose ("10:45 AM"); 24-hour only where the
  product itself shows 24-hour.
- Include the time zone whenever the time is actionable: "10:45 AM UTC".
- **Seasons are hemisphere-dependent** — use a quarter or a month: ✅ Q1 2026 —
  ❌ this winter.
- Do not write a duration as a bare number: ✅ for 30 seconds — ❌ for 30.

---

## Link text

See `accessibility.md` for the full WCAG rules. In brief:

- Link text names the destination and works read out of context.
- ❌ "here", "this page", "link", "read more", "click here", a bare URL.
- Sentence case, no closing punctuation inside the link.
- Say what the reader gets: ✅ "See [rate limits]" — ❌ "See [the documentation]".

---

## Code and UI in text

- Inline code, identifiers, file paths, flags, and literal values go in backticks.
- Do not apply prose rules inside code — no sentence casing, no serial commas, no
  spelling correction. See the checker's context rules.
- **Bold** for UI labels the reader acts on; do not add the control type:
  ✅ Select **Save** — ❌ Select the **Save** button.
- Use a code block with a language tag for anything longer than one line.
- Do not put a period inside a command line the reader copies.

---

## Emoji and symbols

- No emoji in reference documentation, UI copy, or API docs. They render
  inconsistently, translate poorly, and are read aloud verbatim by screen readers.
- Emoji in changelogs, READMEs, or internal notes are an organization's call — an
  overlay decision, not a baseline one.
- Do not use ASCII art, arrows made of characters (`-->`), or `<` `>` for navigation
  in prose; write "go to A, then B" or use a real separator.
