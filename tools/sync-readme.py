#!/usr/bin/env python3
"""Keep the pasteable block in README.md identical to rules/dts.md.

A copied block drifts. RTK ended up with 964 bytes in one agent config, a
hand-written 346-byte summary in another, and nothing in a third. This
regenerates the README copy from the single source, and `--check` fails when the
two differ, so CI catches drift instead of a reader.

Usage:
  ./tools/sync-readme.py
  ./tools/sync-readme.py --check
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "<!-- dts:readme-start -->"
END = "<!-- dts:readme-end -->"


def build():
    rules = open(os.path.join(ROOT, "rules/dts.md")).read().strip()
    return (f"{START}\n\n```markdown\n<!-- dts:start -->\n{rules}\n"
            f"<!-- dts:end -->\n```\n\n{END}")


def main():
    check = "--check" in sys.argv
    p = os.path.join(ROOT, "README.md")
    s = open(p).read()
    want = build()
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pat.search(s):
        sys.exit(f"markers {START} / {END} not found in README.md")
    new = pat.sub(lambda _: want, s, count=1)
    if new == s:
        print("README block matches rules/dts.md")
        return
    if check:
        sys.exit("README block has drifted. Run ./tools/sync-readme.py")
    open(p, "w").write(new)
    print("README block regenerated from rules/dts.md")


if __name__ == "__main__":
    main()
