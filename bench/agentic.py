#!/usr/bin/env python3
"""Measure a writing standard inside a real agent loop, not on a single answer.

The single-turn benchmark asks one question and counts the reply. That is the
setting a compression standard flatters itself in. A real session reads files,
runs tools, and takes several turns, and a terse instruction can cost turns it
saves in prose. Ponytail's own benchmark found `caveman` cut its single-shot
reply and still spent 7% MORE tokens driving an agent. This measures that.

Each trial gets a pristine copy of a pinned real repository. The arm is
installed the way a user installs it, as a rules block in the project memory
file, so the always-on input cost is measured too and not assumed away.

Usage:
  ./agentic.py --list
  ./agentic.py --arms baseline dts --reps 2 --model haiku
  ./agentic.py --ids ag01 ag03 --arms baseline dts --out out/ag.json
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
BEGIN = "<!-- dts:start -->"
END = "<!-- dts:end -->"

REPO = "https://github.com/pallets/itsdangerous"
COMMIT = "672971d66a2ef9f85151e53283113f33d642dabd"


def fixture(cache):
    """Clone the pinned repo once. Every trial copies from here."""
    if os.path.isdir(os.path.join(cache, ".git")):
        return cache
    os.makedirs(os.path.dirname(cache) or ".", exist_ok=True)
    subprocess.run(["git", "clone", "-q", REPO, cache], check=True)
    subprocess.run(["git", "-C", cache, "checkout", "-q", COMMIT], check=True)
    return cache


def prepare(cache, arm_body):
    """A throwaway working copy with the arm installed as a project memory file."""
    d = tempfile.mkdtemp(prefix="dts-agentic-")
    work = os.path.join(d, "repo")
    shutil.copytree(cache, work)
    if arm_body.strip():
        with open(os.path.join(work, "CLAUDE.md"), "w") as f:
            f.write(f"{BEGIN}\n{arm_body.strip()}\n{END}\n")
    return d, work


def diffstat(work):
    r = subprocess.run(["git", "-C", work, "diff", "--numstat"],
                       capture_output=True, text=True)
    added = removed = 0
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0])
            removed += int(parts[1])
    # CLAUDE.md is ours, never the agent's work.
    untracked = [f for f in subprocess.run(
        ["git", "-C", work, "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True).stdout.split() if f != "CLAUDE.md"]
    return added, removed, untracked


def run_cell(a, cache, arm, arm_body, task, rep):
    d, work = prepare(cache, arm_body)
    base = dict(arm=arm, id=task["id"], cat=task["cat"], rep=rep)
    try:
        t0 = time.time()
        p = subprocess.run(
            ["claude", "-p", task["q"], "--output-format", "json",
             "--model", a.model, "--permission-mode", "acceptEdits"],
            cwd=work, capture_output=True, text=True, timeout=a.timeout)
        wall = time.time() - t0
        if p.returncode != 0:
            return dict(base, error=f"exit {p.returncode}: {p.stderr[-300:]}")
        try:
            r = json.loads(p.stdout)
        except json.JSONDecodeError:
            return dict(base, error=f"unparseable reply: {p.stdout[:300]}")
        if r.get("is_error"):
            return dict(base, error=f"agent error: {str(r.get('result'))[:300]}")

        u = r.get("usage", {}) or {}
        added, removed, untracked = diffstat(work)
        return dict(
            base,
            out_tok=u.get("output_tokens", 0),
            in_tok=u.get("input_tokens", 0),
            cache_create=u.get("cache_creation_input_tokens", 0),
            cache_read=u.get("cache_read_input_tokens", 0),
            turns=r.get("num_turns", 0),
            cost=r.get("total_cost_usd", 0.0),
            duration_ms=r.get("duration_ms", 0),
            wall_s=round(wall, 1),
            added=added, removed=removed, untracked=untracked,
            edited=bool(added or removed or untracked),
            expected_edit=task.get("edits", False),
            text=r.get("result", "") or "",
            chars=len(r.get("result", "") or ""),
        )
    except subprocess.TimeoutExpired:
        return dict(base, error=f"timeout after {a.timeout}s")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", nargs="+", default=["baseline", "dts"])
    ap.add_argument("--ids", nargs="+", help="run only these task ids")
    ap.add_argument("--cats", nargs="+", help="run only these categories")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--tasks", default="agentic-tasks.json")
    ap.add_argument("--cache", default=os.path.join(ROOT, "out", "fixture"))
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "agentic.json"))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    tasks = json.load(open(os.path.join(ROOT, a.tasks)))
    if a.ids:
        tasks = [t for t in tasks if t["id"] in a.ids]
    if a.cats:
        tasks = [t for t in tasks if t["cat"] in a.cats]

    if a.list:
        arms = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, "arms"))
                      if f.endswith(".txt"))
        print("arms:  " + " ".join(arms))
        print(f"repo:  {REPO} @ {COMMIT[:7]}")
        print(f"tasks ({len(tasks)}):")
        for t in tasks:
            edit = "edits" if t.get("edits") else "read-only"
            print(f"  {t['id']}  {t['cat']:<8} {edit:<10} {t['q'][:60]}")
        return

    if not shutil.which("claude"):
        sys.exit("claude CLI not on PATH")

    bodies = {}
    for name in a.arms:
        p = os.path.join(ROOT, "arms", f"{name}.txt")
        if not os.path.exists(p):
            sys.exit(f"no such arm: {p}")
        bodies[name] = open(p).read()

    cache = fixture(a.cache)
    cells = [(arm, bodies[arm], t, rep)
             for rep in range(a.reps) for t in tasks for arm in a.arms]
    total = len(cells)
    print(f"model={a.model} arms={len(a.arms)} tasks={len(tasks)} "
          f"reps={a.reps} -> {total} sessions")

    results, done = [], 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for r in ex.map(lambda c: run_cell(a, cache, *c), cells):
            results.append(r)
            done += 1
            if "error" in r:
                tag = "ERR " + r["error"][:60]
            else:
                tag = (f"{r['out_tok']:>6}o {r['turns']:>2}t "
                       f"{r['cache_read']:>7}cr {r['wall_s']:>5}s"
                       + ("  edited" if r["edited"] else ""))
            print(f"[{done}/{total}] {r['arm']:<9}{r['id']:<7}{tag}", flush=True)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"model": a.model, "repo": REPO, "commit": COMMIT,
               "reps": a.reps, "tasks": a.tasks,
               "elapsed_s": round(time.time() - t0, 1), "results": results},
              open(a.out, "w"), indent=1)
    errs = sum(1 for r in results if "error" in r)
    print(f"\nwrote {a.out}  ({total - errs} ok, {errs} failed, "
          f"{round(time.time() - t0, 1)}s)")


if __name__ == "__main__":
    main()
