#!/usr/bin/env python3
"""Measure DTS conformance as violations per 100 words.

The bench measures outcomes: tokens down, quality held. It cannot tell whether a
standard was followed or whether the model merely got shorter. This measures the
mechanism, and reports violations per 100 words so results compare against other
controlled-language benchmarks that use the same normalization.

DTS deliberately permits what ASD-STE100 forbids, because those rules cost
tokens: contractions stay, `e.g.` and `i.e.` stay, `ensure` stays, and articles
are not restored. Do not add those checks here.

Code spans, fenced blocks, and quoted error strings are exempt. A standard never
rewrites a verbatim span.

Usage:
  ./lint.py README.md src/main.rs
  ./lint.py --results out/full.json          # lint every answer, by arm
  ./lint.py --results out/full.json --detail dts
"""
import argparse, json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))

KILL = (r"simply|easily|seamless(?:ly)?|robust|powerful|comprehensive|elegant|"
        r"crucial|vital|essential|leverag(?:e|es|ing)|utiliz(?:e|es|ing)|delve|"
        r"unlock|empower|streamline|holistic|cutting-edge|best-in-class")
DEAD = (r"it is worth noting|worth noting that|important to note|keep in mind|"
        r"that said|at the end of the day|needless to say|as you can see|"
        r"I hope this helps|great question|you'?re absolutely right|sure thing")
WORDY = (r"\bin order to\b|\bprior to\b|\bsubsequent to\b|\bdue to the fact\b|"
         r"\bat this point in time\b|\bis able to\b|\bhas the ability to\b")
PREAMBLE = (r"^(sure|certainly|absolutely|of course|great|happy to|I'?d be happy|"
            r"let me (?:explain|help|start)|I'?ll help)")
TRAILING = (r"(let me know if|would you like me to|feel free to ask|"
            r"anything else|hope (?:that|this) helps)")

SYNONYM_SETS = [
    ("verify-verbs", r"\b(check|verify|confirm|validate|ensure)\b"),
    ("config-nouns", r"\b(config|configuration|settings|options)\b"),
    ("failure-nouns", r"\b(error|failure|issue|problem)\b"),
    ("dir-nouns", r"\b(directory|folder|dir)\b"),
]

# Eliding code to save tokens is a direct DTS violation: brevity governs prose
# only. Every pattern here REFERENCES content that should have been reproduced.
# A bare `/* ... */` is deliberately absent: in a fresh illustrative snippet an
# empty body is idiomatic, and nothing was dropped. Searched inside fenced blocks,
# where the other rules do not look.
ELISION = re.compile(

    r"\.\.\.\s*(?:rest|remaining|other|existing|unchanged|same as|snip)|"
    r"(?://|#)\s*(?:existing|unchanged|remainder|previous|omitted)\b|"
    r"(?://|#)\s*(?:rest|remaining)\b[^\n]{0,30}\b(?:unchanged|same|omitted|here|of)\b|"
    r"\[(?:\.\.\.|snip|truncated|unchanged)\]|"
    r"\bkeep (?:the )?(?:existing|rest|remaining)\b", re.I)

# Hedging identity, distinct from hedging confidence. `may cause` at least admits
# uncertainty. `the relevant handler` cannot be checked at all.
VAGUE = (r"\bthe (?:relevant|appropriate|corresponding|necessary|applicable|"
         r"desired|requisite|aforementioned) \w+|"
         r"\ba certain \w+|"
         r"\bthe (?:strongest|leading|nearest|obvious|main) (?:alternative|"
         r"competitor|option|candidate|choice)\b|"
         r"\bthe \w+ in question\b|"
         r"\bthe thing (?:that|which)\b")

RULES = [
    ("vague-reference", VAGUE),
    ("modal",       r"\b(should|would|may|might|could|shall)\b"),
    ("perfect",     r"\b(has|have|had) been\b|\bis to be\b|\bwas being\b"),
    ("semicolon",   r";"),
    ("kill-word",   rf"\b(?:{KILL})\b"),
    ("dead-phrase", DEAD),
    ("wordy",       WORDY),
    ("hedge-stack", r"(might|may|could|appears?|seems?)[^.]{0,30}"
                    r"(possibly|potentially|perhaps|likely)"),
    ("trailing-offer", TRAILING),
]

PROHIBIT = re.compile(r"\bnever\b|\binstead of\b|\bbanned\b|\brather than\b|"
                      r"\bdo not (?:use|write|say)\b|\bnot\s+[\w`]+\s*[,/]", re.I)
SKIP_MARK = re.compile(r"<!--\s*dts:\s*(?:no-lint|off)\s*-->")
CORE_MARK = re.compile(r"<!--\s*dts:\s*core\s*-->")
# Rules that are tuned for the terminal and break long-form genres.
AGENT_SURFACE = {"modal", "long-sentence", "long-list", "preamble"}
FENCE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`]*`")
QUOTED = re.compile(r"\"[^\"\n]{0,200}\"")


def strip_exempt(text):
    """Blank out spans a standard must never rewrite, keeping offsets stable."""
    def blank(m):
        return " " * (m.end() - m.start())
    t = FENCE.sub(blank, text)
    t = INLINE.sub(blank, t)
    return QUOTED.sub(blank, t)


def sentences(text):
    for s in re.split(r"(?<=[.!?])\s+|\n{2,}", text):
        s = s.strip()
        if s and not s.startswith(("|", "#", "-", "*", ">")):
            yield s


def lint(text, cap=20, row_cap=10):
    """Return (violations Counter, word count, detail list).

    A file carrying `<!-- dts:no-lint -->` is skipped. Rule references and
    wordlists must name the words they ban, so linting them reports the
    dictionary, not a defect.
    """
    if SKIP_MARK.search(text):
        return Counter(), len(strip_exempt(text).split()), []
    core_only = bool(CORE_MARK.search(text))
    clean = strip_exempt(text)
    words = len(clean.split())
    v, detail = Counter(), []

    for name, pat in RULES:
        for m in re.finditer(pat, clean, re.I):
            v[name] += 1
            detail.append((name, m.group(0).strip()[:60]))

    for m in ELISION.finditer(text):
        v["code-elision"] += 1
        detail.append(("code-elision", m.group(0).strip()[:60]))

    for s in sentences(clean):
        n = len(s.split())
        if n > cap:
            v["long-sentence"] += 1
            detail.append(("long-sentence", f"{n}w: {s[:60]}"))

    if re.match(PREAMBLE, text.strip(), re.I):
        v["preamble"] += 1
        detail.append(("preamble", text.strip()[:60]))

    # Row cap. DTS sets no hard row limit: it stops a list when the next row
    # adds nothing actionable. Ten is the point past which the question is
    # usually the wrong shape, so this flags a runaway, not a seven-row table.
    #
    # Count data rows, not lines: a markdown table spends two lines on its header
    # and its |---| separator, so counting lines flags a 6-row table as 8 and
    # reports a violation that is not there.
    def flush(run):
        if not run:
            return
        table = run[0].lstrip().startswith("|")
        rows = len(run)
        if table:
            rows -= sum(1 for l in run if re.match(r"\s*\|[\s:|-]*\|\s*$", l))
            rows -= 1  # header row
        if rows > row_cap:
            v["long-list"] += 1
            detail.append(("long-list",
                           f"{rows} {'table rows' if table else 'items'}"))

    run = []
    for line in text.splitlines():
        if re.match(r"\s*(?:[-*+]\s|\d+[.)]\s|\|)", line):
            run.append(line)
        else:
            flush(run)
            run = []
    flush(run)

    # Naming a banned word inside a prohibition is not rotation. A rule that says
    # "write `check`, never verify" uses both words on purpose, so lines carrying
    # a prohibition marker are excluded from the synonym scan.
    scan = "\n".join(l for l in clean.splitlines() if not PROHIBIT.search(l))
    for name, pat in SYNONYM_SETS:
        found = {m.group(1).lower() for m in re.finditer(pat, scan, re.I)}
        if len(found) > 1:
            v["synonym-rotation"] += 1
            detail.append(("synonym-rotation", f"{name}: {'/'.join(sorted(found))}"))

    if core_only:
        for k in AGENT_SURFACE:
            v.pop(k, None)
        detail = [d for d in detail if d[0] not in AGENT_SURFACE]
    return v, words, detail


def per100(v, words):
    return round(100.0 * sum(v.values()) / words, 2) if words else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="files to lint")
    ap.add_argument("--results", help="lint every answer in a bench results file")
    ap.add_argument("--detail", metavar="ARM_OR_FILE",
                    help="list individual violations for this arm or file")
    ap.add_argument("--cap", type=int, default=20, help="sentence word cap")
    ap.add_argument("--row-cap", type=int, default=10, dest="row_cap")
    a = ap.parse_args()

    if not a.files and not a.results:
        ap.error("give files to lint, or --results out/<file>.json")

    if a.results:
        d = json.load(open(a.results))
        agg = {}
        for r in d["results"]:
            if "error" in r or not r.get("text"):
                continue
            v, w, det = lint(r["text"], a.cap, a.row_cap)
            s = agg.setdefault(r["arm"], [Counter(), 0, 0, []])
            s[0] += v
            s[1] += w
            s[2] += 1
            if a.detail == r["arm"]:
                s[3] += det
        print(f"{'arm':<12}{'answers':>8}{'words':>9}{'viol':>7}{'per 100w':>10}"
              f"   top rules")
        for arm in sorted(agg, key=lambda k: per100(agg[k][0], agg[k][1])):
            v, w, n, _ = agg[arm]
            top = ", ".join(f"{k}:{c}" for k, c in v.most_common(3))
            print(f"{arm:<12}{n:>8}{w:>9}{sum(v.values()):>7}"
                  f"{per100(v, w):>10.2f}   {top}")
        if a.detail and a.detail in agg:
            print(f"\nVIOLATIONS — {a.detail}")
            for name, txt in agg[a.detail][3][:60]:
                print(f"  {name:<18}{txt}")
            extra = len(agg[a.detail][3]) - 60
            if extra > 0:
                print(f"  ... {extra} more")
        return

    worst = 0
    for f in a.files:
        if not os.path.exists(f):
            print(f"{f}: not found", file=sys.stderr)
            worst = 1
            continue
        v, w, det = lint(open(f, errors="replace").read(), a.cap, a.row_cap)
        p = per100(v, w)
        print(f"{f}: {sum(v.values())} violations, {w} words, {p} per 100w")
        for name, c in v.most_common():
            print(f"    {name:<18}{c}")
        if a.detail in (f, "all"):
            for name, txt in det:
                print(f"      {name:<16}{txt}")
        if sum(v.values()):
            worst = max(worst, 1)
    sys.exit(worst)


if __name__ == "__main__":
    main()
