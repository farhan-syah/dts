#!/usr/bin/env python3
"""Tests for the sentence-cap check: the awk in check.md and its Python twin.

The awk block is extracted from skills/dts/references/check.md, so a doc edit
that breaks the command fails here. Hosts with no awk report those cases as
skipped, never as passed.

Run: python3 -m unittest discover -s tests -v
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "tools", "sentence-cap.py")
CHECK_MD = os.path.join(ROOT, "skills", "dts", "references", "check.md")
AWK = shutil.which("awk")

spec = importlib.util.spec_from_file_location("sentence_cap", TOOL)
sentence_cap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sentence_cap)

WRAPPED = """# Heading

A wrapped paragraph that runs on
and on across three separate source
lines and clearly exceeds the twenty word ceiling for descriptive prose here.
"""

SHORT = """# Heading

Two words.
"""

FRONTMATTER = """---
description: this frontmatter line is long enough to trip the cap check by a very wide margin indeed
---

Two words.
"""

FENCE = """# Heading

```sh
this fenced line is long enough to trip the cap check by a very wide margin indeed and more
```

Two words.
"""

TABLE = """# Heading

| col | a table row that is long enough to trip the cap check by a very wide margin indeed |
| --- | --- |
"""

LIST = """# Heading

- a list item that is long enough to trip the cap check by a very wide margin indeed and then some more
- short item
"""

FIXTURES = {"wrapped": WRAPPED, "short": SHORT, "frontmatter": FRONTMATTER,
            "fence": FENCE, "table": TABLE, "list": LIST}


def awk_script():
    """Return the sentence-cap awk program as check.md ships it."""
    with open(CHECK_MD, encoding="utf-8") as handle:
        text = handle.read()
    block = re.search(r"````sh\n(awk -v CAP=20 .*?)\n````", text, re.S)
    assert block, "check.md no longer carries an awk -v CAP=20 block"
    body = block.group(1)
    return body[body.index("'") + 1:body.rindex("'")]


def run_awk(paths, cap=20):
    """Run the shipped awk over paths. Raises when the awk body is broken."""
    out = subprocess.run([AWK, "-v", f"CAP={cap}", awk_script()] + paths,
                         capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def run_python(paths, cap=20):
    """Run the Python twin over paths, in process."""
    hits = []
    for path in paths:
        with open(path, encoding="utf-8", errors="replace",
                  newline="") as handle:
            lines = handle.read().split("\n")
        for name, line, words, sentence in sentence_cap.violations(
                lines, path, cap):
            hits.append(f"{name}:{line}: {words} words: {sentence}")
    return hits


class CapCase(unittest.TestCase):
    """Writes fixture files into a throwaway directory."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)

    def write(self, name, text, newline="\n"):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text.replace("\n", newline))
        return path


class TestWrappedSentences(CapCase):
    """A sentence split over source lines is one sentence."""

    def test_wrapped_paragraph_is_caught(self):
        path = self.write("wrapped.md", WRAPPED)
        hits = run_python([path])
        self.assertEqual(len(hits), 1)
        self.assertIn("24 words", hits[0])
        self.assertTrue(hits[0].startswith(f"{path}:3:"), hits[0])

    def test_short_paragraph_passes(self):
        self.assertEqual(run_python([self.write("short.md", SHORT)]), [])

    def test_cap_is_configurable(self):
        path = self.write("cap.md", "# Heading\n\nSix words sit in this"
                                    " sentence.\n")
        self.assertEqual(run_python([path], cap=20), [])
        self.assertEqual(len(run_python([path], cap=5)), 1)


class TestMultiFile(CapCase):
    """Each violation names the file it came from."""

    def test_trailing_paragraph_keeps_its_own_filename(self):
        first = self.write("first.md", WRAPPED)
        second = self.write("second.md", SHORT)
        hits = run_python([first, second])
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].startswith(f"{first}:3:"), hits[0])
        self.assertNotIn("second.md", hits[0])

    def test_both_files_report_their_own_violations(self):
        first = self.write("first.md", WRAPPED)
        second = self.write("second.md", WRAPPED)
        hits = run_python([first, second])
        self.assertEqual(len(hits), 2)
        self.assertTrue(hits[0].startswith(f"{first}:3:"), hits[0])
        self.assertTrue(hits[1].startswith(f"{second}:3:"), hits[1])


class TestCrlf(CapCase):
    """A CRLF file scores the same as its LF twin."""

    def test_wrapped_paragraph_is_caught(self):
        path = self.write("crlf.md", WRAPPED, newline="\r\n")
        hits = run_python([path])
        self.assertEqual(len(hits), 1)
        self.assertIn("24 words", hits[0])
        self.assertNotIn("\r", hits[0])

    def test_frontmatter_is_skipped(self):
        path = self.write("fm.md", FRONTMATTER, newline="\r\n")
        self.assertEqual(run_python([path]), [])

    def test_fence_is_skipped(self):
        path = self.write("fence.md", FENCE, newline="\r\n")
        self.assertEqual(run_python([path]), [])

    def test_table_row_is_skipped(self):
        path = self.write("table.md", TABLE, newline="\r\n")
        self.assertEqual(run_python([path]), [])

    def test_list_item_scores_alone(self):
        path = self.write("list.md", LIST, newline="\r\n")
        hits = run_python([path])
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].startswith(f"{path}:3:"), hits[0])
        self.assertNotIn("\r", hits[0])


class TestSkippedBlocks(CapCase):
    """Frontmatter, fences and tables never score. List items score alone."""

    def test_frontmatter_is_skipped(self):
        self.assertEqual(run_python([self.write("fm.md", FRONTMATTER)]), [])

    def test_fence_is_skipped(self):
        self.assertEqual(run_python([self.write("fence.md", FENCE)]), [])

    def test_table_row_is_skipped(self):
        self.assertEqual(run_python([self.write("table.md", TABLE)]), [])

    def test_list_item_scores_alone(self):
        path = self.write("list.md", LIST)
        hits = run_python([path])
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].startswith(f"{path}:3:"), hits[0])


class TestWordCount(CapCase):
    """A word breaks on space, tab and newline, as it does under awk."""

    def test_non_breaking_space_is_not_a_word_break(self):
        text = "# Heading\n\n" + "\u00a0".join("abcdefghijklmnopqrstuv") + ".\n"
        self.assertEqual(run_python([self.write("nbsp.md", text)]), [])

    def test_carriage_return_run_strips_one(self):
        path = self.write("cr.md", "# Heading\n\nTwo words.\r\r\n")
        self.assertEqual(run_python([path]), [])


class TestCli(CapCase):
    """The command gates CI: non-zero on a hit, on a missing file, else zero."""

    def run_cli(self, args, env=None):
        environment = dict(os.environ, **(env or {}))
        return subprocess.run([sys.executable, TOOL] + args,
                              capture_output=True, text=True, env=environment)

    def test_exit_zero_when_clean(self):
        out = self.run_cli([self.write("short.md", SHORT)])
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout, "")

    def test_exit_one_on_violation(self):
        out = self.run_cli([self.write("wrapped.md", WRAPPED)])
        self.assertEqual(out.returncode, 1)
        self.assertIn("24 words", out.stdout)

    def test_missing_file_reports_and_fails(self):
        out = self.run_cli([os.path.join(self.dir, "nope.md")])
        self.assertEqual(out.returncode, 1)
        self.assertIn("not found", out.stderr)
        self.assertNotIn("Traceback", out.stderr)

    def test_non_utf8_input_does_not_crash(self):
        path = os.path.join(self.dir, "latin1.md")
        with open(path, "wb") as handle:
            handle.write("# Heading\n\ncafé one two three four five six"
                         " seven eight nine ten eleven twelve thirteen"
                         " fourteen fifteen sixteen seventeen eighteen"
                         " nineteen twenty.\n".encode("latin-1"))
        out = self.run_cli([path])
        self.assertEqual(out.returncode, 1)
        self.assertNotIn("Traceback", out.stderr)

    def test_non_ascii_hit_survives_a_narrow_stdout_codepage(self):
        text = ("# Heading\n\n→ one two three four five six seven eight"
                " nine ten eleven twelve thirteen fourteen fifteen sixteen"
                " seventeen eighteen nineteen twenty.\n")
        out = self.run_cli([self.write("arrow.md", text)],
                           env={"PYTHONIOENCODING": "cp1252"})
        self.assertEqual(out.returncode, 1)
        self.assertNotIn("Traceback", out.stderr)
        self.assertIn("words:", out.stdout)


@unittest.skipUnless(AWK, "awk not on PATH")
class TestAwkParity(CapCase):
    """The shipped awk and the Python twin print the same lines."""

    def assert_agrees(self, paths, cap=20):
        self.assertEqual(run_python(paths, cap), run_awk(paths, cap))

    def test_every_fixture_agrees(self):
        for name, text in FIXTURES.items():
            with self.subTest(fixture=name):
                self.assert_agrees([self.write(f"{name}.md", text)])

    def test_every_fixture_agrees_with_crlf(self):
        for name, text in FIXTURES.items():
            with self.subTest(fixture=name):
                self.assert_agrees(
                    [self.write(f"{name}.md", text, newline="\r\n")])

    def test_multi_file_agrees(self):
        first = self.write("first.md", WRAPPED)
        second = self.write("second.md", SHORT)
        self.assert_agrees([first, second])
        self.assert_agrees([second, first])

    def test_cap_fifteen_agrees(self):
        path = self.write("wrapped.md", WRAPPED)
        self.assert_agrees([path], cap=15)

    def test_word_count_agrees_on_unicode_spaces(self):
        text = "# Heading\n\n" + "\u00a0".join("abcdefghijklmnopqrstuv") + ".\n"
        self.assert_agrees([self.write("nbsp.md", text)])

    def test_repo_markdown_agrees(self):
        docs = [os.path.join(ROOT, "README.md"),
                os.path.join(ROOT, "rules", "dts.md"), CHECK_MD]
        docs = [d for d in docs if os.path.exists(d)]
        self.assertTrue(docs, "no shipped Markdown found to compare")
        self.assert_agrees(docs)


if __name__ == "__main__":
    unittest.main()
