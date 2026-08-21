#!/usr/bin/env python3
"""Write or remove the DTS rules block inside an agent memory file.

A memory file belongs to the user, so this never overwrites one. The block lives
between markers. Reinstalling replaces only what is between them, and everything
the user wrote outside them survives untouched.

Called by install.sh. Usable directly:
  python3 install.py write  ~/.claude/CLAUDE.md rules/dts.md
  python3 install.py remove ~/.claude/CLAUDE.md
"""
import os, re, sys

BEGIN = "<!-- dts:start -->"
END = "<!-- dts:end -->"
BLOCK = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)

# Two forms of prior install get adopted rather than duplicated. An older marker
# pair from before the namespace was unified, and a hand paste with no markers at
# all. Without this an upgrade leaves two copies that drift apart.
OLD_MARKERS = re.compile(
    r"<!--\s*dts:begin\s*-->.*?<!--\s*dts:end\s*-->\n?", re.S)
LEGACY = re.compile(r"^## Output Standard \(DTS[^)]*\).*?(?=^## |\Z)", re.S | re.M)


def read(path):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def write(path, rules_path):
    body = read(rules_path).strip()
    if not body:
        sys.exit(f"empty rules file: {rules_path}")
    block = f"{BEGIN}\n{body}\n{END}\n"
    cur = read(path)

    if BLOCK.search(cur):
        new = BLOCK.sub(block, cur, count=1)
        action = "updated"
    elif OLD_MARKERS.search(cur):
        new = OLD_MARKERS.sub(block, cur, count=1)
        action = "migrated from the old marker names"
    elif LEGACY.search(cur):
        new = LEGACY.sub(block, cur, count=1)
        action = "adopted an unmarked block"
    elif cur.strip():
        new = cur.rstrip() + "\n\n" + block
        action = "appended"
    else:
        new = block
        action = "created"

    if new != cur:
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    print(f"      {action}")


def remove(path):
    cur = read(path)
    new = BLOCK.sub("", cur)
    if new == cur:
        print("      nothing to remove")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(new.rstrip() + "\n")
    print("      removed")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "write":
        if len(sys.argv) < 4:
            sys.exit("write needs a rules file")
        write(path, sys.argv[3])
    elif cmd == "remove":
        remove(path)
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
