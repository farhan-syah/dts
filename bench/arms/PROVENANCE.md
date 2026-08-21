<!-- dts:no-lint -->

# Arm provenance

Every arm is the artifact people actually install, copied verbatim. An invented approximation of a competitor is a strawman, and a benchmark built on strawmen measures nothing.

| Arm            | Source                                                                                                                                        | Retrieved  |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `baseline.txt` | Empty file. No system prompt.                                                                                                                 | —          |
| `caveman.txt`  | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) `skills/caveman/SKILL.md`, body after frontmatter. Commit `2f49f0e`.        | 2026-08-21 |
| `ste100.txt`   | [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) `skills/simple-english/SKILL.md`, body after frontmatter. Commit `be3277c`. | 2026-08-20 |
| `eli5.txt`     | A working developer's real Claude Code output style, used daily. Not a reconstruction.                                                        | 2026-08-21 |
| `dts.txt`    | Generated from this repo by `bench/sync-arms.sh`. Never hand-edited.                                                                          | —          |

## Rules for adding or changing an arm

- Copy the upstream artifact verbatim. Do not trim sections that look irrelevant. `caveman.txt` keeps its classical-Chinese modes because a user installing the skill gets them.
- Record the commit hash. An arm without provenance cannot be reproduced.
- Never write an arm yourself to represent someone else's approach.
- Take the body after the YAML frontmatter. Frontmatter routes the skill and never reaches the model as instruction.
- Regenerate `dts.txt` with `bench/sync-arms.sh` after any change to `rules/` or `output-styles/`. Never copy it from a personal agent config, which carries overlays the standard does not ship.

## Known differences from a real install

- A skill loads on trigger. Here every arm is a system prompt on every call, so each arm runs at full strength. That favours no arm over another, and it removes trigger reliability from the measurement.
- `caveman.txt` defaults to `full` intensity, its own documented default. `lite` and `ultra` are untested.
- `caveman.txt` states that persisted text stays in normal prose. The benchmark prompts are conversational, so the rule does not fire.

## Test-only corpora

`prompts-codesafe.json` and `prompts-overlay.json` are pass-or-fail suites, not quality benchmarks. Run them after any change to the rules.

| Corpus | Asks |
|---|---|
| `prompts-codesafe.json` | Does the standard damage code it was given? |
| `prompts-overlay.json` | Does an operator overlay still beat the standard? |

The overlay suite needs a second arm carrying a forcing override. Build it by appending overrides that contradict a rule, such as banning tables. A permissive override cannot be measured, because the model already writes well inside the limit.
