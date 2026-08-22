#!/usr/bin/env python3
"""Measure output-token cost and fact retention of writing standards.

Each arm is a system prompt. Each prompt carries `must` regexes naming facts a
complete answer contains. A standard that saves tokens by dropping facts scores
worse on tokens-per-fact, so brevity alone cannot win.

Models are `provider:model` specs resolved through config.toml. Run
`./providers.py` to see which providers are reachable.

Usage:
  ./bench.py --model claude:opus --arms baseline dts    # Opus 5, no API key
  ./bench.py --model ollama:deepseek-v4-pro:cloud --reps 3 --out out/ds.json
  ./bench.py                                     # first bench.models, all arms
  ./bench.py --ids enum01 des02 --arms baseline dts   # one cluster
"""
import argparse, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import providers

ROOT = os.path.dirname(os.path.abspath(__file__))


def coverage(text, musts):
    hits = [bool(re.search(p, text, re.I)) for p in musts]
    return sum(hits), len(hits), [m for m, h in zip(musts, hits) if not h]


def run_cell(args, cfg, arm, sys_prompt, p, rep):
    try:
        r = providers.complete(
            args.model, sys_prompt, p["q"], cfg=cfg,
            seed=args.seed_base + rep, temperature=args.temp,
            max_tokens=args.max_tokens, timeout=args.timeout)
    except providers.QuotaError as e:
        print(f"\nABORT: {e}", file=sys.stderr)
        print("Quota does not refill mid-run. Nothing further was sent.", file=sys.stderr)
        os._exit(3)
    except providers.ProviderError as e:
        return {"arm": arm, "id": p["id"], "cat": p["cat"], "rep": rep,
                "model": args.model, "error": str(e)}
    got, tot, missing = coverage(r.text, p["must"])
    extra = {} if getattr(r, "deterministic", True) else {"unseeded": True}
    return {
        **extra,
        "arm": arm, "id": p["id"], "cat": p["cat"], "rep": rep,
        "model": args.model,
        "out_tok": r.out_tok, "in_tok": r.in_tok,
        "chars": len(r.text), "words": len(r.text.split()),
        "facts": got, "facts_total": tot, "missing": missing,
        "usage": r.usage(),
        "text": r.text,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=providers.CONFIG)
    ap.add_argument("--prompts", default="prompts.json",
                    help="prompt corpus file (default: prompts.json)")
    ap.add_argument("--model", help="provider:model (default: first bench.models)")
    ap.add_argument("--arms", nargs="+", help="default: bench.arms from config")
    ap.add_argument("--n", type=int, default=0, help="limit prompts (0 = all)")
    ap.add_argument("--ids", nargs="+", help="run only these prompt ids")
    ap.add_argument("--cats", nargs="+", help="run only these categories")
    ap.add_argument("--list", action="store_true",
                    help="print available arms, categories, and prompt ids, then exit")
    ap.add_argument("--reps", type=int, default=1, help="repeats per cell")
    ap.add_argument("--jobs", type=int, help="default: run.jobs from config")
    ap.add_argument("--temp", type=float)
    ap.add_argument("--seed-base", type=int, dest="seed_base")
    ap.add_argument("--max-tokens", type=int, dest="max_tokens")
    ap.add_argument("--timeout", type=int)
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "results.json"))
    a = ap.parse_args()

    cfg = providers.load_config(a.config)
    run = cfg.get("run", {})
    bench = cfg.get("bench", {})
    if not a.model:
        models = bench.get("models") or []
        if not models:
            sys.exit("no --model given and bench.models is empty in config.toml")
        a.model = models[0]
    a.arms = a.arms or bench.get("arms") or ["baseline", "dts"]
    a.jobs = a.jobs or run.get("jobs", 2)
    a.temp = run.get("temperature", 0.2) if a.temp is None else a.temp
    a.seed_base = a.seed_base or run.get("seed_base", 1000)
    a.max_tokens = a.max_tokens or run.get("max_tokens", 4096)
    a.timeout = a.timeout or run.get("timeout_s", 240)

    prompts = json.load(open(os.path.join(ROOT, a.prompts)))

    if a.list:
        arm_files = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, "arms"))
                           if f.endswith(".txt"))
        print("arms:   " + " ".join(arm_files))
        print("models: " + " ".join(bench.get("models", [])))
        cats = {}
        for p in prompts:
            cats.setdefault(p["cat"], []).append(p["id"])
        print(f"\nprompts ({len(prompts)} in {len(cats)} categories):")
        for c in sorted(cats):
            print(f"  {c:<12}{' '.join(cats[c])}")
        return

    if a.cats:
        want = set(a.cats)
        known = {p["cat"] for p in prompts}
        if want - known:
            sys.exit(f"unknown categories: {sorted(want - known)}. "
                     f"Known: {sorted(known)}")
        prompts = [p for p in prompts if p["cat"] in want]
    if a.ids:
        want = set(a.ids)
        prompts = [p for p in prompts if p["id"] in want]
        missing = want - {p["id"] for p in prompts}
        if missing:
            sys.exit(f"unknown prompt ids: {sorted(missing)}")
    if a.n:
        prompts = prompts[:a.n]
    arms = {}
    for name in a.arms:
        path = os.path.join(ROOT, "arms", f"{name}.txt")
        if not os.path.exists(path):
            sys.exit(f"missing arm file: {path}")
        arms[name] = open(path).read()

    cells = [(arm, arms[arm], p, rep)
             for rep in range(a.reps) for p in prompts for arm in a.arms]
    total = len(cells)
    print(f"model={a.model} arms={len(arms)} prompts={len(prompts)} "
          f"reps={a.reps} cells={total} jobs={a.jobs}", flush=True)

    results, done = [], 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for r in ex.map(lambda c: run_cell(a, cfg, *c), cells):
            results.append(r)
            done += 1
            tag = "ERR" if "error" in r else f"{r['out_tok']}t {r['facts']}/{r['facts_total']}f"
            print(f"[{done}/{total}] {r['arm']:<9}{r['id']:<7}{tag}", flush=True)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"model": a.model, "temp": a.temp, "reps": a.reps,
               "prompts": a.prompts, "max_tokens": a.max_tokens,
               "elapsed_s": round(time.time() - t0, 1), "results": results},
              open(a.out, "w"), indent=1)
    errs = sum(1 for r in results if "error" in r)
    print(f"\nwrote {a.out}  ({total - errs} ok, {errs} failed, "
          f"{time.time() - t0:.0f}s)")
    if errs:
        print("first errors:")
        for r in results:
            if "error" in r:
                print(f"  {r['arm']}/{r['id']}: {r['error']}")
                break


if __name__ == "__main__":
    main()
