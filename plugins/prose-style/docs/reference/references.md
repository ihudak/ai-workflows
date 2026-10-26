# References

The baseline is 8 files under `references/` — distilled, actionable rules, not copies of any vendor's style guide. Each names the public authorities it is grounded in.

| File | Covers | Grounded in |
|---|---|---|
| `terminology.md` | Naming rules, trademarks, third-party names, and the schema for declaring your own terms | Microsoft, Google, Apple, Chicago |
| `word-list.md` | Excluded and discouraged words, confusables, compounds, spelling variants, and the entry schema | Microsoft, Google, Merriam-Webster, Conscious Style Guide |
| `voice-and-tone.md` | Clarity, directness, respect, helpfulness, contractions, passive voice | Microsoft, Google, Apple, plainlanguage.gov |
| `grammar.md` | Sentences, tense, person, agreement, verbs, modifiers, parallelism | Chicago, Microsoft, Google |
| `formatting.md` | Headings, numbers, punctuation, lists, dates, acronyms, links, code, emoji | Microsoft, Google, Chicago, AP, WCAG |
| `ui-interactions.md` | Select, go to, open, enter, sign in, turn on and off, control naming | Microsoft, Apple, Google |
| `accessibility.md` | WCAG prose criteria, inclusive language, internationalisation | W3C WCAG 2.2, Conscious Style Guide, Google, Microsoft |
| `top-10-tips.md` | The pre-publish checklist | Microsoft, Google, plainlanguage.gov, WCAG |

Where two authorities disagree — the serial comma (Chicago against AP), spaced dashes, "click" against "select" — the baseline picks one, names the split in the file, and marks it as an overlay point: the place your [overlay](overlay.md) is expected to decide. For the spelling variant and the dash, the checker infers the side from your files where no overlay decides it.

The baseline deliberately ships **no organisation-specific terms**: `terminology.md` holds the naming rules and the schema for declaring your own, and the terms are yours to supply in an overlay.

## Skills

One skill ships under `skills/`: the writing side of the same rules. An agent that produces prose loads it, and it resolves the same baseline-plus-overlay rule set and carries a short checklist, so text comes out styled rather than being corrected afterwards.

| Skill | Invocable | What it's for |
|---|---|---|
| `prose-style-rules` | Yes | A writing aid for any agent writing prose: the baseline and your overlay, and a pre-publish checklist. |

Unlike the three typed-only commands, it stays in the list of skills the model can pick from.
