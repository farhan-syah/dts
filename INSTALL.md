# Installing DTS

The standard is a block of text. This covers where it goes for each agent, and the flags that put it there.

The block itself is at the top of the [README](README.md), or run `./install.sh --print`.

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

## Editors that read rules from the repo

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

Without `--all` it skips any editor whose directory is absent. A repo never collects rule files for editors nobody there runs. The Cursor file gets `alwaysApply: true` so it loads unprompted.

DTS is plain text with no runtime. That is why one file covers every agent above. Nothing here needs Node, a plugin host, or a hook.

**Your memory file is safe.** The rules go between `<!-- dts:start -->` and `<!-- dts:end -->`. Nothing outside those markers is read or changed, so your own notes survive every reinstall.

The skill also installs through the Agent Skills tool:

```sh
npx skills add farhan-syah/dts
```

## Any other agent

If your agent is not in the table, it almost certainly reads a global instructions file. Copy this into it:

Append it to whichever file your agent loads. `./install.sh --print` writes the same block to stdout, ready to pipe.

| Agent         | File                           |
| ------------- | ------------------------------ |
| Claude Code   | `~/.claude/CLAUDE.md`          |
| Codex         | `~/.codex/AGENTS.md`           |
| opencode      | `~/.config/opencode/AGENTS.md` |
| pi            | `~/.pi/agent/AGENTS.md`        |
| Gemini CLI    | `~/.gemini/GEMINI.md`          |
| any other agent | its global instructions file |

There is no shared file across agents. Each reads its own path, so the block goes in each one you use.

**Keep the `<!-- dts:start -->` and `<!-- dts:end -->` markers.** A later `./install.sh` updates the text between them in place. Without them you get a second copy, and the two drift apart.

Everything you write outside the markers is yours. The installer never reads it.

Only Claude Code has an output style. Every other agent gets the same rules through its instructions file, which covers replies as well as files.
