# DTS — Dense Technical Syntax

An always-on output policy for coding agents.

Your agent writes too much. This makes it write less everywhere it writes — replies, commit messages, PR bodies, code comments, docs, error strings — from one install, with nothing to invoke and nothing to remember.

**Across the three model setups measured here, it cut output tokens 12% to 83% and held 96% to 101% of the judge score.**

Three setups are not a law. Every number ships with the benchmark that produced it. Run it on your own model.

## How it is built

| Layer                      | Loaded     | Cost                        | Owns                                    |
| -------------------------- | ---------- | --------------------------- | --------------------------------------- |
| [Core rules](rules/dts.md) | every turn | ~1000 input tokens, cached  | every surface, always                   |
| [Skill](skills/dts/)       | on demand  | nothing until called        | full spec, audits, per-artifact shapes  |
| [Your overlays](overlays/) | every turn | yours                       | domain exceptions, other languages      |

The core is small enough to leave on. Depth sits in the skill, which costs nothing until something calls it. Your exceptions sit in an overlay the installer never touches.

That split is the point. A standard you have to invoke is a standard you forget.

## Why this exists

Cutting tokens has meant choosing between two bad deals.

### 1. Simple, but worse output

Paste "explain like I'm five" into your config. You are done in a minute.

Your agent then scores 14.5 out of 20. It drops a third of the facts you asked for.

ASD-STE100 does better at 17.8. But it writes `the ampersand symbol` where an engineer needed `&`.

### 2. Good output, but real setup

Caveman ships twenty skills.

Its main skill tightens conversation, then exempts everything else on purpose:

> Persisted outside chat: write normal prose — code, comments, commits, docs, issue/PR/MR text, memory files.

So your commit messages stay long until you remember `caveman-commit`. Your docs stay long until you remember `caveman-compress`.

Whatever you forget stays full length.

### DTS takes the first deal and removes the cost

| Approach   | Setup           | Judge /20 | Covers your docs and commits |
| ---------- | --------------- | ----------- | ---------------------------- |
| ELI5       | one prompt      | 14.5        | yes                          |
| ASD-STE100 | one prompt      | 17.8        | yes                          |
| Caveman    | twenty skills   | 17.9        | only when you invoke them    |
| **DTS**    | **one install** | **18.8**    | **yes, always**              |

**Want fine control, per-task skills, and intensity levels?** Use [Caveman](https://github.com/JuliusBrussee/caveman).

It is a good tool making a different bet: that you want to steer. On Claude Opus it is also about 5-7% cheaper than DTS on raw tokens.

It depends, if you want that final 5-7% for reduced quality.

## Install

```sh
git clone https://github.com/farhan-syah/dts
cd dts
./install.sh
```

It finds every agent on your PATH and installs into each.

| Agent       | Skill | Rules | Output style |
| ----------- | ----- | ----- | ------------ |
| Claude Code | yes   | yes   | yes          |
| Codex       | yes   | yes   | —            |
| opencode    | yes   | yes   | —            |
| pi          | yes   | yes   | —            |
| Gemini CLI  | —     | yes   | —            |

On Claude Code, turn on the output style: `/config`, then Output style, then DTS.

```sh
./install.sh --list        # what it found, and where it will write
./install.sh --dry-run     # show every change, touch nothing
./install.sh --only codex  # one agent
./install.sh --uninstall   # remove it cleanly
```

**Your memory file is safe.** The rules go between `<!-- dts:start -->` and `<!-- dts:end -->`. Nothing outside those markers is read or changed, so your own notes survive every reinstall.

The skill also installs through the Agent Skills tool:

```sh
npx skills add farhan-syah/dts
```

### Any other agent

If your agent is not in the table, it almost certainly reads a global instructions file. Copy this into it:

<!-- dts:readme-start -->

```markdown
<!-- dts:start -->
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
<!-- dts:end -->
```

<!-- dts:readme-end -->

Append it to whichever file your agent loads. `./install.sh --print` writes the same block to stdout if you would rather pipe it.

| Agent         | File                           |
| ------------- | ------------------------------ |
| Claude Code   | `~/.claude/CLAUDE.md`          |
| Codex         | `~/.codex/AGENTS.md`           |
| opencode      | `~/.config/opencode/AGENTS.md` |
| pi            | `~/.pi/agent/AGENTS.md`        |
| Gemini CLI    | `~/.gemini/GEMINI.md`          |
| anything else | its global instructions file   |

There is no shared file across agents. Each reads its own path, so the block goes in each one you use.

**Keep the `<!-- dts:start -->` and `<!-- dts:end -->` markers.** A later `./install.sh` updates the text between them in place. Without them you get a second copy, and the two drift apart.

Everything you write outside the markers is yours. The installer never reads it.

Only Claude Code has an output style. Every other agent gets the same rules through its instructions file, which covers replies as well as files.

## What you save

Savings depend on your model. In the three setups below, quality held.

| Your setup                  | Before      | After | Saved    | Quality kept |
| --------------------------- | ----------- | ----- | -------- | ------------ |
| glm-5.2                     | 1001 tokens | 171   | **-83%** | 96%          |
| Claude Opus, in Claude Code | 926         | 743   | **-20%** | **101%**     |
| Claude Opus, bare model     | 735         | 645   | **-12%** | 98%          |

A standard removes padding. It cannot remove padding your model never wrote.

Ask glm-5.2 to explain processes and threads. It opens with a house-and-tenant analogy, a "here is the breakdown" line, then numbered headings.

Ask Opus the same thing. You get a one-line definition, a table, and nothing else.

Both answers score 20 out of 20. Opus needs 485 tokens where glm needs 853, so DTS finds far less to cut.

Expect the high end on a smaller or older model. Expect the low end on a frontier model that already writes tightly.

Anyone who gives one number for every model has measured one model. Measure yours.

## How it compares

One model wrote 320 answers across 5 arms. A different model graded them on 4 things. 64 answers per arm.

Every rival is the real thing people install, copied word for word: [Caveman](https://github.com/JuliusBrussee/caveman) and [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish). Versions are in [`bench/arms/PROVENANCE.md`](bench/arms/PROVENANCE.md).

| Standard    | Tokens  | vs baseline | English /5 | Judge /20 | Cost per point | False claims |
| ----------- | ------- | ----------- | ---------- | ----------- | ---------------------- | -------------- |
| No standard | 1001    | —           | 5.00       | 19.45       | 51.5                   | 0.53           |
| **DTS**     | **171** | **-83%**    | **5.00**   | **18.77**   | **9.1**                | **0.23**       |
| Caveman     | 212     | -79%        | 4.27       | 17.94       | 11.8                   | 0.34           |
| ASD-STE100  | 187     | -81%        | 4.97       | 17.80       | 10.5                   | 0.27           |
| ELI5        | 169     | -83%        | 4.69       | 14.48       | 11.7                   | 0.66           |

Two results stand out.

**The English stays perfect.** 5.00, same as an agent with no rules at all. Caveman drops to 4.27 because it writes fragments.

**It invents less per answer.** 0.23 false claims against the baseline's 0.53.

Read that one carefully. A shorter answer makes fewer claims, so it has fewer chances to be wrong. The count alone cannot separate "more careful" from "said less". [`report.py`](bench/report.py) also prints false claims per 1000 words and the share of answers holding at least one, which do separate them. Both are in the run output, not in this table, because no frozen run currently backs them.

It loses on one thing: completeness, 4.23 against Caveman's 4.36. Caveman keeps a little more because it caps nothing.

### Did the rules actually get followed

Token counts show what an answer cost. They do not show whether your agent followed the rules or just got shorter. [`bench/lint.py`](bench/lint.py) counts rule breaks per 100 words.

| Standard    | Rule breaks per 100 words |
| ----------- | ------------------------- |
| ASD-STE100  | 0.10                      |
| **DTS**     | **0.13**                  |
| Caveman     | 0.41                      |
| ELI5        | 0.72                      |
| No standard | 1.45                      |

ASD-STE100 wins this and loses the benchmark. It obeys its own rules slightly better and still scores 17.80 against 18.77. Obedience is not the point.

## Why not just use ASD-STE100

[ASD-STE100](https://asd-ste100.org) is the aerospace writing standard. Its grammar rules are excellent.

Its dictionary is the problem. It bans common verbs, so `check the config` becomes `do a check of the config`.

That costs tokens and strips out the words an engineer needs.

DTS keeps the grammar and drops the dictionary.

Asked to explain a Rust move error, ASD-STE100 produced:

> If you pass a reference, use the ampersand symbol before the variable name.

`the ampersand symbol` instead of `&`, and no code block at all. Correct English, useless to a programmer.

## The rules

15 rules, in [`rules/dts.md`](rules/dts.md). The short version:

- Cut filler, never content. Every fact the reader needs survives.
- Answer first. No preamble, no repeating the question, no recap at the end.
- One idea per sentence. 15 words for an instruction, 20 for an explanation. Shorter is better.
- Active voice. Simple tense.
- Only `can`, `will`, `must`. No `should`, `would`, `may`, `might`, `could`.
- Lists and tables for anything countable. Stop when the next row adds nothing.
- One word per idea. The word is fixed, not chosen fresh each time.
- Code, paths, and error messages are copied exactly.
- Short prose only. Code is always complete, never `// ... existing code`.

## What ships

| Path                                           | What it is                                             |
| ---------------------------------------------- | ------------------------------------------------------ |
| [`rules/dts.md`](rules/dts.md)                 | The always-on rules. Goes in your agent's memory file. |
| [`skills/dts/`](skills/dts/)                   | The full spec. Costs nothing until something calls it. |
| [`output-styles/dts.md`](output-styles/dts.md) | Chat style, Claude Code only.                          |
| [`overlays/`](overlays/)                       | Templates for adding your own rules.                   |
| [`bench/`](bench/)                             | The benchmark.                                         |
| [`tests/`](tests/)                             | Unit tests. `python3 -m unittest discover -s tests`    |

## Turning it off, and adding your own rules

DTS covers English technical writing. It stops there.

Out of scope: other languages, fiction, marketing copy, and long-form argument like a thesis or a contract, where hedging and long sentences are part of the job.

Switch it off for one file with a marker:

| Marker              | Effect                                                       |
| ------------------- | ------------------------------------------------------------ |
| `<!-- dts:core -->` | Keeps the safe basics. Drops the word limits and list rules. |
| `<!-- dts:off -->`  | Nothing applies.                                             |

Add your own rules below the DTS block in your memory file. The installer never touches them.

```
### My overlays
- Spanish text: DTS does not apply. Use my `spanish-prose` skill.
- Unlike DTS, in this repo sentences run to 30 words.
- Also fixed here: `endpoint`, never route or path or URL.
```

Say which rule you are changing. A silent contradiction reads as a mistake. [`overlays/README.md`](overlays/README.md) walks through it.

## Running the benchmark

Python 3.11 or newer. Nothing to install.

```sh
cd bench
./providers.py       # which models you can reach
./bench.py --list    # arms, models, and the 32 prompts
./runall.sh --dry    # show the plan
./runall.sh          # run it
```

Models are written `provider:model`:

```sh
./bench.py --model ollama:kimi-k3:cloud --cats debug --reps 3 --out out/x.json
./judge.py out/x.json --judge-model anthropic:claude-sonnet-5
./report.py out/x-judged.json --by-cat
./lint.py --results out/x.json
```

Providers live in [`bench/config.toml`](bench/config.toml). Three protocols cover almost everything.

| Protocol    | Reaches                                                       |
| ----------- | ------------------------------------------------------------- |
| `ollama`    | local and Ollama Cloud                                        |
| `openai`    | OpenAI, DeepSeek, Groq, Together, OpenRouter, vLLM, LM Studio |
| `anthropic` | Claude                                                        |

Adding a provider is a config entry, never a code change. Keys come from environment variables, never from the file.

**Claude Code users need no API key.** The `claude` provider runs your local CLI against your subscription.

## How quality is measured

Saving tokens proves nothing on its own. An empty answer saves 100%.

So four things are measured together.

| Measure            | Catches                                                        |
| ------------------ | -------------------------------------------------------------- |
| Output tokens      | What it cost                                                   |
| Fact coverage      | Whether the needed content survived                            |
| A judge, on 4 axes | correct, complete, usable, english                             |
| Lint               | Whether the rules were followed, or the agent just got shorter |

The `english` axis matters most. Every ratio metric favours telegraphic output until you check whether it is still a sentence.

No model ever grades its own writing. Self-preference inflated one arm by roughly 40% in an early run.

## What this does not prove

- Savings are not a property of the standard alone. They come from the standard, your model, and your harness together. Treat any single number, including the ones here, as one setup measured once.
- The comparison used one writer model, glm-5.2. Two Claude Opus setups were added separately. Three setups show savings vary. They cannot predict a fourth.
- The judges are language models. They are told that length is not quality, and two independent judges agreed on the ranking, but they are not people.
- No confidence interval is reported, so a small gap is not a result. DTS scores 18.77 against Caveman's 17.94. That 0.83 is one judge model's mean over 64 answers. It has not been shown to exceed judge noise. The gap against ELI5 is 4.29 and is not in doubt.
- Raw answers are not committed. `out/` is regenerable and stays out of the repo, so the tables here cannot be audited without rerunning against the same model version. Rerun before citing them.
- The lint is regular expressions. It cannot see passive voice or parts of speech, so it undercounts.
- 64 answers per arm, temperature 0.2, no runaway answers. An earlier 32-answer run was decided by a single answer that hit the token ceiling. Treat any single-run result as undecided.

## License

MIT. See [LICENSE](LICENSE).
