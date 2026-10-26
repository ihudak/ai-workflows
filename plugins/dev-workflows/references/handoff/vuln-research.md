# vuln-research Handoff Format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

## Input (orchestrator → vuln-research)

```markdown
## Vuln Research Request
repo: /absolute/path/to/repo
cves:
  - id: CVE-2023-46604
    address: PROJ-2423     # optional folder key; omit when the token carried none
  - id: CVE-2024-12345    # bare CVE, no address
ecosystem_hint: java      # optional; helps when auto-detection is ambiguous
dependency_tree_files:    # optional; on every dispatch after a NEEDS_TREE, for those CVEs: each ecosystem's
  Maven: /tmp/dw-vuln-tree-AbC123   # dependency tree, under its name, written by /vuln Step 2
model_routing:            # optional; if present, echo back in output.
  classification: SIGNIFICANT      # See `workflows-core:model-routing/classification` for the full model-routing schema.
  # The orchestrator MUST re-invoke this agent under Opus for HIGH-RISK
  # CVEs, and SHOULD re-invoke for SIGNIFICANT CVEs involving a major bump
  # or non-trivial breaking-change surface (per the `/vuln` command Step 2).
  # That re-invocation is the orchestrator's responsibility, not this
  # agent's.
```

## Output (vuln-research → vuln-fixer)

```markdown
## Vuln Research Report

### CVE-2023-46604
status: READY             # READY | NEEDS_TREE | NOT_IN_REPO | LOOKUP_FAILED | SKIP_NON_CVE
address: PROJ-2423
description: "Apache ActiveMQ RCE via ClassInfo deserialization"
library: activemq-broker
ecosystem: Maven
vulnerable_range: "<5.15.16"
current_version: "5.15.5"
safe_version: "5.15.16"
introduced_by: null       # for a transitive library: the direct dependency that brings it in, from the tree
files:
  - path: pom.xml
    change: "bump activemq-broker.version from 5.15.5 to 5.15.16"
error: null               # error message if status != READY

### CVE-2024-99999
status: NOT_IN_REPO
library: some-other-lib
error: "Library 'some-other-lib' not detected in repo"
```

**status values:**
- `READY` — research complete, safe to hand off to vuln-fixer
- `NEEDS_TREE` — no manifest or lockfile names the library, and the ecosystem pulls dependencies in
  transitively with no lockfile that would list it (`build-systems.md` *Resolving the dependency tree*):
  whether the repo uses it is not yet known. The orchestrator resolves the tree and dispatches again with
  `dependency_tree_files:`, which settles it as `READY` or `NOT_IN_REPO`; never terminal
- `NOT_IN_REPO` — library not used in this repo; skip fix
- `LOOKUP_FAILED` — NVD API unavailable or CVE not found
- `SKIP_NON_CVE` — ID was CWE or OWASP, not a CVE
