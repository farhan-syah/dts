<!-- dts:no-lint -->

# DTS grammar

## Sentence caps

| Text type             | Ceiling  | Form                   |
| --------------------- | -------- | ---------------------- |
| Directive (do this)   | 15 words | Command form           |
| Descriptive (this is) | 20 words | Simple present or past |

These are ceilings, never targets. Shorter is always better.

A thought that exceeds the ceiling becomes two sentences. It never becomes a truncated sentence.

Code spans in backticks, paths, hyphenated terms, and numbers with units each count as one word.

## Rules

0. **Compression removes filler, never content.** Every fact the reader needs to act survives. When keeping a fact costs another sentence, write the sentence. Being complete is never a reason to hedge: state an uncertain fact as unconfirmed, never as `may`.
1. **One idea per sentence.** Two ideas means two sentences.
2. **Answer first.** Conclusion in sentence one. Reasons come after.
3. **Condition before command.** Write `If the build fails, run cargo clean.` Never `Run cargo clean if the build fails.`
4. **Name who does the thing.** `The parser rejects null.` Not `Null is rejected.`
5. **Plain present tense.** No `has been`, `have been`, `was being`, `is to be`.
6. **Modals: `can`, `will`, `must`.** Never `should`, `would`, `may`, `might`, `could`. A rule becomes `must`. A capability becomes `can`. A suggestion becomes a plain statement of fact.
7. **No semicolons.** Write two sentences.
8. **No `-ing` chains.** `...ran the test, causing a panic` becomes two sentences.
9. **Noun clusters: three words maximum.** Break longer ones with `of` or a verb.
10. **Bullets and tables for enumerations.** A prose sentence listing four things is four bullets. Stop a list when the next row adds nothing the reader will act on. Never pad to look thorough, never truncate mid-row. Open each item with the thing it names, never with one verb repeated down the list.
11. **One word, one meaning.** Reuse the exact term for a concept across the whole document. Synonym rotation forces the reader to re-derive the mapping.
12. **Prefer the plain word.** Keep a technical term when it is exact and the reader already uses it. `mutex` stays. `orthogonal` becomes `unrelated`. A word chosen to sound expert costs the reader and buys nothing.
13. **Say it straight.** No analogy, no clever one-liner, no `not X, but Y`. An inverted sentence reads as insight and costs the reader a second pass.
14. **Verbatim technical spans.** Code, paths, commands, flags, identifiers, error strings, product and API names, UI labels: character-exact. A rule never rewrites one of these.

## Locked action verbs

One verb per action, everywhere. No synonyms.

| Verb     | Meaning                               |
| -------- | ------------------------------------- |
| `Fetch`  | Retrieve data across a network or API |
| `Read`   | Read a local file from disk           |
| `Modify` | Edit existing code, config, or docs   |
| `Create` | Make a new file, resource, or entity  |
| `Remove` | Delete an existing file or entity     |
| `Run`    | Execute a command or test             |

## What DTS rejects from ASD-STE100

These STE rules inflate tokens and are **not** part of DTS:

- The ~900-word approved dictionary. Software vocabulary is legal.
- Verb-to-noun expansion (`check` → `do a check of`). Direct verbs stay.
- `ensure` → `make sure that`. `ensure` stays.
- The contraction ban. Contractions are legal and cheaper.
- `e.g.` → `for example`, `i.e.` → `that is`. The abbreviations stay.
- Mandatory restoration of every article and `that` clause.
