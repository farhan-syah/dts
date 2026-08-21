#!/usr/bin/env python3
"""Blind LLM-judge pass over bench.py results.

Regex fact-coverage cannot tell a keyword from a claim, so a telegraphic arm can
score well by emitting bare nouns. This pass reads each answer with no arm label
and scores it on correctness, completeness, and usability against an anchored
rubric, and lists any false statements it finds.

The judge is told explicitly that length is not quality. LLM judges reward
verbosity by default, which would bias every result toward the baseline arm.

Models are `provider:model` specs resolved through config.toml. Judge with a
model that did not write the answers, or self-preference bias inflates the
writing model's own scores.

Usage:
  ./judge.py                                    # first judge.models, out/results.json
  ./judge.py out/full.json --judge-model ollama:kimi-k3:cloud --jobs 3
  ./judge.py out/full.json --judge-model anthropic:claude-sonnet-5
"""
import argparse, json, os, random, sys, time
from concurrent.futures import ThreadPoolExecutor

import providers

ROOT = os.path.dirname(os.path.abspath(__file__))

AXES = {
    "correct": """correct — factual accuracy of what the answer actually asserts.
  5 every claim is true.
  3 mostly true, one minor error.
  1 a central claim is wrong.
  0 the answer asserts nothing checkable, or is mostly wrong.
  A bare list of nouns or fragments asserts nothing. Score it 0 or 1.""",

    "complete": """complete — does it cover what a competent engineer needs to act?
  5 every important point is present.
  3 the main point is present, supporting detail is missing.
  1 one fragment of the answer is present.
  0 the question is not answered.
  Naming a term without saying anything about it is not coverage.""",

    "usable": """usable — can the reader act on this immediately, with no rewriting?
  5 immediately actionable and unambiguous.
  3 usable after a re-read.
  1 the reader must reconstruct the meaning.
  0 unintelligible, or so terse it is ambiguous.""",

    "english": """english — is this fluent, grammatical, professional technical English?
  5 fluent and idiomatic. Reads as a competent technical writer wrote it.
  3 understandable, with awkward phrasing or a grammar slip.
  1 telegraphic or broken. Articles, verbs, or prepositions are dropped.
  0 not English sentences. Bare fragments or noun lists.
  Grade the writing only. A fluent answer that is wrong still scores 5 here and
  loses on correct.
  Terse is not broken. A short, grammatical, complete sentence scores 5.
  Bullets and tables are normal technical writing. Grade the prose inside them,
  never the fact that they are lists.""",
}

RULES = """Rules you must follow:
- Length is NOT quality. A short answer that is correct and complete scores
  HIGHER than a long one that says the same thing. Never reward verbosity.
- Never reward or punish tone, formatting, or warmth on its own.
- Judge the answer as written. Do not fill in what you assume the writer meant.
- wrong_claims lists each false statement verbatim. Empty array if none."""


def build_rubric(axes):
    """Compose the grading prompt from the selected axes."""
    unknown = [a for a in axes if a not in AXES]
    if unknown:
        raise ValueError(f"unknown axes {unknown}. Known: {sorted(AXES)}")
    body = "\n\n".join(AXES[a] for a in axes)
    contract = ", ".join(f'"{a}": 0' for a in axes)
    return (f"You grade one answer written for a professional software engineer.\n\n"
            f"Score {len(axes)} axes, 0 to 5 each.\n\n{body}\n\n{RULES}\n\n"
            f"Return exactly this JSON object, with these exact key names, "
            f"and nothing else:\n{{{contract}, \"wrong_claims\": []}}")


def extract_json(s):
    """Parse a JSON object out of a model reply.

    Models ignore structured-output schemas at different rates and providers
    expose them differently, so the rubric states the key contract in the prompt
    and this parses whatever comes back. glm-5.2 wraps its reply in a markdown
    fence, which makes a bare json.loads fail on the first character.
    """
    s = s.strip()
    if s.startswith("```"):
        s = s.split("```")[1]
        if s.lstrip().lower().startswith("json"):
            s = s.lstrip()[4:]
    i = s.find("{")
    if i < 0:
        raise ValueError(f"no JSON object in reply: {s[:120]!r}")
    depth, in_str, esc = 0, False, False
    for j, ch in enumerate(s[i:], i):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(s[i:j + 1])
    raise ValueError(f"unbalanced JSON in reply: {s[:120]!r}")


def judge_one(model, q, ans, timeout, cfg, rubric, axes):
    r = providers.complete(
        model, rubric,
        f"QUESTION:\n{q}\n\nANSWER:\n{ans}\n\nGrade the answer.",
        cfg=cfg, seed=7, temperature=0.0, max_tokens=1024, timeout=timeout,
        retries=1)
    s = extract_json(r.text)
    for k in axes:
        if k not in s:
            raise ValueError(f"judge omitted key {k!r}: {s}")
    s.setdefault("wrong_claims", [])
    if not isinstance(s["wrong_claims"], list):
        s["wrong_claims"] = [str(s["wrong_claims"])]
    return s


def run(a, cfg, prompts, rec, rubric):
    if "error" in rec or not rec.get("text"):
        return dict(rec, judge_error="no text")
    q = prompts[rec["id"]]
    for attempt in range(3):
        try:
            s = judge_one(a.judge_model, q, rec["text"], a.timeout, cfg,
                          rubric, a.axes)
            for k in a.axes:
                s[k] = max(0, min(5, int(s[k])))
            out = dict(rec)
            out["judge"] = s
            out["judge_model"] = a.judge_model
            out["axes"] = list(a.axes)
            out["quality"] = sum(s[k] for k in a.axes)
            return out
        except providers.QuotaError as e:
            print(f"\nABORT: {e}", file=sys.stderr)
            print("Quota does not refill mid-run. Nothing further was sent.", file=sys.stderr)
            os._exit(3)
        except Exception as e:
            if attempt == 2:
                return dict(rec, judge_error=f"{type(e).__name__}: {e}")
            time.sleep(2 * (attempt + 1))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=os.path.join(ROOT, "out", "results.json"))
    ap.add_argument("--config", default=providers.CONFIG)
    ap.add_argument("--prompts", help="corpus file (default: the one the run used)")
    ap.add_argument("--judge-model", help="provider:model (default: first judge.models)")
    ap.add_argument("--arms", nargs="+", help="limit to these arms")
    ap.add_argument("--ids", nargs="+", help="limit to these prompt ids")
    ap.add_argument("--cats", nargs="+", help="limit to these categories")
    ap.add_argument("--axes", nargs="+",
                    help=f"axes to score (default: judge.axes in config). "
                         f"Known: {', '.join(sorted(AXES))}")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    cfg = providers.load_config(a.config)
    if not a.judge_model:
        jm = cfg.get("judge", {}).get("models") or []
        if not jm:
            sys.exit("no --judge-model given and judge.models is empty in config.toml")
        a.judge_model = jm[0]
    a.axes = a.axes or cfg.get("judge", {}).get("axes") or [
        "correct", "complete", "usable", "english"]
    try:
        rubric = build_rubric(a.axes)
    except ValueError as e:
        sys.exit(str(e))

    if not os.path.exists(a.path):
        sys.exit(f"no results at {a.path} — run bench.py first")
    data = json.load(open(a.path))
    corpus = a.prompts or data.get("prompts") or "prompts.json"
    prompts = {p["id"]: p["q"] for p in
               json.load(open(os.path.join(ROOT, corpus)))}

    recs = data["results"]
    if a.arms:
        recs = [r for r in recs if r["arm"] in a.arms]
    if a.ids:
        recs = [r for r in recs if r["id"] in a.ids]
    if a.cats:
        recs = [r for r in recs if r.get("cat") in a.cats]
    if not recs:
        sys.exit("no records match the given --arms/--ids/--cats filters")
    # Shuffle so any judge drift over the run does not land on one arm.
    recs = list(recs)
    random.Random(42).shuffle(recs)

    out_path = a.out or a.path.replace(".json", "") + "-judged.json"
    print(f"judge={a.judge_model} axes={','.join(a.axes)} "
          f"cells={len(recs)} jobs={a.jobs}", flush=True)

    judged, done = [], 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for r in ex.map(lambda x: run(a, cfg, prompts, x, rubric), recs):
            judged.append(r)
            done += 1
            if "judge" in r:
                j = r["judge"]
                tag = " ".join(f"{k[:2]}{j[k]}" for k in a.axes)
                if j["wrong_claims"]:
                    tag += f"  {len(j['wrong_claims'])} false"
            else:
                tag = "JUDGE-ERR"
            print(f"[{done}/{len(recs)}] {r['arm']:<9}{r['id']:<7}{tag}", flush=True)

    data["results"] = judged
    data["judge_model"] = a.judge_model
    data["axes"] = list(a.axes)
    data["judge_elapsed_s"] = round(time.time() - t0, 1)
    json.dump(data, open(out_path, "w"), indent=1)
    errs = sum(1 for r in judged if "judge" not in r)
    print(f"\nwrote {out_path}  ({len(judged)-errs} ok, {errs} failed, "
          f"{time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
