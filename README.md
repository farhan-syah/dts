<h1 align="center">DTS — Dense Technical Syntax</h1>

<p align="center">
  <em>Makes your agent write shorter, without removing what you needed.</em>
</p>

<p align="center">
  <a href="#install"><b>Install</b></a> &middot;
  <a href="#before-and-after">See it</a> &middot;
  <a href="rules/dts.md">The rules</a> &middot;
  <a href="#how-it-compares">Numbers</a> &middot;
  <a href="EXAMPLES.md">Examples</a> &middot;
  <a href="MECHANISM.md">How it works</a> &middot;
  <a href="BENCHMARK.md">Method</a>
</p>

---

A writing standard for AI coding agents. It governs every surface the agent writes to — chat replies, commit messages, PR bodies, code comments, documentation, error strings — from one install, with nothing to invoke per task.

Agent output has grown more verbose with each model generation. The available remedies trade brevity against content: an "explain like I'm five" prompt drops about 30% of the facts in an answer, and ASD-STE100 keeps its content but does not shorten the output.

DTS is a prompt. Paste it into your agent's instructions file, or into a new chat, and it applies from the next message.

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

That is the whole standard. It works in a `CLAUDE.md`, an `AGENTS.md`, a Cursor rule, a `.clinerules` file, or pasted straight into a conversation.

Keep the two markers. A later install updates the text between them in place instead of adding a second copy.

### Or let the installer place it

```sh
git clone https://github.com/farhan-syah/dts && cd dts && ./install.sh
```

It finds every agent on your PATH and writes to each one's global file, so the standard applies in every project, to the main agent and to every subagent it delegates to. It also installs the skill and, on Claude Code, an output style.

---

## Before and after

Left column is real unedited Claude Opus 5 output. Right column is the same model with DTS as its system prompt. Nothing else loaded, nothing truncated.

<table>
<tr><th width="50%">README opening — 587 tokens</th><th width="50%">with DTS — 445 tokens</th></tr>
<tr>
<td valign="top">

> This tool streams tables out of a Postgres database and lands them in S3 as Parquet or CSV, reading in bounded chunks so that a hundred-gigabyte table costs about as much memory as a small one and nothing is staged on local disk. It is meant for the unglamorous middle of a data pipeline — nightly snapshots, one-off extracts for analysts, seeding a warehouse before a backfill — where what you want is a single command with a predictable output layout, not another long-running service to operate.

</td>
<td valign="top">

> This tool copies Postgres tables to S3 as Parquet or CSV files. Rows stream in fixed-size batches, so memory use stays flat no matter how large the table.

</td>
</tr>
<tr><th width="50%">Incident update — 830 tokens</th><th width="50%">with DTS — 128 tokens</th></tr>
<tr>
<td valign="top">

> Between 14:00 and 14:29 UTC today, approximately 12% of incoming requests failed, returning errors or timing out. The issue has been resolved and the service has been operating normally since 14:29. No data was lost, and requests that succeeded during the window were processed correctly.
>
> The trigger was a routine deploy that went out at 14:00. That change inadvertently removed the cache warmup step that runs as part of application startup, so the new instances came up with empty caches and passed traffic straight through to the primary datastore. The resulting load pushed query latency past our timeout thresholds, and a portion of requests began failing almost immediately. Because the failures were tied to cache misses rather than a hard outage, the impact was partial and intermittent rather than total, which is why most users saw only occasional errors while a smaller group hit them repeatedly.
>
> Our alerting fired within a few minutes of the deploy on elevated error rate. The on-call engineer correlated the spike with the 14:00 release, initiated a revert at 14:27, and the previous build was fully rolled out shortly after. Caches repopulated within about two minutes of the revert completing, and error rates returned to baseline by 14:29, giving a total impact window of 29 minutes.
>
> We are treating the root cause as a gap in our deploy validation rather than the change itself. The warmup step was removed without any check that would catch its absence, so we are adding a startup assertion that fails the deploy if warmup does not run, along with a canary stage that holds a small share of traffic long enough for cold-cache effects to surface before a full rollout. We are also reviewing our timeout and retry configuration, since the datastore was under strain but never unavailable, and better degradation behavior would have reduced the share of failed requests. A full postmortem will follow within the week, and we apologize for the disruption.

</td>
<td valign="top">

> Between 14:00 and 14:29 UTC, 12% of requests failed. A deploy at 14:00 removed the cache warmup step, so cold caches drove request timeouts. We reverted the deploy at 14:27, and error rates returned to baseline within two minutes. No data loss occurred. We are restoring the warmup step with a deploy-time check that blocks release if it is absent.

</td>
</tr>
</table>

87 words to 28, and 325 to 60. Both right-hand answers keep every fact the left one carries.

DTS does not always cut this hard. Asked for a database error message it saves only nine words, and uses them to name the exact config file and the command to run next. The goal is not a shorter answer. The goal is an answer with nothing wasted and nothing missing.

More examples, every standard, complete replies: [EXAMPLES.md](EXAMPLES.md).

---

## Why this exists

Four approaches are in common use. Each has a documented cost.

**ELI5 prompts.** A one-line config change, and the shortest path to a shorter agent. Fact retention falls to 70% and the judge score to 14.3 out of 20. The output is short because it carries less.

**[ASD-STE100](https://asd-ste100.org).** The aerospace controlled-language standard. Its grammar rules are sound and it retains 88% of facts. It is not a brevity measure: its dictionary bans common verbs, so `check the config` becomes `do a check of the config`, and it renders `&` as `the ampersand symbol`.

**[Caveman](https://github.com/JuliusBrussee/caveman).** Twenty skills with per-task intensity levels. Its main skill governs conversation and exempts persisted text by design:

> Persisted outside chat: write normal prose — code, comments, commits, docs, issue/PR/MR text, memory files.

Commit messages and documentation stay at full length unless the matching skill is invoked.

**Claude Code's built-in `Concise` style.** Introduced in 2.1.237. It scores 19.2 and retains 97% of facts, the strongest result of any alternative measured here. An output style edits the system prompt, so it governs files and commit messages as well as replies. Two limits: it exists only in Claude Code, and it stops at the main conversation. Every subagent you delegate to writes unconstrained prose.

### Where DTS sits

| Approach   | Setup           | Judge /20 | Facts kept | Covers docs and commits      |
| ---------- | --------------- | --------- | ---------- | ---------------------------- |
| ELI5       | one prompt      | 13.7      | 69.7%      | yes                          |
| ASD-STE100 | one prompt      | 16.4      | 88.0%      | yes                          |
| Caveman    | twenty skills   | 16.5      | 95.1%      | only when you invoke them    |
| Concise    | one setting     | 19.2      | 97.3%      | main agent, Claude Code only |
| **DTS**    | **one install** | **18.6**  | **95.1%**  | **main agent and subagents** |

It is a good tool making a different bet: that you want to steer. On Claude Opus it is also about 5-7% cheaper than DTS on raw tokens.

It depends, if you want that final 5-7% for reduced quality.

---

## Install

```sh
git clone https://github.com/farhan-syah/dts && cd dts && ./install.sh
```

It detects every agent on your PATH and writes to each one's global file.

|                            |                                                     |
| -------------------------- | --------------------------------------------------- |
| `./install.sh --list`      | what it found, and where it will write              |
| `./install.sh --dry-run`   | show every change, touch nothing                    |
| `./install.sh --project`   | rule files for editors that read them from the repo |
| `./install.sh --print`     | the block, to paste anywhere else                   |
| `./install.sh --uninstall` | remove it cleanly                                   |

Per-agent paths, project rules, and the agents that need a manual paste: [INSTALL.md](INSTALL.md).

---

## What you save

Savings depend on your model and on what you asked. Quality held in both setups.

| Your setup          | Median cut | Range across 50 prompts | Cuts output on | Facts kept |
| ------------------- | ---------- | ----------------------- | -------------- | ---------- |
| glm-5.2             | **-83%**   | -95% to -36%            | 50 of 50       | 95.1%      |
| Claude Opus 5, bare | **-10%**   | -49% to **+57%**        | 34 of 50       | **97.8%**  |

A model that pads gets padding removed, everywhere. Opus already writes densely, so the result depends on the request:

| On Opus, DTS cuts                                     | On Opus, DTS adds                                     |
| ----------------------------------------------------- | ----------------------------------------------------- |
| design -25%, enumerate -22%, debug -22%, compare -20% | error messages +25%, quick answers +8%, decisions +8% |

Long answers compress. Short ones do not, and DTS spends words there on the contrast cases and exact commands a bare model leaves out. The incident update above ran -85% on Opus. A one-line lookup runs positive.

One percentage per model is not enough. How much you save depends on what you ask for.

Inside an agent loop the answer is different: prose falls about 14% and the bill does not move, because output is under 1% of the tokens a session spends. [The detail](MECHANISM.md#inside-an-agent-loop).

---

## How it compares

Seven arms, 50 prompts, two reps, 100 answers per arm. Two independent judges scored every answer: `deepseek-v4-pro` and Claude Opus 5. Neither wrote any of them.

Each rival is the artifact people install, copied verbatim — [Caveman](https://github.com/JuliusBrussee/caveman), [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), [ponytail](https://github.com/DietrichGebert/ponytail), and Claude Code's built-in `Concise`. Versions and commits are in [`bench/arms/PROVENANCE.md`](bench/arms/PROVENANCE.md).

| Standard    | Tokens, median | vs baseline | Facts kept, mean | English /5 | Judge /20 |
| ----------- | -------------- | ----------- | ---------------- | ---------- | --------- |
| Concise     | 231            | -71%        | 97.3%            | 4.98       | 19.18     |
| No standard | 808            | —           | 98.3%            | 4.97       | 18.93     |
| **DTS**     | **118**        | **-85%**    | **95.1%**        | **4.97**   | **18.62** |
| ponytail    | 132            | -84%        | 91.2%            | 4.63       | 17.52     |
| Caveman     | 114            | -86%        | 95.1%            | 3.39       | 16.48     |
| ASD-STE100  | 146            | -82%        | 88.0%            | 4.69       | 16.36     |
| ELI5        | 148            | -82%        | 69.7%            | 4.24       | 13.65     |

Tokens are medians. One truncated answer moves a mean by 70 tokens and cannot move a median. Facts are means, because the median saturates: most answers match every required pattern, so six of the seven arms have a median of exactly 100%.

Paired bootstrap over the same prompts, DTS against each:

| Comparison        | Difference | 95% CI         | Verdict             |
| ----------------- | ---------- | -------------- | ------------------- |
| DTS vs ELI5       | +4.97      | [+4.51, +5.43] | real                |
| DTS vs ASD-STE100 | +2.27      | [+1.81, +2.75] | real                |
| DTS vs Caveman    | +2.14      | [+1.74, +2.58] | real                |
| DTS vs ponytail   | +1.10      | [+0.67, +1.55] | real                |
| DTS vs Concise    | **-0.56**  | [-0.82, -0.30] | real, Concise ahead |

Three results are worth reading closely.

**DTS holds the English.** 4.97 out of 5, the same as an agent running no standard at all. Caveman reaches a shorter answer than DTS and scores 3.39, because it drops articles and inflections. Its own output above reads `git revert create new commit that undo changes`.

**Caveman keeps the same facts DTS does.** Both retain 95.1%. The difference between them is not what survives compression, it is whether the result is still English.

**Concise scores higher than DTS at twice the tokens.** It is the strongest alternative measured and it costs 231 tokens against 118. It runs only in Claude Code, and it stops at the main conversation. DTS installs as a rules block as well as a style, so it also governs every subagent the main agent delegates to.

Method, estimators and limits: [BENCHMARK.md](BENCHMARK.md).

---

## The rules

15 rules, in [`rules/dts.md`](rules/dts.md). The full text is in the paste block above.

The layers, and how DTS reaches subagents: [MECHANISM.md](MECHANISM.md).

---

## What ships

| Path                                           | What it is                                             |
| ---------------------------------------------- | ------------------------------------------------------ |
| [`rules/dts.md`](rules/dts.md)                 | The always-on rules. Goes in your agent's memory file. |
| [`skills/dts/`](skills/dts/)                   | The full spec. Costs nothing until something calls it. |
| [`output-styles/dts.md`](output-styles/dts.md) | Chat style, Claude Code only.                          |
| [`overlays/`](overlays/)                       | Templates for adding your own rules.                   |
| [`bench/`](bench/)                             | The benchmark, conversational and agentic.             |
| [MECHANISM.md](MECHANISM.md)                   | How it works, and why the saving varies by model.      |
| [BENCHMARK.md](BENCHMARK.md)                   | Method, estimators, and what it does not prove.        |
| [INSTALL.md](INSTALL.md)                       | Per-agent paths, project rules, manual paste.          |
| [EXAMPLES.md](EXAMPLES.md)                     | Full unedited replies from every standard.             |
| [`tests/`](tests/)                             | Unit tests. `python3 -m unittest discover -s tests`    |

---

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

---

## License

MIT. See [LICENSE](LICENSE).
