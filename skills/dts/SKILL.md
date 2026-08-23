---
name: dts
description: Apply or audit DTS (Dense Technical Syntax), a standard for token-dense English. Use to write or rewrite any persisted text — READMEs, docs, code comments, commit and PR bodies, checklists, error messages, CLI help, tool descriptions, and agent prompts. Also use when asked to de-slop, tighten, compress, cut verbosity, reduce tokens, or apply STE / Simplified Technical English / ASD-STE100 / DOCS-26. NOT for another language, NOT for fiction, NOT for brand or marketing copy, NOT for long-form argument such as a thesis or legal text.
license: MIT
compatibility: claude-code codex opencode pi gemini-cli
metadata:
  standard: DTS
  spec_version: "0.1"
---

# DTS — Dense Technical Syntax

Apply these six to every passage. They cover the common case.

1. **Compression removes filler, never content.** Every fact the reader needs to act survives. When keeping a fact costs another sentence, write the sentence.
2. **Answer first.** No preamble, no question echo, no closing recap.
3. **One idea per sentence.** At most 15 words for a directive, 20 for description. Shorter is always better.
4. **Bullets and tables** for anything enumerable. Never a prose list. Stop a list when the next row adds nothing the reader will act on.
5. **Delete filler and hedge stacks.** State the fact, or state that it is unconfirmed.
6. **Reproduce technical spans verbatim.** Code, paths, commands, identifiers, and error strings stay character-exact.

Read [`references/grammar.md`](references/grammar.md) before rewriting a whole document. Run the audit in [`references/check.md`](references/check.md) before delivering one.

## Hard boundary

Brevity governs prose only. Code inside an edit stays complete, syntactically valid, and self-contained. Treat `// ... existing code` and stub placeholders as defects.

Never re-output unchanged code to confirm a change.

## Routing

Each row fires on what you are about to do. Read the file first, then write. A row that does not fire costs nothing.

| Trigger                                                                                          | Read                                                 |
| ------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| You are rewriting a whole document, or a passage the six rules above do not settle               | [`references/grammar.md`](references/grammar.md)     |
| You are cutting a word, collapsing a hedge, or picking between synonyms                          | [`references/wordlist.md`](references/wordlist.md)   |
| The target has a fixed shape: commit, PR, README, comment, error, CLI help, agent prompt, schema | [`references/artifacts.md`](references/artifacts.md) |
| You are about to deliver a persisted file                                                        | [`references/check.md`](references/check.md)         |
| The genre is out of scope, an overlay contradicts a rule, or the file opts out of DTS            | [`references/scope.md`](references/scope.md)         |

Two triggers can fire at once. Read both files.

An unrecognized request fires no row. Read [`references/grammar.md`](references/grammar.md) and apply it.

## Stop conditions

Do not apply DTS to any of these. Apply the operator's own handler instead, and say which one is running.

- Long-form argument: thesis, paper, essay, legal text, proposals. Hedging and subordinate clauses are genre requirements there.
- Any language other than English.
- Fiction and narrative prose.
- Brand, marketing, or persuasive copy.
- String literals, test fixtures, and any text asserted against in code.

DTS names no replacement, so read the operator's overlay to learn which handler owns the genre. When a prose skill and DTS both match, the prose skill wins for its language or genre.

A file can opt out of DTS, or keep the core and drop the terminal-tuned rules. The markers, the layer model, and precedence live in [`references/scope.md`](references/scope.md).

## Boundary

DTS owns structure and word choice in English technical prose. It does not own tone, persuasion, voice, or any other language. Leave those to whatever the operator has configured.
