# How DTS was measured

The harness, the estimators, and what the numbers do not establish.

## Running the benchmark

Python 3.11 or newer. Nothing to install.

```sh
cd bench
./providers.py       # which models you can reach
./bench.py --list    # arms, models, and the 50 prompts
./runall.sh --dry    # show the plan
./runall.sh          # run it
```

The agent-loop benchmark runs a headless Claude Code session per trial against a pinned real repository. Each arm installs the way a user installs it, as a project memory file.

```sh
./agentic.py --list
./agentic.py --arms baseline dts --reps 4
```

Models are written `provider:model`:

```sh
./bench.py --model claude:opus --cats debug --reps 3 --out out/x.json
./judge.py out/x.json --judge-model ollama:deepseek-v4-pro:cloud
./report.py out/x-judged.json --by-cat
./lint.py --results out/x.json
```

`claude:opus` runs Opus 5 through your local CLI with no API key. Judge with a model that did not write the answers.

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

## Did the rules actually get followed

Token counts show what an answer cost. They do not show whether your agent followed the rules or just got shorter. [`bench/lint.py`](bench/lint.py) counts rule breaks per 100 words.

| Standard    | Rule breaks per 100 words |
| ----------- | ------------------------- |
| **DTS**     | **0.18**                  |
| ASD-STE100  | 0.19                      |
| Caveman     | 0.30                      |
| ELI5        | 0.60                      |
| ponytail    | 0.95                      |
| Concise     | 1.05                      |
| No standard | 1.63                      |

DTS and ASD-STE100 sit level here, at 0.18 and 0.19. On the benchmark they score 18.62 and 16.36. Following the rules closely does not make the rules good.

Concise scores 1.05, above ELI5, and still wins the quality table. Its rules are not DTS's rules. This measures distance from the DTS grammar, never how well an arm followed its own.

## The inversion rule

`Say it straight` bans a sentence that says what something is by first saying what it is not. `not X, but Y`. `the method, not the goal`. [`bench/lint.py`](bench/lint.py) finds some of them. The check also runs on the standard's own files, so DTS cannot break a rule it ships.

Detection is measured on text the pattern was never tuned against, in [`tests/fixtures-inversion.json`](tests/fixtures-inversion.json).

| Measure                              | Result  |
| ------------------------------------ | ------- |
| Recall, 40 unseen inversions         | **20%** |
| False positives, 40 plain statements | **0%**  |

Use it to confirm a problem. Never use it to confirm there is none. A passing run means the four commonest shapes are absent. It says nothing about the rest.

It misses sentences that bury the negation in the middle, such as `It is not the pursuit of perfection that guides the work, but the discipline`. A regular expression cannot find those.

Two shapes are allowed on purpose. `X, never Y` states a direct contrast, and DTS uses it throughout. `Never paraphrase them, never re-case them` is an instruction. An early pattern flagged both.

An earlier version scored 85% against the six sentences used to write it, then 0% against the first unseen set. Tuning a detector on its own test set measures nothing.

Whether the rule changes what a model writes is untested. [`bench/prompts-inversion.json`](bench/prompts-inversion.json) ran on glm-5.2 across 6 prompts and 3 reps. Both arms wrote zero inversions. glm does not write them, so this corpus cannot show whether the rule stops them.

Every case the rule was written for was Claude Opus 5 writing documentation. Testing it needs that model and that task.

## What this does not prove

- Savings depend on your model and your harness, not on the standard alone. Treat every number here as one setup measured once, and run the benchmark on yours.
- One writer model was compared across all arms, plus two Claude Opus setups measured separately. Three setups cannot predict a fourth.
- The agent-loop numbers are Haiku 4.5 on one repository across 8 prose-heavy tasks. Opus is the model people call verbose, and it is not measured here yet. No judge scored those answers, so they are shorter by measurement and equally correct only by task completion.
- The judges are language models, told that length is not quality. They are not people, and two of them agree exactly on 39% of answers. Gaps under about half a point are noise, which is why every comparison above carries an interval.
- The lint is regular expressions. It cannot see passive voice or parts of speech, so it undercounts.
- Raw answers are not committed. `out/` stays out of the repo, so these tables cannot be audited without rerunning against the same model version.
