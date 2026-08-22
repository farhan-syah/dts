# DTS — Dense Technical Syntax

An always-on output policy for coding agents.

Your agent writes too much. This makes it write less everywhere it writes — replies, commit messages, PR bodies, code comments, docs, error strings — from one install, with nothing to invoke and nothing to remember.

**In conversation it cut output tokens 12% to 83% and held 96% to 101% of the judge score. Inside an agent loop it writes 14% less prose and costs nothing extra.**

Those are two different surfaces with two different answers. Every number ships with the benchmark that produced it. Run both on your own model.

## How it is built

| Layer                      | Loaded     | Cost                       | Owns                                   |
| -------------------------- | ---------- | -------------------------- | -------------------------------------- |
| [Core rules](rules/dts.md) | every turn | ~1000 input tokens, cached | every surface, always                  |
| [Skill](skills/dts/)       | on demand  | nothing until called       | full spec, audits, per-artifact shapes |
| [Your overlays](overlays/) | every turn | yours                      | domain exceptions, other languages     |

The core is small enough to leave on. Depth sits in the skill, which costs nothing until something calls it. Your exceptions sit in an overlay the installer never touches.

That split is the point. A standard you have to invoke is a standard you forget.

## Why this exists

Cutting tokens has meant choosing between two bad deals.

### 1. Simple, but worse output

Paste "explain like I'm five" into your config. You are done in a minute.

Your agent then scores 14.3 out of 20. It drops a third of the facts you asked for.

ASD-STE100 does better at 17.9. But it writes `the ampersand symbol` where an engineer needed `&`.

### 2. Good output, but real setup

Caveman ships twenty skills. Its main skill tightens conversation, then exempts everything else on purpose:

> Persisted outside chat: write normal prose — code, comments, commits, docs, issue/PR/MR text, memory files.

So your commit messages stay long until you remember `caveman-commit`. Whatever you forget stays full length.

### DTS takes the first deal and removes the cost

| Approach   | Setup           | Judge /20 | Covers your docs and commits |
| ---------- | --------------- | --------- | ---------------------------- |
| ELI5       | one prompt      | 14.3      | yes                          |
| Caveman    | twenty skills   | 17.1      | only when you invoke them    |
| ASD-STE100 | one prompt      | 17.9      | yes                          |
| **DTS**    | **one install** | **18.7**  | **yes, always**              |

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

It writes to each agent's global file, so DTS applies in every project.

| Agent       | Skill | Rules | Output style |
| ----------- | ----- | ----- | ------------ |
| Claude Code | yes   | yes   | yes          |
| Codex       | yes   | yes   | —            |
| opencode    | yes   | yes   | —            |
| pi          | yes   | yes   | —            |
| Gemini CLI  | —     | yes   | —            |
| Copilot CLI | —     | yes   | —            |
| Amp         | —     | yes   | —            |
| Kiro        | —     | yes   | —            |

On Claude Code, turn on the output style: `/config`, then Output style, then DTS.

```sh
./install.sh --list        # what it found, and where it will write
./install.sh --dry-run     # show every change, touch nothing
./install.sh --only codex  # one agent
./install.sh --uninstall   # remove it cleanly
```

### Editors that read rules from the repo

Cursor, Windsurf, Cline, Qoder and Kiro keep their rules inside the project. Zed, Amp, Jules, Junie, Antigravity and CodeWhale read `AGENTS.md` from the repo root.

```sh
./install.sh --project           # write into the current repo
./install.sh --project ~/code/x  # or another one
./install.sh --project --all     # every target, not only the ones detected
```

It writes `AGENTS.md` always, and a rule file for each editor the repo already uses:

| Editor   | File                              |
| -------- | --------------------------------- |
| Cursor   | `.cursor/rules/dts.mdc`           |
| Windsurf | `.windsurf/rules/dts.md`          |
| Cline    | `.clinerules/dts.md`              |
| Qoder    | `.qoder/rules/dts.md`             |
| Kiro     | `.kiro/steering/dts.md`           |
| Copilot  | `.github/copilot-instructions.md` |

Without `--all` it skips any editor whose directory is absent, so a repo does not collect rule files for editors nobody there runs. The Cursor file gets `alwaysApply: true` so it loads unprompted.

DTS is plain text with no runtime. That is why one file covers every agent above, and why nothing here needs Node, a plugin host, or a hook.

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

Two surfaces, two answers. Do not carry a number from one to the other.

### In conversation

Savings depend on your model. In the three setups below, quality held.

| Your setup                  | Before      | After | Saved    | Quality kept |
| --------------------------- | ----------- | ----- | -------- | ------------ |
| glm-5.2                     | 1076 tokens | 190   | **-82%** | 96%          |
| Claude Opus, in Claude Code | 926         | 743   | **-20%** | **101%**     |
| Claude Opus, bare model     | 735         | 645   | **-12%** | 98%          |

A standard removes padding. It cannot remove padding your model never wrote.

Ask glm-5.2 to explain processes and threads. It opens with a house-and-tenant analogy, a "here is the breakdown" line, then numbered headings.

Ask Opus the same thing. You get a one-line definition, a table, and nothing else.

Both answers score 20 out of 20. Opus needs 485 tokens where glm needs 853, so DTS finds far less to cut.

Expect the high end on a smaller or older model. Expect the low end on a frontier model that already writes tightly.

Anyone who gives one number for every model has measured one model. Measure yours.

### Inside an agent loop

A coding agent reads far more than it writes. Across 48 paired sessions on a real repository, every prose measure moved and the bill did not.

| Measure         | Baseline | DTS    | Change     | 95% CI           |
| --------------- | -------- | ------ | ---------- | ---------------- |
| Prose written   | 2021 ch  | 1747   | **-13.6%** | [-23.8%, -4.3%]  |
| Cost            | $0.0880  | 0.0874 | -0.7%      | [-6.5%, +4.6%]   |
| Turns           | 6.9      | 6.6    | -4.5%      | [-12.0%, +2.1%]  |
| Tasks completed | 12/12    | 12/12  | —          | —                |

**Output tokens are 0.9% of the tokens in an agent session.** There are 102 tokens read for every one written. Compressing what the agent says cannot move a bill dominated by what it reads, however hard you compress.

So DTS makes an agent write shorter, and charges you nothing for it. That second half is not free elsewhere: Caveman on the same harness cut output tokens 31.5% and moved cost `+9.6%`.

Expect the conversation numbers where you talk to the model. Expect these where it works on your code.

## How it compares

One model wrote 384 answers across 6 arms. **Two** other models graded every one. 64 answers per arm. This section is the conversational benchmark; the agent-loop numbers are above.

Every rival is the real thing people install, copied word for word: [Caveman](https://github.com/JuliusBrussee/caveman), [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), [ponytail](https://github.com/DietrichGebert/ponytail). Versions are in [`bench/arms/PROVENANCE.md`](bench/arms/PROVENANCE.md).

| Standard    | Median tokens | vs baseline | English /5 | Judge /20 |
| ----------- | ------------- | ----------- | ---------- | --------- |
| No standard | 1076          | —           | 5.00       | 19.58     |
| **DTS**     | **190**       | **-82%**    | **5.00**   | **18.74** |
| ponytail    | 210           | -81%        | 4.97       | 18.59     |
| ASD-STE100  | 172           | -84%        | 5.00       | 17.90     |
| Caveman     | 150           | -86%        | 3.80       | 17.12     |
| ELI5        | 158           | -85%        | 4.40       | 14.33     |

**Which gaps are real.** Both judges scored every answer. A paired bootstrap over the same prompts gives:

| Comparison        | Difference | 95% CI         | Verdict               |
| ----------------- | ---------- | -------------- | --------------------- |
| DTS vs ELI5       | +4.43      | [+3.71, +5.18] | real                  |
| DTS vs Caveman    | +1.60      | [+1.06, +2.17] | real                  |
| DTS vs ASD-STE100 | +0.83      | [+0.40, +1.24] | real                  |
| DTS vs ponytail   | +0.17      | [-0.29, +0.65] | **too close to call** |

**The English stays perfect.** 5.00, same as no rules at all. Caveman drops to 3.80 because it writes fragments.

**ponytail is not a rival.** It governs the code an agent writes, not the prose, and its own skill description says not to use it for prose. It is here as a control showing the two do not overlap. Run both.

### Did the rules actually get followed

Token counts show what an answer cost. They do not show whether your agent followed the rules or just got shorter. [`bench/lint.py`](bench/lint.py) counts rule breaks per 100 words.

| Standard    | Rule breaks per 100 words |
| ----------- | ------------------------- |
| ASD-STE100  | 0.10                      |
| **DTS**     | **0.13**                  |
| Caveman     | 0.41                      |
| ELI5        | 0.72                      |
| No standard | 1.45                      |

ASD-STE100 wins this and loses the benchmark. It obeys its own rules slightly better and still scores 17.90 against 18.74. Obedience is not the point.

## Why not just use ASD-STE100

[ASD-STE100](https://asd-ste100.org) is the aerospace writing standard. Its grammar rules are excellent.

Its dictionary is the problem. It bans common verbs, so `check the config` becomes `do a check of the config`.

That costs tokens and strips out the words an engineer needs.

DTS keeps the grammar and drops the dictionary.

Asked to explain a Rust move error, ASD-STE100 produced:

> If you pass a reference, use the ampersand symbol before the variable name.

`the ampersand symbol` instead of `&`, and no code block at all. Correct English, useless to a programmer.

## The rules

15 rules, in [`rules/dts.md`](rules/dts.md). The full text is in the paste block above.

## What ships

| Path                                           | What it is                                             |
| ---------------------------------------------- | ------------------------------------------------------ |
| [`rules/dts.md`](rules/dts.md)                 | The always-on rules. Goes in your agent's memory file. |
| [`skills/dts/`](skills/dts/)                   | The full spec. Costs nothing until something calls it. |
| [`output-styles/dts.md`](output-styles/dts.md) | Chat style, Claude Code only.                          |
| [`overlays/`](overlays/)                       | Templates for adding your own rules.                   |
| [`bench/`](bench/)                             | The benchmark, conversational and agentic.             |
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

The agent-loop benchmark runs a headless Claude Code session per trial against a pinned real repository, and installs each arm the way you would, as a project memory file.

```sh
./agentic.py --list
./agentic.py --arms baseline dts --reps 4 --model haiku
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

No model ever grades its own writing, and two judges score every answer.

## What this does not prove

- Savings depend on your model and your harness, not on the standard alone. Treat every number here as one setup measured once, and run the benchmark on yours.
- One writer model was compared across all arms, plus two Claude Opus setups measured separately. Three setups cannot predict a fourth.
- The agent-loop numbers are one model on one repository across 8 prose-heavy tasks. No judge scored those answers, so they are shorter by measurement and equally correct only by task completion.
- The judges are language models, told that length is not quality. They are not people, and two of them agree exactly on 39% of answers. Gaps under about half a point are noise, which is why every comparison above carries an interval.
- The lint is regular expressions. It cannot see passive voice or parts of speech, so it undercounts.
- Raw answers are not committed. `out/` stays out of the repo, so these tables cannot be audited without rerunning against the same model version.

## License

MIT. See [LICENSE](LICENSE).
