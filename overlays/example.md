<!-- dts:no-lint -->

# Overlay template

Copy the parts you want into your agent memory file, below the DTS block.

The installer writes DTS between `<!-- dts:start -->` and `<!-- dts:end -->`. It never reads or writes a line outside those markers, so anything you put here survives every reinstall and every upgrade.

Delete this file's heading and comments. Keep only the lines you need.

---

## My writing overlays

DTS stops at English technical prose. Route everything else to your own handler. DTS ships no handler names, because it cannot see what you have installed.

- Spanish text: DTS does not apply. Use my `spanish-prose` skill.
- Fiction drafts: DTS does not apply. Use my `fiction-voice` skill.
- Landing pages and ad copy: DTS does not apply. Use my brand guide.
- Thesis chapters under `research/`: apply DTS core only.

Override a specific rule by naming it. A silent contradiction is a defect.

- Unlike DTS, in this repo descriptive sentences run to 30 words.
- Unlike DTS, keep `validate` as a distinct verb. We validate schemas here.
- Unlike DTS, `significant` is allowed. We report statistical significance.

Add to the canon rather than replacing it.

- Also canonical here: `endpoint` never route/path/URL. `job` never task/work item.

---

## Scoping an overlay to one project

Put the same lines in that project's memory file instead of your global one. A project file outranks the global DTS block for that project alone.

## Scoping to one file

Skip the overlay. Put a marker in the file:

- `<!-- dts:core -->` keeps the genre-neutral core only.
- `<!-- dts:off -->` disables DTS for that file.
