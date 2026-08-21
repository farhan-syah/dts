#!/usr/bin/env python3
"""Aggregate bench.py results into a comparison table.

Key metric is tok/fact: output tokens spent per required fact retained. Lower is
better. A standard that wins on raw tokens by dropping facts loses here.

Usage:
  ./report.py                     # reads out/results.json
  ./report.py out/full.json --by-cat
  ./report.py --missing dts     # show which facts an arm drops
"""
import argparse, json, os, statistics as st, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))


def agg(rows):
    ok = [r for r in rows if "error" not in r]
    if not ok:
        return None
    tok = [r["out_tok"] for r in ok]
    fac = sum(r["facts"] for r in ok)
    tot = sum(r["facts_total"] for r in ok)
    jr = [r for r in ok if "judge" in r]
    axes = jr[0].get("axes") or ["correct", "complete", "usable"] if jr else []
    a = {
        "n": len(ok), "err": len(rows) - len(ok),
        "tok": st.mean(tok), "sd": st.pstdev(tok) if len(tok) > 1 else 0.0,
        "chars": st.mean(r["chars"] for r in ok),
        "cov": 100.0 * fac / tot if tot else 0.0,
        "tpf": sum(tok) / fac if fac else float("inf"),
        "jn": len(jr),
    }
    if jr:
        a["axes"] = axes
        a["ax"] = {k: st.mean(r["judge"][k] for r in jr if k in r["judge"])
                   for k in axes}
        a["qual"] = st.mean(r["quality"] for r in jr)
        a["qmax"] = 5 * len(axes)
        qsum = sum(r["quality"] for r in jr)
        a["tpq"] = sum(r["out_tok"] for r in jr) / qsum if qsum else float("inf")
        # A false-claim COUNT falls when an answer simply makes fewer claims, so
        # a terse arm wins it for free. Two normalisations separate the two
        # causes: per 1000 words removes the length effect, and the share of
        # answers holding at least one false claim ignores volume entirely.
        nfalse = sum(len(r["judge"]["wrong_claims"]) for r in jr)
        words = sum(len(r.get("text", "").split()) for r in jr)
        a["false"] = nfalse / len(jr)
        a["false_kw"] = 1000.0 * nfalse / words if words else 0.0
        a["false_any"] = 100.0 * sum(
            1 for r in jr if r["judge"]["wrong_claims"]) / len(jr)
    return a


def table(title, groups, base_key, order):
    b = groups.get(base_key)
    judged = any(g and g.get("jn") for g in groups.values())
    axes = next((g["axes"] for g in groups.values() if g and g.get("axes")), [])
    print(f"\n{title}")
    hdr = (f"{'arm':<10}{'n':>4}{'out tok':>9}{'±sd':>7}{'vs base':>9}"
           f"{'facts%':>8}{'tok/fact':>10}")
    if judged:
        for k in axes:
            hdr += f"{k[:5]:>7}"
        hdr += (f"{'qual':>7}{'tok/qual':>10}{'eff':>8}{'false':>7}"
                f"{'f/kw':>7}{'f-any':>7}")
    print(hdr)
    for k in order:
        a = groups.get(k)
        if not a:
            continue
        d = f"{100*(a['tok']-b['tok'])/b['tok']:+.1f}%" if b else "-"
        row = (f"{k:<10}{a['n']:>4}{a['tok']:>9.0f}{a['sd']:>7.0f}{d:>9}"
               f"{a['cov']:>7.1f}%{a['tpf']:>10.1f}")
        if judged:
            if "qual" in a:
                e = (f"{100*(a['tpq']-b['tpq'])/b['tpq']:+.1f}%"
                     if b and "tpq" in b else "-")
                for k in axes:
                    row += f"{a['ax'].get(k, 0):>7.2f}"
                row += (f"{a['qual']:>7.2f}{a['tpq']:>10.1f}{e:>8}"
                        f"{a['false']:>7.2f}{a['false_kw']:>7.2f}"
                        f"{a['false_any']:>6.0f}%")
            else:
                row += (f"{'-':>7}" * len(axes)
                        + f"{'-':>7}{'-':>10}{'-':>8}{'-':>7}{'-':>7}{'-':>7}")
        print(row)
    print("  tok/fact = regex keyword coverage (weak: a bare noun counts).")
    if judged:
        print(f"  qual = {'+'.join(axes)}, 0-{5*len(axes)}.  "
              f"tok/qual = tokens per quality point (the real score).")
        print("  eff  = tok/qual vs baseline; negative is better.")
        print("  false = mean false claims per answer (rises with length).  "
              "f/kw = per 1000 words.  f-any = answers with 1 or more.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=os.path.join(ROOT, "out", "results.json"))
    ap.add_argument("--base", default="baseline")
    ap.add_argument("--by-cat", action="store_true")
    ap.add_argument("--missing", help="list unmet facts for this arm")
    ap.add_argument("--false", dest="false_", metavar="ARM",
                    help="list judge-flagged false claims for this arm")
    a = ap.parse_args()

    if not os.path.exists(a.path):
        sys.exit(f"no results at {a.path} — run bench.py first")
    d = json.load(open(a.path))
    rows = d["results"]
    # judge.py shuffles records, so first-appearance order is not stable.
    # Pin the baseline first, then sort, so tables read the same every run.
    arms = sorted({r["arm"] for r in rows})
    order = ([a.base] if a.base in arms else []) + [x for x in arms if x != a.base]

    by_arm = defaultdict(list)
    for r in rows:
        by_arm[r["arm"]].append(r)
    print(f"model={d['model']}  temp={d['temp']}  reps={d['reps']}  "
          f"elapsed={d['elapsed_s']}s")
    table("OVERALL", {k: agg(v) for k, v in by_arm.items()}, a.base, order)

    if a.by_cat:
        cats = sorted({r["cat"] for r in rows})
        for c in cats:
            g = defaultdict(list)
            for r in rows:
                if r["cat"] == c:
                    g[r["arm"]].append(r)
            table(f"CATEGORY: {c}", {k: agg(v) for k, v in g.items()}, a.base, order)

    if a.missing:
        print(f"\nUNMET FACTS — arm {a.missing}")
        miss = defaultdict(list)
        for r in rows:
            if r["arm"] == a.missing and "error" not in r:
                for m in r["missing"]:
                    miss[r["id"]].append(m)
        if not miss:
            print("  none — full coverage")
        for k in sorted(miss):
            print(f"  {k}: {', '.join(sorted(set(miss[k])))}")

    if a.false_:
        print(f"\nFALSE CLAIMS FLAGGED BY JUDGE — arm {a.false_}")
        n = 0
        for r in rows:
            if r["arm"] == a.false_ and r.get("judge", {}).get("wrong_claims"):
                for c in r["judge"]["wrong_claims"]:
                    print(f"  {r['id']}: {c}")
                    n += 1
        print(f"  ({n} total)" if n else "  none flagged")


if __name__ == "__main__":
    main()
