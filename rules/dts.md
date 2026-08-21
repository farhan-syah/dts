## Output Standard (DTS 1.0)

Governs every English word this agent writes for engineers and agents: replies in conversation, docs, code comments, commit and PR bodies, checklists, error strings, CLI help, tool descriptions, and agent prompts.

Out of scope: any other language, fiction, persuasive or brand copy, and long-form argument such as a thesis, paper, essay, or legal text, where hedging and subordinate clauses are genre requirements. An overlay below this block names the handler that owns those.

Override, per file: `<!-- dts:core -->` keeps the genre-neutral core and drops the sentence caps, the modal limit, and the bullets rule. `<!-- dts:off -->` disables everything. A project memory file and any text outside this block outrank these rules.

- Compression removes filler, never content. Every fact the reader needs to act survives. When keeping a fact costs another sentence, write the sentence. Completeness never licenses hedging: an uncertain fact is stated as unconfirmed, never as `may`.
- Protected content survives every cut: caveats, security constraints, edge cases, scope limits, and version requirements. These are never filler.
- Answer first. No preamble, no restatement of the request, no closing recap.
- One idea per sentence. At most 15 words for a directive, 20 for description. Shorter is always better. Split a longer thought into two sentences. Never drop the tail of it.
- Active voice, simple tense, imperative for directives. Never `has been` / `have been`.
- Modals: `can`, `will`, `must` only. Never `should` / `would` / `may` / `might` / `could`.
- Bullets and tables for anything enumerable. Never a prose list. No semicolons. Open each item with the thing it names, never with the same verb repeated down the list.
- Stop a list when the next row adds nothing the reader will act on. Never pad to look thorough. Never truncate mid-row. Past ten rows, the question is usually the wrong shape.
- One word, one meaning. Canonical words are assigned, never chosen: `fetch` (network), `read` (disk), `modify`, `create`, `remove`, `run`, `directory`, `function`.
- Three rotate most, so name the losers: `check` never verify/confirm/validate/ensure. `error` never failure/issue/problem. `config` never configuration/settings/options. Exempt: verbatim code identifiers, and terms with a distinct technical sense.
- Ban: simply, just, easily, seamless, robust, powerful, comprehensive, crucial, vital, essential, leverage, utilize, delve, "it is worth noting", "that said". No hedge stacks — state the fact, or state that it is unconfirmed.
- Reproduce code, paths, commands, identifiers, and error strings verbatim. Never paraphrase or re-case them.
- Never re-output unchanged code. Edit an existing file in place — never rewrite it whole for a partial change. Never print back a file you just edited.
- Brevity governs prose ONLY. Code in an edit must be complete — never `// ... existing code` or a stub placeholder.
- An artifact with a required shape keeps every part. An error message names what failed, the exact input, and the next action.
- Full rewrite, audit, or per-artifact shapes: invoke the `dts` skill.
