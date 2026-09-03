#!/usr/bin/env python3
"""Flag every sentence over the DTS word cap.

Mirrors the awk in skills/dts/references/check.md, for hosts with no native
awk. Skips frontmatter, fenced code in either marker, headings, and table
rows. Scores each list item alone. Buffers a wrapped paragraph, so a sentence
split over source lines is scored whole, and reports the line the paragraph
starts on.

Exits non-zero when a sentence is over the cap, so it works as a CI gate. The
awk exits 0 either way, because a shell audit is read by a person.

Usage:
  ./sentence-cap.py --cap 20 ../README.md
  ./sentence-cap.py --cap 15 $(git ls-files '*.md')
"""
import argparse, os, re, sys

INLINE = re.compile(r"`[^`]*`")
SENTENCE = re.compile(r"[.!?]+[ \t]|[.!?]+$")
# awk splits a record on space, tab and newline. Splitting on every Unicode
# space instead counts a non-breaking space as a word break, and a line pasted
# from the web then scores higher here than under the awk.
WORD = re.compile(r"[^ \t\n]+")
LIST_ITEM = re.compile(r"^[ \t]*([-*+]|[0-9]+[.)])[ \t]")
SKIP = re.compile(r"^[ \t]*$|^\||^#")
# A fence marker takes up to three spaces of indent, then three or more
# backticks or tildes. Four spaces make an indented code block, where the
# marker is content, not a fence.
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
# awk's sub(/\r$/, "") removes one carriage return, never a run of them.
CR = re.compile(r"\r$")


class Buffer:
    """One paragraph, with the file and line it started on."""

    def __init__(self):
        self.text, self.path, self.line = "", "", 0

    def start(self, path, line, text):
        self.text, self.path, self.line = text, path, line

    def add(self, text):
        self.text = text if not self.text else self.text + " " + text

    def flush(self, cap):
        """Return (path, line, words, sentence) for each sentence over cap."""
        if not self.text:
            return []
        body, self.text = INLINE.sub("X", self.text), ""
        hits = []
        for sentence in SENTENCE.split(body):
            words = len(WORD.findall(sentence))
            if words > cap:
                hits.append((self.path, self.line, words, sentence))
        return hits


def violations(lines, path, cap):
    """Yield every over-cap sentence in one file's lines."""
    buf = Buffer()
    frontmatter = False
    open_len, open_mark = 0, ""

    for number, raw in enumerate(lines, 1):
        line = CR.sub("", raw)

        if number == 1 and line == "---":
            frontmatter = True
            continue
        if frontmatter:
            if line == "---":
                frontmatter = False
            continue

        marker = FENCE.match(line)
        if marker:
            yield from buf.flush(cap)
            run, rest = marker.group(1), marker.group(2)
            if not open_len:
                open_len, open_mark = len(run), run[0]
            # A fence closes only on the same character, at least as long,
            # and bare.
            elif (run[0] == open_mark and len(run) >= open_len
                    and not rest.strip()):
                open_len, open_mark = 0, ""
            continue
        if open_len:
            continue
        if SKIP.search(line) or LIST_ITEM.search(line):
            yield from buf.flush(cap)
            if LIST_ITEM.search(line):
                buf.start(path, number, line)
            continue

        if not buf.text:
            buf.start(path, number, line)
        else:
            buf.add(line)

    yield from buf.flush(cap)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="files to check")
    ap.add_argument("--cap", type=int, default=20, help="sentence word cap")
    a = ap.parse_args()

    # Windows encodes a redirected stdout with the locale codepage, so an arrow
    # or a CJK character in a flagged sentence raises UnicodeEncodeError there.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    worst = 0
    for f in a.files:
        if not os.path.exists(f):
            print(f"{f}: not found", file=sys.stderr)
            worst = 1
            continue
        # errors="replace" matches bench/lint.py. awk reads bytes and never
        # fails on a latin-1 file, so neither does this.
        with open(f, encoding="utf-8", errors="replace", newline="") as handle:
            lines = handle.read().split("\n")
        for name, line, words, sentence in violations(lines, f, a.cap):
            print(f"{name}:{line}: {words} words: {sentence}")
            worst = 1
    sys.exit(worst)


if __name__ == "__main__":
    main()
