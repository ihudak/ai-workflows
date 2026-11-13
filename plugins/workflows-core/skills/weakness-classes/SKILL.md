---
name: weakness-classes
description: Runs workflows-core's weakness-classes.py for a command — the weakness classes the security findings registers hold, for the repositories a piece of work touches or recurring across every register at a ref — and prints the path of the JSON it wrote, or one line saying why it did not run. The script reads each register by its format and prints validated fields only. Passes no argument value holding a character outside [A-Za-z0-9._:/@+=-]. Called by commands only, never by an agent.
user-invocable: false
allowed-tools: Bash
---

# weakness-classes — the weakness classes the security registers hold

The argument is the verb, `classes` or `across`, then its flags as your command wrote them, each value between single quotes: `classes --repo 'api' --component 'api:src/orders'`, or `across --ref 'origin/main'`. The skill adds `--specs` itself. `workflows-core:security-register-format` §7 is the rule, each flag and each field of the JSON, and `${CLAUDE_PLUGIN_ROOT}/scripts/weakness-classes.py` computes it. This text is what your run executes: making the call reads nothing more.

Only a command calls this skill, never an agent. The command hands the path to its agent, or reads the JSON's fields itself, and opens no register for the classes: the JSON is all the call gives it, and a finding's text is never in it.

## The argument rule

A value taken from a register is text the scanner wrote — a finding's `origin` above all, whose plugin ID `register.py` checks only for a `:`. So no value reaches the command line unless each of its characters is a letter, a digit, or one of `.` `_` `:` `/` `@` `+` `=` `-` — the class `[A-Za-z0-9._:/@+=-]`. Read the argument in three steps, in order:

1. **Its words.** The verb is the text before the first ` --` (a space and two hyphens), or the whole argument where it has none. Each flag is a ` --` and the word after it, up to the next space. Its value is the text after that space, up to the next ` --` or the argument's end, with trailing spaces and then one pair of enclosing single quotes taken off.
2. **The characters.** A `--component` whose value is empty or holds any other character — a space, a bracket, a quote — is dropped, flag and value. Its `--repo` stays, so the run loses only whether a class lies inside that component (`in_component`). Where the value of any other flag holds such a character, run nothing: print `weakness-classes: not run (an argument holds a character the skill does not pass)`, and no path.
3. **The shape.** The verb is `classes` or `across`. `classes` takes `--repo`, `--component`, `--origin`, `--prd-key` and `--today`, and `across` takes `--ref` and `--today`; a flag may repeat. Where the verb or a flag is any other — `--specs` among them, which the skill adds itself — or nothing stands between a flag and the next ` --` or the argument's end, run nothing: print `weakness-classes: not run (usage: an unknown verb or flag, or a flag without its value)`, the line the script prints for the same mistake, and no path.

No line you print ever holds a value that failed.

## The call

Make one Bash call, with a timeout of 600000 ms:

```bash
if out=$(TMPDIR="<scratchpad>" command mktemp -t dw-weakness-classes-XXXXXX.json 2>/dev/null); then
  err=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/weakness-classes.py" <verb> --specs "${SPECS_PATH-}" <flags> 2>&1 > "$out"); code=$?
  if [ "$code" -eq 0 ]; then printf '%s\n' "$out"
  else
    command rm -f -- "$out"
    case "$err" in
      'weakness-classes: not run ('*) printf '%s\n' "${err%%$'\n'*}" ;;
      *) printf 'weakness-classes: not run (the script exited %s)\n' "$code" ;;
    esac
  fi
else
  echo 'weakness-classes: not run (no temporary file could be made)'
fi
```

- `<verb>` is the argument's verb. `<flags>` is each flag the rule kept, in the argument's order, each followed by its value between single quotes: `--repo 'api' --component 'api:src/orders'`. A value the rule passed holds no quote, so it cannot leave its quotes.
- `<scratchpad>` is the scratchpad directory your session names. Where it names none, or one that does not exist, drop `TMPDIR="<scratchpad>" ` and run `command mktemp` as written — `workflows-core:run-flags` §7, stated here so you read nothing more.
- Where your run took `$SPECS_PATH` from an answer rather than from the environment, open the call with `export SPECS_PATH='<the value>';`, as `specs-git` does.

## What it prints

The skill's result is one line — the one line the call printed, or the argument rule's refusal — and you print it, verbatim, as your last line.

- **A path**, where the script exited 0: the JSON file's absolute path, holding §7.4's object for `classes` or §7.5's for `across`. Hand it on, or read its fields. The file is never edited and never removed.
- **A line beginning `weakness-classes: not run (`**, on every other outcome, the argument rule's refusals included. No file is left, and you print no path. This line is the skill's error that a caller's report line quotes. It is the script's own stderr line only where that line begins so; any other text the script wrote — a traceback, a warning — is never printed, and an exit other than 0 is a failure whatever its stdout held.

Where the call prints nothing — the harness stopped it at its timeout — print `weakness-classes: not run (the call did not finish)`, and no path.

## What a failure line means

So that a caller can say why it went without the classes. Each line names a flag, never its value; the script's other lines are in §7.4's and §7.5's tables.

| The line's `(…)` | What it means |
|---|---|
| `an argument holds a character the skill does not pass` | a value other than a `--component`'s holds a character outside the class above; nothing ran |
| `usage: an unknown verb or flag, or a flag without its value` | from the skill, as its step 3 says; from the script, a value opening with `-`, which it can read as a flag |
| `--repo is not a repository slug` | a `--repo` holds a `:`, `/`, `@`, `+` or `=`, is empty, or is `.` or `..` |
| `--component names a repository no --repo names` | a `--component`'s id, or its part before the first `:`, is no `--repo` |
| `--specs is not a directory` | `$SPECS_PATH` is unset or empty, or names no directory |
| `--specs is not the top level of a git work tree` | `across` only: `$SPECS_PATH` is a directory inside the specs repository rather than its top level, or git refuses the repository — `safe.directory`'s refusal of one another user owns among them |
| `--ref is not a plain ref name` | `across` only: the ref holds a `:` or `=`, or opens with `.`, `/`, `@` or `+`, so a default branch named with `=` cannot be read. One named with `#`, `,` or any other character outside the class is refused by the skill first |
| `--ref names no commit in --specs` | `across` only: the ref names no commit in the specs repository |
| `the script exited <code>` | the script exited other than 0 without a line of its own |
| `no temporary file could be made` | `mktemp` failed; the script did not run |
