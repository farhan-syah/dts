#!/usr/bin/env python3
"""Tests for the benchmark harness: JSON extraction, coverage, aggregation, lint.

Run: python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bench"))

import bench  # noqa: E402
import judge  # noqa: E402
import lint  # noqa: E402
import report  # noqa: E402


class TestExtractJson(unittest.TestCase):
    """A judge reply arrives as prose, a fence, or bare JSON, per provider."""

    def test_bare_object(self):
        self.assertEqual(judge.extract_json('{"correct": 5}'), {"correct": 5})

    def test_json_fence(self):
        self.assertEqual(
            judge.extract_json('```json\n{"correct": 4}\n```'), {"correct": 4})

    def test_plain_fence(self):
        self.assertEqual(
            judge.extract_json('```\n{"correct": 3}\n```'), {"correct": 3})

    def test_uppercase_fence_tag(self):
        self.assertEqual(
            judge.extract_json('```JSON\n{"correct": 2}\n```'), {"correct": 2})

    def test_leading_and_trailing_prose(self):
        self.assertEqual(
            judge.extract_json('Here is my grade:\n{"correct": 1}\nDone.'),
            {"correct": 1})

    def test_nested_objects(self):
        got = judge.extract_json('{"a": {"b": {"c": 1}}, "d": 2}')
        self.assertEqual(got, {"a": {"b": {"c": 1}}, "d": 2})

    def test_brace_inside_a_string_does_not_end_the_object(self):
        got = judge.extract_json('{"wrong_claims": ["use {} for a set"]}')
        self.assertEqual(got["wrong_claims"], ["use {} for a set"])

    def test_escaped_quote_inside_a_string(self):
        got = judge.extract_json(r'{"wrong_claims": ["said \"x\" wrongly"]}')
        self.assertEqual(got["wrong_claims"], ['said "x" wrongly'])

    def test_no_object_raises(self):
        with self.assertRaises(ValueError):
            judge.extract_json("I refuse to grade this.")

    def test_unbalanced_object_raises(self):
        with self.assertRaises(ValueError):
            judge.extract_json('{"correct": 5')

    def test_malformed_json_raises(self):
        with self.assertRaises(Exception):
            judge.extract_json('{"correct": 5,,}')

    def test_empty_reply_raises(self):
        with self.assertRaises(ValueError):
            judge.extract_json("")


class TestCoverage(unittest.TestCase):
    def test_counts_hits_and_reports_misses(self):
        hit, total, missed = bench.coverage(
            "A process has its own memory.", ["process", "memory", "thread"])
        self.assertEqual((hit, total), (2, 3))
        self.assertEqual(missed, ["thread"])

    def test_alternation_pattern(self):
        hit, _, _ = bench.coverage("its own address space", ["memory|address space"])
        self.assertEqual(hit, 1)

    def test_is_case_insensitive(self):
        hit, _, _ = bench.coverage("PROCESS and Thread", ["process", "thread"])
        self.assertEqual(hit, 2)

    def test_empty_musts_is_not_a_division_hazard(self):
        self.assertEqual(bench.coverage("anything", []), (0, 0, []))

    def test_empty_text_scores_zero(self):
        hit, total, _ = bench.coverage("", ["process", "thread"])
        self.assertEqual((hit, total), (0, 2))

    def test_a_bare_keyword_list_scores_full_marks(self):
        """Documents the known weakness, so a future fix has a failing anchor."""
        hit, total, _ = bench.coverage(
            "process thread memory kernel share",
            ["process", "thread", "memory|address space", "schedul|CPU|kernel",
             "share|isolat"])
        self.assertEqual(hit, total)


def rec(arm, tok, text, wrong=(), quality=15, facts=2, total=2):
    return {
        "arm": arm, "out_tok": tok, "chars": len(text), "text": text,
        "facts": facts, "facts_total": total, "quality": quality,
        "axes": ["correct", "complete", "usable", "english"],
        "judge": {"correct": 4, "complete": 4, "usable": 4, "english": 3,
                  "wrong_claims": list(wrong)},
    }


class TestAgg(unittest.TestCase):
    def test_empty_input_returns_none(self):
        self.assertIsNone(report.agg([]))

    def test_all_errored_returns_none(self):
        self.assertIsNone(report.agg([{"error": "timeout"}]))

    def test_errors_are_counted_not_averaged(self):
        a = report.agg([rec("dts", 100, "a b c"), {"error": "timeout"}])
        self.assertEqual((a["n"], a["err"]), (1, 1))

    def test_false_claim_count_rises_with_verbosity_alone(self):
        """The confound the normalised metrics exist to remove."""
        short = report.agg([rec("dts", 50, "ten words " * 5, wrong=["x"])])
        long = report.agg([rec("base", 500, "ten words " * 50, wrong=["x", "y"])])
        self.assertGreater(long["false"], short["false"])

    def test_false_per_1000_words_removes_the_length_effect(self):
        # Same error density, ten times the length: the raw count differs, the
        # normalised rate does not.
        short = report.agg([rec("dts", 50, "w " * 100, wrong=["x"])])
        long = report.agg([rec("base", 500, "w " * 1000, wrong=["x"] * 10)])
        self.assertNotEqual(short["false"], long["false"])
        self.assertAlmostEqual(short["false_kw"], long["false_kw"], places=6)

    def test_false_any_is_a_percentage_of_answers(self):
        a = report.agg([
            rec("dts", 50, "a b", wrong=["x"]),
            rec("dts", 50, "a b"),
            rec("dts", 50, "a b"),
            rec("dts", 50, "a b"),
        ])
        self.assertAlmostEqual(a["false_any"], 25.0)

    def test_false_any_ignores_how_many_errors_one_answer_holds(self):
        one = report.agg([rec("a", 50, "w " * 100, wrong=["x"])])
        many = report.agg([rec("b", 50, "w " * 100, wrong=["x", "y", "z"])])
        self.assertEqual(one["false_any"], many["false_any"])
        self.assertGreater(many["false"], one["false"])

    def test_zero_facts_does_not_divide_by_zero(self):
        a = report.agg([rec("dts", 100, "a b", facts=0, total=0)])
        self.assertEqual(a["cov"], 0.0)
        self.assertEqual(a["tpf"], float("inf"))

    def test_missing_text_field_does_not_crash_normalisation(self):
        r = rec("dts", 100, "a b", wrong=["x"])
        del r["text"]
        a = report.agg([r])
        self.assertEqual(a["false_kw"], 0.0)


class TestLint(unittest.TestCase):
    def kinds(self, text, **kw):
        """Returns the set of violation kinds, so a test names what it caught."""
        counts, _words, hits = lint.lint(text, **kw)
        self.assertEqual(sum(counts.values()), len(hits))
        return {kind for kind, _ in hits}

    def test_clean_text_has_no_violations(self):
        self.assertEqual(self.kinds("Answer first. Cut filler, never content."),
                         set())

    def test_banned_modal_is_caught(self):
        self.assertIn("modal", self.kinds("You should use a transaction here."))

    def test_kill_list_word_is_caught(self):
        self.assertIn("kill-word",
                      self.kinds("This is a robust and comprehensive solution."))

    def test_passive_marker_is_caught(self):
        self.assertTrue(self.kinds("The file has been modified by the agent."))

    def test_over_cap_sentence_is_caught(self):
        long = "This " + "very " * 30 + "long sentence runs well past the cap."
        self.assertTrue(self.kinds(long, cap=20))

    def test_a_prohibition_is_not_read_as_a_violation(self):
        """`write X, never Y` names the banned word. It is not using it."""
        self.assertEqual(
            self.kinds("Write `check`, never verify, confirm, or validate."),
            set())

    def test_code_fence_content_is_exempt(self):
        self.assertEqual(
            self.kinds("Run it.\n\n```py\n# this should be robust\n```\n"),
            set())


class TestPromptCorpus(unittest.TestCase):
    def corpora(self):
        for name in os.listdir(os.path.join(ROOT, "bench")):
            if name.startswith("prompts") and name.endswith(".json"):
                yield name

    def test_every_corpus_is_valid_and_well_formed(self):
        seen_any = False
        for name in self.corpora():
            seen_any = True
            with open(os.path.join(ROOT, "bench", name)) as f:
                rows = json.load(f)
            self.assertIsInstance(rows, list, name)
            self.assertGreater(len(rows), 0, name)
            ids = [r["id"] for r in rows]
            self.assertEqual(len(ids), len(set(ids)), f"duplicate id in {name}")
            for r in rows:
                self.assertTrue(r.get("q", "").strip(), f"{name}:{r['id']} empty q")
                self.assertTrue(r.get("cat", "").strip(), f"{name}:{r['id']} no cat")
                self.assertIsInstance(r.get("must"), list, f"{name}:{r['id']}")
        self.assertTrue(seen_any, "no prompt corpora found")

    def test_every_must_pattern_compiles(self):
        import re
        for name in self.corpora():
            with open(os.path.join(ROOT, "bench", name)) as f:
                for r in json.load(f):
                    for pat in r["must"]:
                        try:
                            re.compile(pat)
                        except re.error as e:
                            self.fail(f"{name}:{r['id']} bad regex {pat!r}: {e}")


class TestAgenticTasks(unittest.TestCase):
    def rows(self):
        with open(os.path.join(ROOT, "bench", "agentic-tasks.json")) as f:
            return json.load(f)

    def test_corpus_is_well_formed(self):
        rows = self.rows()
        self.assertGreater(len(rows), 0)
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)), "duplicate task id")
        for r in rows:
            self.assertTrue(r.get("q", "").strip(), f"{r['id']} empty q")
            self.assertTrue(r.get("cat", "").strip(), f"{r['id']} no cat")
            self.assertIsInstance(r.get("edits"), bool, f"{r['id']} edits flag")

    def test_paths_named_in_tasks_exist_in_the_pinned_fixture(self):
        """A task naming a missing file measures the agent hunting, not writing."""
        import re
        pat = re.compile(r'\b(src/[\w/]+\.py|tests/[\w/]+\.py|[A-Z]+\.rst)')
        named = {m for r in self.rows() for m in pat.findall(r["q"])}
        self.assertTrue(named, "no file paths found in the task corpus")
        cache = os.path.join(ROOT, "bench", "out", "fixture")
        if not os.path.isdir(cache):
            self.skipTest("fixture not cloned yet; run agentic.py once")
        for path in sorted(named):
            self.assertTrue(os.path.exists(os.path.join(cache, path)),
                            f"task names a path absent from the fixture: {path}")

    def test_harness_imports_and_declares_a_pinned_commit(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "agentic", os.path.join(ROOT, "bench", "agentic.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual(len(m.COMMIT), 40, "fixture commit must be a full sha")
        self.assertTrue(m.REPO.startswith("https://"))


class TestArms(unittest.TestCase):
    def test_every_arm_exists_and_baseline_is_empty(self):
        d = os.path.join(ROOT, "bench", "arms")
        for name in ("baseline", "dts", "eli5", "caveman", "ste100"):
            p = os.path.join(d, name + ".txt")
            self.assertTrue(os.path.exists(p), f"missing arm: {name}")
            with open(p) as f:
                body = f.read()
            if name == "baseline":
                self.assertEqual(body.strip(), "", "baseline must be empty")
            else:
                self.assertTrue(body.strip(), f"{name} arm is empty")

    def test_competitor_arms_have_recorded_provenance(self):
        with open(os.path.join(ROOT, "bench", "arms", "PROVENANCE.md")) as f:
            prov = f.read().lower()
        for name in ("caveman", "ste100", "eli5"):
            self.assertIn(name, prov, f"{name} has no provenance entry")


if __name__ == "__main__":
    unittest.main()
