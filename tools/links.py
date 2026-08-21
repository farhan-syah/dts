#!/usr/bin/env python3
"""Check Markdown links: unresolvable targets and malformed syntax.

A checker that only validates links it can parse will miss the worst kind. When
`[LICENSE](LICENSE)` degrades to `LICENSE[LICENSE]`, the link regex no longer
matches, so a naive checker reports zero problems on a broken page. This looks
for both.

Fenced code blocks are skipped, so shell and awk snippets containing brackets
never register as broken links.

Exits non-zero when anything fails, so it works as a pre-publish gate.

Usage:
  ./links.py ../README.md
  ./links.py $(git ls-files '*.md')
"""
import os, re, sys

FENCE = re.compile(r"^\s*(```|~~~)")
LINK = re.compile(r"\[([^\]^]*?)\]\(([^)]*)\)")
# `text[target]` — a link whose parentheses were lost.
LOST_PARENS = re.compile(r"(?<![\[\s!])\w\[[^\]\n]+\](?!\()")
# `[text] (target)` — a space that stops it rendering.
SPLIT = re.compile(r"\][ \t]+\(")
EMPTY = re.compile(r"\[[^\]\n]*\]\(\s*\)")
SKIP = ("http://", "https://", "mailto:", "#")


def check(path):
    problems = []
    base = os.path.dirname(os.path.abspath(path))
    fence = None
    total = 0
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        m = FENCE.match(line)
        if m:
            fence = None if fence else m.group(1)
            continue
        if fence:
            continue

        for pat, why in ((LOST_PARENS, "lost parentheses"),
                         (SPLIT, "space between ] and ("),
                         (EMPTY, "empty target")):
            for mo in pat.finditer(line):
                problems.append((n, why, mo.group(0).strip()))

        for mo in LINK.finditer(line):
            target = mo.group(2).strip()
            if not target or target.startswith(SKIP):
                continue
            total += 1
            resolved = os.path.normpath(os.path.join(base, target.split("#")[0]))
            if not os.path.exists(resolved):
                problems.append((n, "target not found", target))
    return total, problems


def main():
    paths = sys.argv[1:]
    if not paths:
        sys.exit(__doc__)
    checked = failed = 0
    for p in paths:
        if not os.path.exists(p):
            print(f"  MISSING FILE {p}")
            failed += 1
            continue
        total, problems = check(p)
        checked += total
        for n, why, txt in problems:
            print(f"  {p}:{n}: {why}: {txt}")
            failed += 1
    print(f"{checked} local links checked, {failed} problem(s)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
