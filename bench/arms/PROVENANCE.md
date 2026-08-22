<!-- dts:no-lint -->

# Arm provenance

Every arm is the artifact people actually install, copied verbatim. An invented approximation of a competitor is a strawman, and a benchmark built on strawmen measures nothing.

| Arm            | Source                                                                                                                                              | Retrieved  |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| [`baseline.txt`](baseline.txt) | Empty file. No system prompt.                                                                                                                       | —          |
| [`caveman.txt`](caveman.txt)  | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) `skills/caveman/SKILL.md`, body after frontmatter. Commit `2f49f0e`.              | 2026-08-21 |
| [`ste100.txt`](ste100.txt)   | [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) `skills/simple-english/SKILL.md`, body after frontmatter. Commit `be3277c`.       | 2026-08-20 |
| [`eli5.txt`](eli5.txt)     | A working developer's real Claude Code output style, used daily. Not a reconstruction.                                                              | 2026-08-21 |
| [`ponytail.txt`](ponytail.txt) | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) `skills/ponytail/SKILL.md`, body after frontmatter. Commit `2ed6c52`, v4.9.0. | 2026-08-22 |
| [`dts.txt`](dts.txt)      | Generated from this repo by [`bench/sync-arms.sh`](../sync-arms.sh). Never hand-edited.                                                                                | —          |

## Rules for adding or changing an arm

- Copy the upstream artifact verbatim. Do not trim sections that look irrelevant. [`caveman.txt`](caveman.txt) keeps its classical-Chinese modes because a user installing the skill gets them.
- Record the commit hash. An arm without provenance cannot be reproduced.
- Never write an arm yourself to represent someone else's approach.
- Take the body after the YAML frontmatter. Frontmatter routes the skill and never reaches the model as instruction.
- Regenerate [`dts.txt`](dts.txt) with [`bench/sync-arms.sh`](../sync-arms.sh) after any change to `rules/` or `output-styles/`. Never copy it from a personal agent config, which carries overlays the standard does not ship.

## Out-of-domain arms

[`ponytail.txt`](ponytail.txt) is not a competitor to DTS. It governs the code an agent writes. DTS governs the prose. Its own skill description says so:

> Do NOT use for non-coding requests (general knowledge, prose, translation, summaries, recipes).

The prompt corpus here is prose. Ponytail is therefore measured outside the domain it claims, and a low score on this corpus says nothing about it. Read it as a control that shows the two standards do not overlap, never as a ranking.

Ponytail's own benchmark makes the mirror-image move: it runs `caveman` on a code corpus and labels it a "terse-prose control". Both directions are honest as long as the label travels with the number.

Report an out-of-domain arm with its disclaimer attached, or leave it out.

## Rejected variants

Changes measured and not shipped. Recorded so the same idea is not proposed again. Rebuild either arm by editing a copy of [`dts.txt`](dts.txt).

| Change tested                                                                                        | Result    |
| ---------------------------------------------------------------------------------------------------- | --------- |
| Added to the tables rule: a cell states a fact unconditionally, move a sometimes-true fact to prose. | Rejected  |
| Removed the table mandate. Bullets, semicolons, and the item-opening rule stay.                      | No effect |

The motive was measured. DTS puts 21% of its lines in tables where every other arm stays under 6%, and its table rows carry 13% to 21% of its false claims against 0% to 8% elsewhere. A table cell holds no room for a condition, so `REST typically uses JSON` becomes a cell reading `JSON`.

The clause made every measure worse and none of it separable from noise: false claims `+0.09` per answer with CI `[-0.04, +0.23]`, quality `-0.26` with CI `[-0.62, +0.09]`. Table use rose from 26% of lines to 36%.

Naming tables in one more sentence made the model reach for tables more often. Any future wording that spends words on the tables rule carries the same risk, so measure table share, not only the target metric.

Removing the mandate settled the question the other way. Table share fell from 26% of lines to 0%, a complete manipulation, and nothing else moved:

| Axis          | Change | 95% CI         |
| ------------- | ------ | -------------- |
| correct       | +0.00  | [-0.14, +0.14] |
| complete      | -0.02  | [-0.14, +0.09] |
| usable        | -0.05  | [-0.19, +0.07] |
| english       | -0.02  | [-0.05, +0.00] |
| false claims  | -0.04  | [-0.23, +0.13] |
| fact coverage | -1.56  | [-4.06, +0.62] |

False claims did not fall when the tables went away. A table cell was where an error was visible, never where it was made. Compression makes the error, and it lands wherever the answer puts it.

Read this as a null, not as proof of no effect. With 64 pairs an effect under about 0.4 quality points stays invisible, and neither judge can see whether a table reads better to a person.

## Known differences from a real install

- A skill loads on trigger. Here every arm is a system prompt on every call, so each arm runs at full strength. That favours no arm over another, and it removes trigger reliability from the measurement.
- [`caveman.txt`](caveman.txt) defaults to `full` intensity, its own documented default. `lite` and `ultra` are untested.
- [`caveman.txt`](caveman.txt) states that persisted text stays in normal prose. The benchmark prompts are conversational, so the rule does not fire.
- [`ponytail.txt`](ponytail.txt) ships intensity levels and defaults to `full`. It also expects a repo to read, which a single-turn prompt cannot give it.

## Test-only corpora

[`prompts-codesafe.json`](../prompts-codesafe.json) and [`prompts-overlay.json`](../prompts-overlay.json) are pass-or-fail suites, not quality benchmarks. Run them after any change to the rules.

| Corpus                  | Asks                                              |
| ----------------------- | ------------------------------------------------- |
| [`prompts-codesafe.json`](../prompts-codesafe.json) | Does the standard damage code it was given?       |
| [`prompts-overlay.json`](../prompts-overlay.json)  | Does an operator overlay still beat the standard? |

The overlay suite needs a second arm carrying a forcing override. Build it by appending overrides that contradict a rule, such as banning tables. A permissive override cannot be measured, because the model already writes well inside the limit.
