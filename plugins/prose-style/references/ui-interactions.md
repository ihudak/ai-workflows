# UI interactions

The verbs used to describe what a reader does in an interface.

**Baseline.** These are the shipped, vendor-neutral defaults. A repo-local or env-var
overlay layers on top of them and wins on conflict — see `prose-style-checker` step 1
("Resolve the active rule set") and the plugin's `docs/reference/overlay.md`. This file applies to product
documentation and UI copy; it is calibrated down to NIT for planning documents.

**Grounded in:** Microsoft Writing Style Guide ("Describing interactions with UI",
"Procedures and instructions", "Formatting text in instructions"); Apple Style Guide
(interface terms, "choose" vs. "select"); Google developer documentation style guide
("UI elements and interaction").

---

## Select — the default interaction verb

"Select" is device-agnostic: it covers mouse, touch, keyboard, and assistive
technology. Use it for links, buttons, options, checkboxes, list values, menu items,
tabs, and text.

- ✅ Select **Save**.
- ❌ Click **Save**. / ❌ Tap **Save**. / ❌ Press **Save**.
- ✅ Edit the name, then select **Save**.

Use **click** or **double-click** only when the interaction is genuinely
mouse-specific (a right-click menu, a drag). Use **tap** only for touch-only content.
Google's guide permits "click" for desktop-only interfaces — that is an overlay
decision, not a baseline one.

Use **press** for physical and keyboard keys: "Press **Enter**", "Press
**Ctrl+C**".

---

## Choose — when the reader decides

Apple distinguishes *choose* (the reader picks based on judgment or preference) from
*select* (the reader marks an item). Both are correct; the distinction is worth
keeping.

- ✅ Choose the retention period that fits your budget.
- ✅ Select **90 days**.

---

## Go to — navigation

Use "go to" for pages, tabs, sections, top-level menu items, URLs, and file paths.

- ✅ Go to the **Operating systems** tab.
- ✅ Go to `example.com/status`.
- ✅ Go to **Settings > Access > Tokens**.
- ❌ Navigate to the **Settings** page.
- ❌ Locate the **Settings** page.

### Navigation sequences

- Use `>` between steps: **Settings > Access > Tokens**.
- Bold each label; do not bold the separator.
- Use the sequence only for a uniform chain of navigation. Mixed actions get full
  sentences.

### See / see also — cross-references

- ✅ For the full list, see [rate limits].
- ❌ For the full list, go to [rate limits]. ("go to" is for the interface, not for docs)

---

## Open — display something

Use for apps, files, folders, dashboards, browser tabs and windows, and terminals.

- ✅ Open the `config.yaml` file.
- ✅ Open a terminal window.
- ❌ Launch the app. / ❌ Fire up a terminal.
- ❌ Open the **Operating systems** tab. (use "go to")

## Close

For apps, dialogs, files, folders, tabs, and notifications.

- ✅ Save and close the file.
- ❌ Exit the dialog. / ❌ Quit the dialog.
- "Quit" is correct for ending an application on macOS; "exit" for a CLI process.

## Clear

For emptying something or deselecting: caches, cookies, fields, checkboxes.

- ✅ Clear your browser cache.
- ✅ Select or clear the **Notify me** checkbox.

---

## Enter — supply a value

- ✅ Enter your access key in the **Token** field.
- ❌ Type your access key. / ❌ Paste your access key. / ❌ Input your access key.
- "Type" is correct only when typing specifically is required (a confirmation phrase).

---

## Sign in / sign out

- ✅ Sign in to your account. — ❌ Log in to your account.
- ✅ Sign out. — ❌ Log out. / ❌ Logoff.
- **Preposition:** sign in **to**, not "sign into".
- As nouns/adjectives: "the sign-in page", "your sign-in credentials". "Login" as a
  noun is widely accepted; the verb is always two words.

---

## Turn on / turn off

Prefer "turn on" and "turn off" for switches, toggles, and settings the reader flips
(Microsoft).

- ✅ Turn on **Automatic updates**.
- ✅ Turn off monitoring for the selected host.
- ❌ Enable **Automatic updates**. / ❌ Disable monitoring.
- ❌ Toggle **Automatic updates**. (never use "toggle" as a verb)

"Enable" is acceptable when the subject is a capability rather than a control:
"Encryption enables compliance with…". Do not use "enable/disable" for the act of
flipping a setting — see `accessibility.md`.

---

## Expand / collapse

- ✅ Expand the **Advanced** section.
- ❌ Open the **Advanced** section. / ❌ Click the arrow.

## Move / drag

- **Move** for repositioning generally (device-agnostic).
- **Drag** only for a pointer-driven move. Always provide a non-drag alternative in the
  same procedure — a drag-only instruction fails keyboard users.

---

## Naming controls

Refer to the **label**, not the control type. The type is visible; the label is the
information.

- ✅ Select **Install now**. — ❌ Select the **Install now** button.
- ✅ In **Region**, select **eu-central-1**. — ❌ In the **Region** dropdown list…
- Name the control type only when the reader has to distinguish two controls with the
  same label.

### Checkboxes and options

- Use **select** and **clear** — not check/uncheck, tick/untick, mark/unmark.
  - ✅ Select **Restart on failure**. — ✅ Clear **Restart on failure**.
  - ❌ Check the **Restart on failure** checkbox.

### Label capitalization

Reproduce a UI label exactly as it appears on screen, including its capitalization —
even where it breaks the sentence-case rule in `formatting.md`. The label is a quotation
of the product, not prose.

---

## Procedure steps

- One action per numbered step.
- State the location first, the action second: "In **Settings**, select **Users**."
- Describe the result only when it is not obvious or when the reader must wait for it.
- Do not narrate the interface ("A dialog appears, which contains a form, which has…").
- Do not describe an icon by shape or color alone (WCAG 1.3.3, 1.4.1) — name it:
  "select the **More options** icon (⋯)".
