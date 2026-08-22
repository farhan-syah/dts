# How DTS works

The parts, what each one costs, and why the saving depends on your model.

## How it is built

| Layer                      | Loaded     | Cost                       | Owns                                    |
| -------------------------- | ---------- | -------------------------- | --------------------------------------- |
| [Core rules](rules/dts.md) | every turn | ~1000 input tokens, cached | every surface, main agent and subagents |
| [Skill](skills/dts/)       | on demand  | nothing until called       | full spec, audits, per-artifact shapes  |
| [Your overlays](overlays/) | every turn | yours                      | domain exceptions, other languages      |

The core is small enough to leave on. Depth sits in the skill, which costs nothing until something calls it. Your exceptions sit in an overlay the installer never touches.

That split is the point. A standard you have to invoke is a standard you forget.

The rules layer is why DTS reaches subagents. Claude Code loads every level of the `CLAUDE.md` hierarchy into a subagent's context. An output style does not travel, because a subagent runs its own system prompt. DTS installs as both, so a delegated agent writes to the same standard as the one that delegated to it. The built-in `Explore` and `Plan` agents skip memory files by design and are the exception.

## Why not just use ASD-STE100

[ASD-STE100](https://asd-ste100.org) is the aerospace writing standard. Its grammar rules are excellent.

Its dictionary is the cost. It bans common verbs, so `check the config` becomes `do a check of the config`.

That costs tokens and strips out the words an engineer needs.

DTS keeps the grammar and drops the dictionary.

Asked to explain a Rust move error, ASD-STE100 produced:

> If you pass a reference, use the ampersand symbol before the variable name.

`the ampersand symbol` instead of `&`, and no code block at all. Correct English, useless to a programmer.

## Why the saving depends on your model

A standard removes padding. It cannot remove padding your model never wrote.

Ask glm-5.2 to explain processes and threads. It opens with a house-and-tenant analogy, a "here is the breakdown" line, then numbered headings. Ask Claude Opus 5 the same thing and you get a one-line definition, a table, and nothing else. Both answers score 20 out of 20. Opus needs 485 tokens where glm needs 853, so DTS finds far less to cut.

Expect the high end on a smaller or older model. Expect the low end on a frontier model that already writes tightly.

Measured on 50 prompts with the model bare, Opus cuts output on 34 of them. The median prompt falls 10%, the best falls 49%, and the worst rises 57%. Fact retention goes up, from 95.9% to 97.8%. The split is by request, not by luck. Design, enumeration, debugging and comparison answers fall 20% to 25%. Error messages rise 25%, and short lookups rise 8%. Asked whether `git revert` rewrites history, Opus under DTS writes more. The standard asks for the contrast cases a bare model omits.

On glm-5.2 there is no such split. Every one of the 50 prompts got shorter, the median by 83%.

Anyone who gives one number for every model has measured one model. Measure yours.

## Inside an agent loop

A coding agent reads far more than it writes. Across 48 paired sessions on a real repository, on Haiku 4.5, every prose measure moved and the bill did not.

| Measure         | Baseline | DTS    | Change     | 95% CI          |
| --------------- | -------- | ------ | ---------- | --------------- |
| Prose written   | 2021 ch  | 1747   | **-13.6%** | [-23.8%, -4.3%] |
| Cost            | $0.0880  | 0.0874 | -0.7%      | [-6.5%, +4.6%]  |
| Turns           | 6.9      | 6.6    | -4.5%      | [-12.0%, +2.1%] |
| Tasks completed | 12/12    | 12/12  | —          | —               |

**Output tokens are 0.9% of the tokens in an agent session.** There are 102 tokens read for every one written. Compressing what the agent says cannot move a bill dominated by what it reads, however hard you compress.

So DTS makes an agent write shorter, and charges you nothing for it. That second half is not free elsewhere: Caveman on the same harness cut output tokens 31.5% and moved cost `+9.6%`.

Expect the conversation numbers where you talk to the model. Expect these where it works on your code.
