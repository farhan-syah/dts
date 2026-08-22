#!/usr/bin/env bash
# Full DTS validation matrix. One command reproduces every published number.
#
# Writers: every model in bench.models. Judges: for each writer, the other two
# models. No model ever judges its own output, because self-preference inflated
# one arm by about 40% in an earlier run.
#
# Usage:
#   ./runall.sh              # reps=2, all arms, all 32 prompts
#   REPS=3 ./runall.sh       # more statistical power, more time
#   ./runall.sh --dry        # print the plan and exit
set -euo pipefail
cd "$(dirname "$0")"

REPS="${REPS:-2}"
JOBS="${JOBS:-3}"
STAMP="${STAMP:-$(date +%Y%m%d-%H%M)}"
DIR="out/run-$STAMP"

# Keep this in step with bench.models in config.toml. kimi-k3 is left out on
# purpose: it is the costliest model here and drains the shared session quota.
MODELS=(
  ollama:glm-5.2:cloud
  ollama:deepseek-v4-pro:cloud
  ollama:minimax-m3:cloud
)

short() { echo "$1" | sed 's|.*:||; s|^|x|' | sed 's|^x||' ; }
tag() { echo "$1" | sed 's|ollama:||; s|:cloud||; s|[^A-Za-z0-9]|-|g'; }

if [[ "${1:-}" == "--dry" ]]; then
  echo "reps=$REPS jobs=$JOBS out=$DIR"
  for m in "${MODELS[@]}"; do
    echo "  write $m"
    for j in "${MODELS[@]}"; do
      [[ "$j" == "$m" ]] && continue
      echo "    judge by $j"
    done
  done
  exit 0
fi

mkdir -p "$DIR"
echo "=== DTS full matrix — reps=$REPS jobs=$JOBS -> $DIR ==="
./providers.py >"$DIR/providers.txt" 2>&1 || {
  echo "provider check failed:"; cat "$DIR/providers.txt"; exit 1; }

for m in "${MODELS[@]}"; do
  wt=$(tag "$m")
  raw="$DIR/w-$wt.json"
  echo
  echo "--- WRITE  $m"
  ./bench.py --model "$m" --reps "$REPS" --jobs "$JOBS" --out "$raw" \
    >"$DIR/w-$wt.log" 2>&1
  tail -1 "$DIR/w-$wt.log"

  echo "--- LINT   $wt"
  ./lint.py --results "$raw" | tee "$DIR/lint-$wt.txt"

  for j in "${MODELS[@]}"; do
    [[ "$j" == "$m" ]] && continue
    jt=$(tag "$j")
    echo "--- JUDGE  $wt by $jt"
    ./judge.py "$raw" --judge-model "$j" --jobs "$JOBS" \
      --out "$DIR/j-$wt-by-$jt.json" >"$DIR/j-$wt-by-$jt.log" 2>&1
    tail -1 "$DIR/j-$wt-by-$jt.log"
  done
done

echo
echo "=== REPORTS ==="
for f in "$DIR"/j-*.json; do
  echo
  echo "### $(basename "$f" .json)"
  ./report.py "$f"
done | tee "$DIR/report.txt"

echo
echo "matrix complete: $DIR"
