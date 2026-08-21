<!-- dts:no-lint -->

# DTS scope and precedence

## Layers

A later layer overrides an earlier one. DTS defines layers 0 and 1 only.

| Layer | Content                                            | Source                      |
| ----- | -------------------------------------------------- | --------------------------- |
| 0     | Core rules, genre-neutral                          | DTS                         |
| 1     | Agent-surface rules, terminal-tuned                | DTS                         |
| 2     | Overlays: genre routing, domain terms, house style | the operator's memory file  |
| 3     | Per-file marker                                    | the file itself             |
| 4     | A direct instruction in conversation               | final, overrides everything |

## Layer 0 against layer 1

Apply layer 0 to any English. Drop layer 1 when a marker or an overlay calls for it.

| Layer 0 — core                     | Layer 1 — agent surface                 |
| ---------------------------------- | --------------------------------------- |
| Delete filler and dead phrases     | Sentence caps of 15 and 20 words        |
| Active voice, simple tense         | Modals limited to `can`, `will`, `must` |
| One word, one meaning              | Bullets and tables over prose           |
| Reproduce technical spans verbatim | Answer first, no preamble               |
| No hedge stacks                    | Seven-row cap on lists                  |

## Stop conditions

Do not apply DTS to these. Read the operator's overlay to find the handler that owns the genre, then name that handler in the reply.

| Genre                                         | Reason                                                                                                | Fall back to |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------ |
| Thesis, paper, journal article                | Hedging is a genre requirement. `may indicate` carries a claim strength that `can indicate` destroys. | layer 0      |
| Essay, long-form nonfiction                   | Rhythm and paragraph flow are the form                                                                | layer 0      |
| Legal and contract text                       | Precision comes from defined terms and long qualified clauses                                         | stop         |
| Grant and funding proposals                   | Persuasion, not instruction                                                                           | stop         |
| Brand, marketing, persuasive copy             | The rules delete persuasion                                                                           | stop         |
| Fiction                                       | Voice is the point                                                                                    | stop         |
| Any language other than English               | Different grammar, different conventions                                                              | stop         |
| String literals, test fixtures, asserted text | Rewriting breaks the test                                                                             | never touch  |

## Markers

Honor a marker found anywhere in a file. It governs that file alone and overrides layers 0 through 2.

| Marker              | Effect              |
| ------------------- | ------------------- |
| `<!-- dts:core -->` | Apply layer 0 only. |
| `<!-- dts:off -->`  | Apply nothing.      |

A source file carries the marker in that language's comment syntax.

## Reading an overlay

An overlay is free text in the operator's memory file, outside the `dts:start` and `dts:end` markers. Two forms carry weight.

Genre routing names the handler that replaces DTS:

```
- Spanish text: DTS does not apply. Use the `spanish-prose` skill.
```

A named override changes one rule and says which:

```
- Unlike DTS, in this repo descriptive sentences run to 30 words.
```

Honor a named override. Treat a contradiction that names no rule as ambiguous, and ask which one wins.

## Local edits to the standard

The operator can extend two things in [`wordlist.md`](wordlist.md): the canonical-word table and the kill-list. Treat an edited copy as authoritative. The caps and the modal list are not per-document settings, so read a marker instead of assuming a local change.
