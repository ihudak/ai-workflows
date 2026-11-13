---
name: weakness-classes
description: Runs workflows-core's weakness-classes.py for a command — the weakness classes the security findings registers hold, for the repositories a piece of work touches or recurring across every register at a ref — and prints the path of the JSON it wrote, or one line saying why it did not run. The script reads each register by its format and prints validated fields only. Takes its flags in one fixed order, and passes no value holding a character outside [A-Za-z0-9._:/@+=-]. Called by commands only, never by an agent.
user-invocable: false
allowed-tools: Bash
---

# weakness-classes — the weakness classes the security registers hold

The argument is the verb, `classes` or `across`, then its flags in the order below, each value between single quotes: `classes --repo 'api' --component 'api:src/orders'`, or `across --ref 'origin/main'`. The skill adds `--specs` itself. `workflows-core:security-register-format` §7 is the rule, each flag and each field of the JSON, and `${CLAUDE_PLUGIN_ROOT}/scripts/weakness-classes.py` computes it. This text is what your run executes: making the call reads nothing more.

Only a command calls this skill, never an agent. The command hands the path to its agent, or reads the JSON's fields itself, and opens no register for the classes: the JSON is all the call gives it, and a finding's text is never in it.

## The argument rule

A value taken from a register is text the scanner wrote — a finding's `origin` above all, whose plugin ID `register.py` checks only for a `:`. So no value reaches the command line unless each of its characters is a letter, a digit, or one of `.` `_` `:` `/` `@` `+` `=` `-` — the class `[A-Za-z0-9._:/@+=-]`. A value from a register can also hold a quote that ends it early, after which the rest reads as more flags: an origin `x' --prd-key 'K-1`, written as `--origin '<origin>'`, reads as an origin `x` and a `--prd-key`. So the flags are taken in one order only, origins last, and each single-value flag once: whatever is smuggled into an origin can then be only one more `--origin`, and every other flag that stands out of place is refused. Read the argument in three steps, in order:

1. **Its words.** The verb is the text before the first ` --` (a space and two hyphens), or the whole argument where it has none. Each flag is a ` --` and the word after it, up to the next space. Its value is the text after that space, up to the next ` --` or the argument's end, with trailing spaces and then one pair of enclosing single quotes taken off.
2. **The order**, read on the argument as written, before step 3 drops anything. The verb is `classes` or `across`. The flags come in this order and no other: every `--repo`; then every `--component`; then at most one `--prd-key`; then at most one `--ref`; then every `--origin`, always last. `classes` takes all of these but `--ref`, and `across` takes `--ref` alone. Where the verb or a flag is any other — `--specs`, which the skill adds itself, and `--today`, since the script dates the run itself, among them — where a flag stands out of that order, where `--prd-key` or `--ref` comes twice, or where nothing stands between a flag and the next ` --` or the argument's end, run nothing: print `weakness-classes: not run (usage: the argument is not a verb and its flags in the order the skill takes them)`, and no path.
3. **The characters.** A `--component` whose value is empty or holds any character outside the class — a space, a bracket, a quote — is dropped, flag and value. Its `--repo` stays, so the run loses only whether a class lies inside that component (`in_component`). Where the value of any other flag holds such a character, run nothing: print `weakness-classes: not run (an argument holds a character the skill does not pass)`, and no path.

No line you print ever holds a value that failed.

## The call

Make one Bash call, with a timeout of 600000 ms:

```bash
(
out=; trap '[ -n "$out" ] && command rm -f -- "$out"' EXIT; trap 'exit 129' HUP
out=$(TMPDIR="<scratchpad>" command mktemp -t dw-weakness-classes-XXXXXX.json 2>/dev/null) || { echo 'weakness-classes: not run (no temporary file could be made)'; exit; }
err=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/weakness-classes.py" <verb> --specs "${SPECS_PATH-}" <flags> 2>&1 > "$out"); code=$?
if [ "$code" -ne 0 ]; then
  case "$err" in
    'weakness-classes: not run (usage: an unknown verb or flag, or a flag without its value)' | \
    'weakness-classes: not run (usage: --specs is required)' | \
    'weakness-classes: not run (usage: --repo is required)' | \
    'weakness-classes: not run (usage: --ref is required)' | \
    'weakness-classes: not run (--repo is not a repository slug)' | \
    'weakness-classes: not run (--prd-key is not a key)' | \
    'weakness-classes: not run (--today is not a real YYYY-MM-DD date)' | \
    'weakness-classes: not run (--component names a repository no --repo names)' | \
    'weakness-classes: not run (--specs is not a directory)' | \
    'weakness-classes: not run (--ref is not a plain ref name)' | \
    'weakness-classes: not run (git could not be run in --specs)' | \
    'weakness-classes: not run (--specs is not the top level of a git work tree)' | \
    'weakness-classes: not run (--ref names no commit in --specs)' | \
    'weakness-classes: not run (git could not list --specs at --ref)' | \
    'weakness-classes: not run (internal error)') printf '%s\n' "$err" ;;
    *) printf 'weakness-classes: not run (the script exited %s)\n' "$code" ;;
  esac
elif python3 -I -c 'import json, sys; sys.exit(not isinstance(json.load(open(sys.argv[1], encoding="utf-8")), dict))' "$out" 2>/dev/null; then
  trap - EXIT; printf '%s\n' "$out"
else
  echo 'weakness-classes: not run (the script exited 0 without a JSON object)'
fi
)
```

- `<verb>` is the argument's verb. `<flags>` is each flag the rule kept, in the argument's order, each followed by its value between single quotes: `--repo 'api' --component 'api:src/orders'`. A value the rule passed holds no quote, so it cannot leave its quotes.
- `<scratchpad>` is the scratchpad directory your session names. Where it names none, or one that does not exist, drop `TMPDIR="<scratchpad>" ` and run `command mktemp` as written — `workflows-core:run-flags` §7, stated here so you read nothing more.
- Where your run took `$SPECS_PATH` from an answer rather than from the environment, open the call with `export SPECS_PATH='<the value>';`, as `specs-git` does.

## What it prints

The skill's result is one line — the one line the call printed, or the argument rule's refusal — and you print it, verbatim, as your last line.

- **A path**, where the script exited 0 and its file holds a JSON object: the file's absolute path, holding §7.4's object for `classes` or §7.5's for `across`. Hand it on, or read its fields. The file is never edited and never removed.
- **A line beginning `weakness-classes: not run (`**, on every other outcome, the argument rule's refusals included, and you print no path. The call's `EXIT` trap removes the file it made wherever its subshell ends, a SIGTERM, SIGINT or SIGHUP to the call included; a SIGKILL can leave the file, and no path is printed either way. This line is the skill's error that a caller's report line quotes. The script's stderr is printed only where it is, whole, one of the script's own lines — the closed list in the block's `case`; anything else the script wrote — a traceback, a warning, a second line — is never printed. An exit other than 0 is a failure whatever its stdout held, and so is an exit 0 whose file is empty or holds no JSON object.

Where the call prints nothing — the harness stopped it at its timeout — print `weakness-classes: not run (the call did not finish)`, and no path.

## What a failure line means

So that a caller can say why it went without the classes. Each line names a flag, never its value; the script's other lines are in §7.4's and §7.5's tables.

| The line's `(…)` | What it means |
|---|---|
| `usage: the argument is not a verb and its flags in the order the skill takes them` | the skill's step 2: an unknown verb or flag, `--specs` or `--today`, a flag out of order, a second `--prd-key` or `--ref`, or a flag with no value; nothing ran |
| `an argument holds a character the skill does not pass` | a value other than a `--component`'s holds a character outside the class above; nothing ran |
| `usage: an unknown verb or flag, or a flag without its value` | from the script: a value opening with `-`, which it reads as a flag (a `-` before a number, such as `-1`, it reads as a value) |
| `--repo is not a repository slug` | a `--repo` holds a `:`, `/`, `@`, `+` or `=`, is empty, or is `.` or `..` |
| `--component names a repository no --repo names` | a `--component`'s id, or its part before the first `:`, is no `--repo` |
| `--specs is not a directory` | `$SPECS_PATH` is unset or empty, or names no directory |
| `--specs is not the top level of a git work tree` | `across` only: `$SPECS_PATH` is a directory inside the specs repository rather than its top level, or git refuses the repository — `safe.directory`'s refusal of one another user owns among them |
| `--ref is not a plain ref name` | `across` only: the ref is empty, holds a `:` or `=`, or opens with `.`, `/`, `@`, `+` or a `-` before a number, so a default branch named with `=` cannot be read; one named with `#`, `,` or any other character outside the class is refused by the skill first |
| `--ref names no commit in --specs` | `across` only: the ref names no commit in the specs repository |
| `the script exited <code>` | the script exited other than 0 without exactly one line of its own |
| `the script exited 0 without a JSON object` | its file is empty, or holds no JSON object |
| `no temporary file could be made` | `mktemp` failed; the script did not run |
| `the call did not finish` | the harness stopped the call at its timeout |
