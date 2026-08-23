#!/usr/bin/env python3
"""Tests for install.py, which edits a user's global agent memory file.

Everything outside the markers belongs to the user. A bug here silently eats
notes the user cannot get back, so each case below asserts survival of the
surrounding text, not only correctness of the block.

Run: python3 -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import install  # noqa: E402

BEGIN = "<!-- dts:start -->"
END = "<!-- dts:end -->"


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.mem = os.path.join(self.dir.name, "CLAUDE.md")
        self.rules = os.path.join(self.dir.name, "rules.md")
        with open(self.rules, "w") as f:
            f.write("## Output Standard (DTS 0.1)\n\n- Answer first.\n")
        self.addCleanup(self.dir.cleanup)

    def put(self, text):
        with open(self.mem, "w") as f:
            f.write(text)

    def get(self):
        with open(self.mem) as f:
            return f.read()

    def block_count(self):
        return self.get().count(BEGIN)


class TestWrite(Base):
    def test_creates_missing_file(self):
        install.write(self.mem, self.rules)
        self.assertIn(BEGIN, self.get())
        self.assertIn("Answer first.", self.get())

    def test_creates_missing_parent_directory(self):
        nested = os.path.join(self.dir.name, "a", "b", "AGENTS.md")
        install.write(nested, self.rules)
        with open(nested) as f:
            self.assertIn(BEGIN, f.read())

    def test_appends_to_existing_file_and_keeps_user_text(self):
        self.put("# My notes\n\nDo not lose this line.\n")
        install.write(self.mem, self.rules)
        out = self.get()
        self.assertIn("Do not lose this line.", out)
        self.assertIn(BEGIN, out)

    def test_reinstall_replaces_in_place_without_duplicating(self):
        install.write(self.mem, self.rules)
        install.write(self.mem, self.rules)
        install.write(self.mem, self.rules)
        self.assertEqual(self.block_count(), 1)

    def test_reinstall_updates_stale_content(self):
        install.write(self.mem, self.rules)
        with open(self.rules, "w") as f:
            f.write("## Output Standard (DTS 0.1)\n\n- A new rule.\n")
        install.write(self.mem, self.rules)
        out = self.get()
        self.assertIn("A new rule.", out)
        self.assertNotIn("Answer first.", out)

    def test_text_outside_markers_survives_reinstall(self):
        self.put("TOP\n")
        install.write(self.mem, self.rules)
        with open(self.mem, "a") as f:
            f.write("\n### My overlays\n- Spanish: not DTS.\n")
        install.write(self.mem, self.rules)
        out = self.get()
        self.assertIn("TOP", out)
        self.assertIn("### My overlays", out)
        self.assertIn("Spanish: not DTS.", out)
        self.assertEqual(self.block_count(), 1)

    def test_migrates_old_marker_names(self):
        self.put(f"KEEP\n\n<!-- dts:begin -->\nold rules\n{END}\n\nTAIL\n")
        install.write(self.mem, self.rules)
        out = self.get()
        self.assertIn(BEGIN, out)
        self.assertNotIn("dts:begin", out)
        self.assertNotIn("old rules", out)
        self.assertIn("KEEP", out)
        self.assertIn("TAIL", out)
        self.assertEqual(self.block_count(), 1)

    def test_adopts_unmarked_hand_pasted_block(self):
        self.put("# Notes\n\n## Output Standard (DTS 0.1)\n\n- stale\n\n"
                 "## Task Management\n\n- keep me\n")
        install.write(self.mem, self.rules)
        out = self.get()
        self.assertEqual(self.block_count(), 1)
        self.assertNotIn("- stale", out)
        self.assertIn("## Task Management", out)
        self.assertIn("- keep me", out)

    def test_a_block_from_an_older_version_is_adopted(self):
        """Anyone running DTS 1.0 must not end up with two blocks."""
        self.put("# Notes\n\n## Output Standard (DTS 1.0)\n\n- old rule\n\n"
                 "## Mine\n\n- keep me\n")
        install.write(self.mem, self.rules)
        out = self.get()
        self.assertEqual(self.block_count(), 1)
        self.assertNotIn("- old rule", out)
        self.assertNotIn("DTS 1.0", out)
        self.assertIn("- keep me", out)

    def test_empty_rules_file_aborts(self):
        with open(self.rules, "w") as f:
            f.write("   \n\n")
        with self.assertRaises(SystemExit):
            install.write(self.mem, self.rules)

    def test_whitespace_only_file_is_treated_as_empty(self):
        self.put("\n\n   \n")
        install.write(self.mem, self.rules)
        self.assertTrue(self.get().startswith(BEGIN))

    def test_second_stray_end_marker_is_not_consumed(self):
        # A lone END below the block must not extend the replacement span and
        # swallow the user's text in between.
        install.write(self.mem, self.rules)
        with open(self.mem, "a") as f:
            f.write(f"\nUSER TEXT\n{END}\n")
        install.write(self.mem, self.rules)
        self.assertIn("USER TEXT", self.get())

    def test_is_idempotent_byte_for_byte(self):
        self.put("head\n")
        install.write(self.mem, self.rules)
        once = self.get()
        install.write(self.mem, self.rules)
        self.assertEqual(once, self.get())


class TestRemove(Base):
    def test_removes_block_and_keeps_user_text(self):
        self.put("BEFORE\n")
        install.write(self.mem, self.rules)
        with open(self.mem, "a") as f:
            f.write("\nAFTER\n")
        install.remove(self.mem)
        out = self.get()
        self.assertNotIn(BEGIN, out)
        self.assertNotIn("Answer first.", out)
        self.assertIn("BEFORE", out)
        self.assertIn("AFTER", out)

    def test_remove_on_clean_file_changes_nothing(self):
        self.put("just my notes\n")
        install.remove(self.mem)
        self.assertEqual(self.get(), "just my notes\n")

    def test_remove_on_missing_file_does_not_create_it(self):
        install.remove(self.mem)
        self.assertFalse(os.path.exists(self.mem))

    def test_write_then_remove_restores_original(self):
        original = "# Mine\n\nline one\nline two\n"
        self.put(original)
        install.write(self.mem, self.rules)
        install.remove(self.mem)
        self.assertEqual(self.get().strip(), original.strip())


class TestCli(Base):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "install.py"), *args],
            capture_output=True, text=True)

    def test_write_and_remove_via_cli(self):
        r = self.run_cli("write", self.mem, self.rules)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(BEGIN, self.get())
        r = self.run_cli("remove", self.mem)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(BEGIN, self.get())

    def test_unknown_command_exits_nonzero(self):
        self.assertNotEqual(self.run_cli("frobnicate", self.mem).returncode, 0)

    def test_no_arguments_exits_nonzero(self):
        self.assertNotEqual(self.run_cli().returncode, 0)

    def test_write_without_rules_file_exits_nonzero(self):
        self.assertNotEqual(self.run_cli("write", self.mem).returncode, 0)


class TestHostilePaths(Base):
    """install.sh once built shell strings and called eval. These paths broke it."""

    def paths(self):
        return ["with space", "quote'name", "dollar$sign", "semi;colon"]

    def test_write_survives_awkward_directory_names(self):
        for name in self.paths():
            d = os.path.join(self.dir.name, name)
            os.makedirs(d, exist_ok=True)
            mem = os.path.join(d, "CLAUDE.md")
            install.write(mem, self.rules)
            with open(mem) as f:
                self.assertIn(BEGIN, f.read(), f"failed for {name!r}")


class TestProjectMode(unittest.TestCase):
    """--project writes rule files for editor agents that read from the repo."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.proj = self.dir.name
        self.addCleanup(self.dir.cleanup)

    def install(self, *args):
        return subprocess.run(
            [os.path.join(ROOT, "install.sh"), "--project", self.proj, *args],
            capture_output=True, text=True, cwd=ROOT)

    def files(self):
        out = set()
        for root, _dirs, names in os.walk(self.proj):
            for n in names:
                out.add(os.path.relpath(os.path.join(root, n), self.proj))
        return out

    def read(self, rel):
        with open(os.path.join(self.proj, rel)) as f:
            return f.read()

    def test_agents_md_is_always_written(self):
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("AGENTS.md", self.files())
        self.assertIn(BEGIN, self.read("AGENTS.md"))

    def test_undetected_agents_are_skipped(self):
        self.install()
        self.assertNotIn(".cursor/rules/dts.mdc", self.files())
        self.assertNotIn(".clinerules/dts.md", self.files())

    def test_marker_directory_triggers_its_target(self):
        os.makedirs(os.path.join(self.proj, ".cursor"))
        self.install()
        self.assertIn(".cursor/rules/dts.mdc", self.files())

    def test_all_forces_every_target(self):
        self.install("--all")
        for rel in (".cursor/rules/dts.mdc", ".windsurf/rules/dts.md",
                    ".clinerules/dts.md", ".qoder/rules/dts.md",
                    ".kiro/steering/dts.md", ".github/copilot-instructions.md",
                    "AGENTS.md"):
            self.assertIn(rel, self.files(), rel)

    def test_cursor_file_gets_front_matter(self):
        self.install("--all")
        head = self.read(".cursor/rules/dts.mdc").splitlines()[:4]
        self.assertEqual(head[0], "---")
        self.assertIn("alwaysApply: true", head)

    def test_reinstall_keeps_front_matter_and_does_not_duplicate(self):
        self.install("--all")
        self.install("--all")
        body = self.read(".cursor/rules/dts.mdc")
        self.assertEqual(body.count(BEGIN), 1)
        self.assertIn("alwaysApply: true", body)

    def test_existing_project_text_survives(self):
        os.makedirs(os.path.join(self.proj, ".github"))
        with open(os.path.join(self.proj, ".github",
                               "copilot-instructions.md"), "w") as f:
            f.write("# House rules\n\nAlways rebase.\n")
        self.install()
        body = self.read(".github/copilot-instructions.md")
        self.assertIn("Always rebase.", body)
        self.assertIn(BEGIN, body)

    def test_uninstall_removes_blocks_and_keeps_user_text(self):
        os.makedirs(os.path.join(self.proj, ".github"))
        with open(os.path.join(self.proj, ".github",
                               "copilot-instructions.md"), "w") as f:
            f.write("# House rules\n\nAlways rebase.\n")
        self.install()
        self.install("--uninstall")
        body = self.read(".github/copilot-instructions.md")
        self.assertNotIn(BEGIN, body)
        self.assertIn("Always rebase.", body)
        self.assertNotIn(BEGIN, self.read("AGENTS.md"))

    def test_dry_run_writes_nothing(self):
        os.makedirs(os.path.join(self.proj, ".cursor"))
        before = self.files()
        r = self.install("--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(before, self.files())

    def test_only_restricts_to_one_target(self):
        self.install("--all", "--only", "cline")
        f = self.files()
        self.assertIn(".clinerules/dts.md", f)
        self.assertNotIn(".cursor/rules/dts.mdc", f)
        self.assertNotIn("AGENTS.md", f)

    def test_missing_directory_exits_nonzero(self):
        r = subprocess.run(
            [os.path.join(ROOT, "install.sh"), "--project",
             os.path.join(self.proj, "nope")],
            capture_output=True, text=True, cwd=ROOT)
        self.assertNotEqual(r.returncode, 0)

    def test_every_written_file_carries_the_shipped_rules(self):
        self.install("--all")
        with open(os.path.join(ROOT, "rules", "dts.md")) as f:
            first = next(l for l in f if l.startswith("- "))
        for rel in self.files():
            self.assertIn(first.strip(), self.read(rel), rel)


class TestReadmeBlockInSync(unittest.TestCase):
    """The README carries a copy of the rules. Editing around it drifts it.

    Only CI caught this before, so a push failed three times for a difference
    a local run never reported.
    """

    def test_block_matches_the_shipped_rules(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "sync-readme.py"), "--check"],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0,
                         f"{r.stdout}{r.stderr}run ./tools/sync-readme.py")


class TestShippedRules(unittest.TestCase):
    def test_shipped_rules_file_installs(self):
        rules = os.path.join(ROOT, "rules", "dts.md")
        self.assertTrue(os.path.exists(rules), "rules/dts.md is missing")
        with tempfile.TemporaryDirectory() as d:
            mem = os.path.join(d, "CLAUDE.md")
            install.write(mem, rules)
            install.write(mem, rules)
            with open(mem) as f:
                out = f.read()
        self.assertEqual(out.count(BEGIN), 1)
        self.assertEqual(out.count(END), 1)

    def test_readme_copy_of_the_block_matches_the_shipped_rules(self):
        """The README shows a paste-in copy. Drift makes it wrong silently."""
        with open(os.path.join(ROOT, "README.md")) as f:
            readme = f.read()
        with open(os.path.join(ROOT, "rules", "dts.md")) as f:
            rules = f.read().strip()
        start = readme.find("<!-- dts:readme-start -->")
        end = readme.find("<!-- dts:readme-end -->")
        self.assertNotEqual(start, -1, "README paste block markers missing")
        self.assertGreater(end, start)
        for line in rules.splitlines():
            if line.strip():
                self.assertIn(line, readme[start:end],
                              f"README paste block is stale, missing: {line[:60]!r}")


class TestReadmeSyncTolerance(unittest.TestCase):
    """A format-on-save pass reflows the fenced copy. That is not drift.

    Prettier inserts a blank line after `<!-- dts:start -->` inside the fence.
    A byte-exact guard fails on it, the whole test matrix goes red, and the
    next save undoes any fix.
    """

    def sync(self):
        import importlib.util
        path = os.path.join(ROOT, "tools", "sync-readme.py")
        spec = importlib.util.spec_from_file_location("sync_readme", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_layout_changes_are_not_drift(self):
        m = self.sync()
        plain = "<!-- dts:start -->\n## Title\n\n- One rule.\n"
        formatted = "<!-- dts:start -->\n\n## Title\n\n- One rule.   \n\n"
        self.assertEqual(m.norm(plain), m.norm(formatted))

    def test_content_changes_are_drift(self):
        m = self.sync()
        base = "<!-- dts:start -->\n- One rule.\n"
        for changed in ("<!-- dts:start -->\n- One rules.\n",
                        "<!-- dts:start -->\n- One rule.\n- Two rules.\n",
                        "<!-- dts:start -->\n"):
            self.assertNotEqual(m.norm(base), m.norm(changed), changed)


if __name__ == "__main__":
    unittest.main()
