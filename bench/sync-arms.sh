#!/usr/bin/env bash
# Rebuild bench/arms/dts.txt from the files this repo actually ships.
#
# The arm must never be generated from a personal agent config. A personal file
# carries overlays that DTS does not ship, so the benchmark would measure
# something no user receives.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
style = open("output-styles/dts.md").read().split("---", 2)[2].strip()
rules = open("rules/dts.md").read()
block = "\n".join(l for l in rules.strip().split("\n") if l.startswith("-"))
open("bench/arms/dts.txt", "w").write(style + "\n\n" + block + "\n")
print("bench/arms/dts.txt rebuilt from output-styles/ and rules/")
PY
