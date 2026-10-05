---
name: omega
description: Fixture command in the second plugin.
---

Fixture body.

**Core references.** A citation of the form `dev-workflows:<name>` names a shared reference in the `dev-workflows` plugin. Load it with `Skill(skill: "dev-workflows:reference", args: "<name>")` — never by path.

Before anything else, load `dev-workflows:phase-handoff` — `Skill(skill: "dev-workflows:reference", args: "phase-handoff")`.

Agent notices follow `dev-workflows:untrusted-content` — `Skill(skill: "dev-workflows:reference", args: "untrusted-content")`.
