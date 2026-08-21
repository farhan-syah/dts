# Writing your own overlay

DTS governs English technical prose and stops there. Everything else — another language, fiction, brand copy, your team's house terms — is yours to define. An overlay is how you define it.

An overlay is plain text you add to your agent's memory file, below the DTS block. The installer writes DTS between `<!-- dts:start -->` and `<!-- dts:end -->` and never reads or writes a line outside them, so your overlay survives every reinstall and upgrade.

Copy what you need from [`example.md`](example.md).

## Route a genre to your own handler

DTS ships no handler names, because it cannot know what you have installed. Name yours:

```
### My overlays
- Spanish text: DTS does not apply. Use my `spanish-prose` skill.
- Fiction drafts: DTS does not apply. Use my `fiction-voice` skill.
- Landing pages and ad copy: DTS does not apply. Use my brand guide.
- Thesis chapters under `research/`: apply DTS core only.
```

## Override a rule by naming it

An overlay overrides by saying which rule it changes. A silent contradiction reads as a defect, and the agent will ask which one wins.

```
- Unlike DTS, in this repo descriptive sentences run to 30 words.
- Unlike DTS, keep `validate` as a distinct verb. We validate schemas here.
- Unlike DTS, `significant` is allowed. We report statistical significance.
```

## Add to the canon

Extend rather than replace. The rule is that the word is assigned, not which word wins.

```
- Also canonical here: `endpoint` never route/path/URL. `job` never task/work item.
```

## Choosing where to put it

| Scope             | Where                                                                        |
| ----------------- | ---------------------------------------------------------------------------- |
| Everything you do | Your global memory file, below the DTS block                                 |
| One project       | That project's memory file                                                   |
| One document      | Skip the overlay. Put `<!-- dts:core -->` or `<!-- dts:off -->` in the file. |

## Editing the standard itself

Two files are meant to be edited in your copy, and editing them is not a fork:

- The **canonical-word table** in `skills/dts/references/wordlist.md`. A team that writes `folder` rather than `directory` changes that row.
- The **kill-list** in the same file. Add the filler your field overuses. Remove a word your field needs — `significant` is filler in a README and a term of art in statistics.

Leave the sentence caps and the modal list alone. Use a per-file marker instead. A standard bent per document is not a standard.
