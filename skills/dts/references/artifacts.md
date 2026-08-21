# DTS per-artifact shapes

## Commit body

Subject: imperative, 50 characters, no trailing period. Body: bullets, one change per bullet, each naming the file or symbol. No narrative of the work session. No `this commit`, no `we`, no tool attribution.

## PR body

Three headings maximum: what changed, why, how to check it. Each bullet names a path. Never restate the diff line by line.

## README and docs

Open with what the thing is and who runs it, in one sentence under 20 words. Every command in a fenced block, copy-pasteable, no leading `$`. Options in a table, never in prose. No feature adjectives — give the measurable fact.

## Code comment

Comment the non-obvious only: business rule, invariant, why-not-the-obvious-way, or a link to the tracked error. Never restate the syntax on the next line. One line where one line does.

## Error message

Three parts, in order: what failed, the exact input or path, the next action.

`Config parse failed at ~/.foo/config.toml:12 — expected string, found int. Quote the value.`

No apology, no `Oops`, no `Something went wrong`.

## CLI help

One line per flag. Start with the verb. Show the default in parentheses. Cap at 70 characters so it never wraps.

## Subagent prompts and tool descriptions

This is the highest-value target. Another model parses these with no human present to resolve ambiguity.

- Imperative. One instruction per sentence. 15 words.
- Name every path, symbol, and file explicitly. No `the relevant file`.
- State the return contract first: what shape the answer must take.
- State the hard constraints as `must` and `never`, not as preferences.
- No background narrative the agent cannot act on.

## Structured output schemas

For `Workflow` and subagent `schema` objects, short keys cut generation tokens because every key is regenerated per record. Use single-word or single-character keys and map them back in the caller.

| Verbose              | Dense |
| -------------------- | ----- |
| `status`             | `s`   |
| `error_type`         | `e`   |
| `file_path`          | `f`   |
| `line_number`        | `l`   |
| `recommended_action` | `a`   |
| `result`             | `r`   |

This applies only to schemas you define. Tool schemas built into your harness are fixed and must not be renamed.

## Checklists under `.claude/prep/`

One line per item. Start with a locked action verb. State done-ness with `[x]` only, never with a prose status note.
