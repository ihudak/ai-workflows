# Accessibility and inclusive language

Rules for prose that every reader can use, and language that respects every reader.

**Baseline.** These are the shipped, vendor-neutral defaults. A repo-local or env-var
overlay layers on top of them and wins on conflict — see `prose-style-checker` step 1
("Resolve the active rule set") and the plugin's `docs/reference/overlay.md`.

**Grounded in:** W3C Web Content Accessibility Guidelines (WCAG) 2.2 — success criteria
cited inline; Conscious Style Guide; Google developer documentation style guide
("Write inclusive documentation"); Microsoft Writing Style Guide ("Bias-free
communication", "Accessibility guidelines and requirements").

---

## Core principle

Write so that anyone can act on the text — regardless of ability, assistive
technology, first language, or prior exposure to the product. Before naming a human
characteristic (gender, ability, age, race, religion, orientation), ask whether it is
relevant to the sentence. Usually it is not.

---

## Prose accessibility (WCAG)

These are the WCAG criteria a writer — not a developer — controls.

### Alt text for images (WCAG 1.1.1, Non-text Content)

- Every meaningful image carries alt text that conveys the same information as the
  image, not a description of the picture.
- ✅ `![Latency rises after the 14:00 deploy](chart.png)`
- ❌ `![Screenshot](chart.png)` — describes the file, not the information
- ❌ `![Image of a chart showing latency](chart.png)` — "image of" is redundant; screen
  readers already announce it as an image
- Purely decorative images take empty alt text (`![](divider.png)`), never a filler word.
- A complex chart or diagram needs its data or conclusion in the surrounding prose;
  alt text alone cannot carry it.

### Link text (WCAG 2.4.4 and 2.4.9, Link Purpose)

- Link text describes the destination and makes sense read on its own, out of context.
  Screen-reader users navigate by a list of links with no surrounding sentence.
- ✅ See [configure retention policies].
- ❌ See [here] for retention policies. / ❌ To learn more, [click here].
- ❌ [Read more] / ❌ [this page] / ❌ [link]
- Do not use the raw URL as link text, except when the URL itself is the thing being
  taught (an endpoint, a CLI target).
- Two links on the same page with the same text must go to the same destination.
- Do not put closing punctuation inside the link text.

### Do not rely on sensory characteristics (WCAG 1.3.3)

Instructions must not depend on shape, size, position, or sound alone.

- ✅ Select **Save** in the upper right.
- ❌ Select the round button on the right.
- ❌ Select the button below. (breaks in reflowed or linearized layouts)

### Do not rely on color alone (WCAG 1.4.1)

- ✅ Failed runs are marked red and carry a **Failed** label.
- ❌ Failed runs are shown in red.

### Headings and structure (WCAG 1.3.1, 2.4.6)

- Use real heading markup, never bold text standing in for a heading.
- Headings describe the section that follows; do not skip levels (H2 → H4).
- One H1 per page.
- Use real list markup for lists and real table markup for tabular data; never fake
  either with dashes, spaces, or line breaks.

### Abbreviations (WCAG 3.1.4) and reading level (WCAG 3.1.5)

- Expand an abbreviation on first use in a page: full term, then the abbreviation in
  parentheses.
- Prefer the shorter, more common word. Keep sentences short; one idea per sentence.

---

## Ableist language — avoid

These words characterize people by ability, or treat disability as a defect.

| ❌ Avoid | ✅ Alternative |
|---|---|
| crazy, insane, nuts | unexpected, surprising, confusing |
| sanity check | confidence check, quick check, validation |
| blind to, turn a blind eye | unaware of, overlook, ignore |
| deaf to, fell on deaf ears | unresponsive to, ignored |
| cripple, crippled | impair, break, degrade, slow down |
| dummy (value, data) | placeholder, sample, test |
| lame | poor, inadequate |
| suffers from, victim of | has, lives with |
| the disabled, the blind | disabled people, blind people (or per the person's own preference) |

Note: "disable" / "enable" applied to a *setting* is not ableist language; see
`ui-interactions.md` for the separate UI-verb rule.

---

## Racist and violent language — avoid

Terms rooted in slavery, exclusion, or violence.

| ❌ Avoid | ✅ Alternative |
|---|---|
| blacklist | blocklist, denylist, exclude list |
| whitelist | allowlist, safe list, approved list |
| master (technical) | primary, main, source, leader |
| slave | replica, secondary, worker, follower |
| grandfathered | legacy, exempt, pre-existing |
| native (of people) | name the specific group; for software, "built-in" |
| kill, hang, abort (where a plain verb works) | stop, end, force quit, cancel |
| hit (a target) | reach, meet |

Do not flag correct English uses: "she mastered the API", "MasterCard", "master's
degree", "the master copy of a recording" in a quotation.

---

## Gendered language — avoid

- Use **they / them / their** as the singular pronoun when the person is unspecified.
- ✅ their, them, they — ❌ he, she, his, her, he/she, (s)he, his or her
- Prefer rewriting to second person or plural: "You configure your dashboard."

| ❌ Avoid | ✅ Alternative |
|---|---|
| chairman | chair, chairperson |
| spokesman | spokesperson |
| manpower | workforce, staff, personnel, capacity |
| mankind, man-hours | people, humanity, person-hours |
| guys (addressing a group) | everyone, folks, team |
| middleman | intermediary, broker |

---

## Age, health, and socioeconomic framing

- Do not mention age unless it is relevant; avoid "young", "elderly", "digital native".
- Avoid casual clinical terms: "OCD", "bipolar", "schizophrenic", "ADHD" as metaphors.
- Avoid "first-world problem", "third world"; name the region or the constraint.

---

## Diversity in examples

- Vary names, places, holidays, currencies, and family structures across examples.
- Avoid defaulting to one culture's placeholder names ("John Doe", "Jane Doe").
- Avoid slang, sports metaphors, military metaphors, and insider jokes — they exclude
  readers and do not translate.

---

## Internationalization

### Writing for translation

- Use familiar, common words. Avoid academic or invented vocabulary.
- Keep sentences short and complete; end them with a period.
- Prefer active voice so the subject-verb-object order survives translation.
- Do not omit optional relative pronouns: "the setting **that** you configured", not
  "the setting you configured".
- Avoid idioms, jokes, puns, and culture-bound references.
- Do not assume text length is fixed — translations can run 30% longer.
- Never build a sentence out of concatenated UI strings; translate whole sentences.

### Locale-dependent content

Check that each of these is either localized or written locale-neutrally:

- Numbers, decimal separators, and currency
- Dates and times, and time zones
- Units of measure
- Address and phone formats
- Reading direction (left-to-right vs. right-to-left) in layout and screenshots
- Names, images, and scenarios that read as regional

### Do not translate

- Product and feature names, when the organization treats them as marks
- Trademarked terms, with their symbols
- Code, identifiers, file paths, and CLI flags
