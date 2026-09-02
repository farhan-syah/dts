<!-- dts:no-lint -->

# DTS self-audit

Run these before delivering any persisted text. `$F` is the target file.

## Grep patterns

```sh
# Perfect tense and passive scaffolding
grep -nEi '\b(has|have|had) been\b|\bis to be\b|\bwas being\b' "$F"

# Banned modals
grep -nEi '\b(should|would|may|might|could|shall)\b' "$F"

# Kill-list
grep -nEi '\b(simply|easily|seamless(ly)?|robust|powerful|comprehensive|elegant|crucial|vital|essential|leverage|utiliz(e|es|ing)|delve|unlock|empower|streamline|holistic)\b' "$F"

# Dead phrases
grep -nEi 'worth noting|important to note|keep in mind|that said|at the end of the day|as you can see|I hope this helps|great question' "$F"

# Wordy connectives
grep -nEi '\bin order to\b|\bprior to\b|\bdue to the fact\b|\bat this point in time\b|\bis able to\b|\bhas the ability to\b' "$F"

# Semicolons
grep -n ';' "$F"

# Hedge stacks (two qualifiers in one clause)
grep -nEi '(might|may|could|appears?|seems?)[^.]{0,30}(possibly|potentially|perhaps|likely)' "$F"
```

## Sentence-length check

Flags every sentence over the cap. Skips fenced code blocks and table rows.

````sh
awk -v CAP=20 '
function flush(  n,i,w,s,t,b) {
  if (buf == "") return
  b = buf; buf = ""
  gsub(/`[^`]*`/, "X", b)
  n = split(b, s, /[.!?]+[ \t]|[.!?]+$/)
  for (i = 1; i <= n; i++) {
    w = split(s[i], t, " ")
    if (w > CAP) printf "%s:%d: %d words: %s\n", FILENAME, ln, w, s[i]
  }
}
FNR==1 { flush(); fm = 0; c = 0; if ($0 ~ /^---$/) { fm = 1; next } }
fm && /^---$/ { fm = 0; next }
fm { next }
/^```/ { flush(); c = !c; next }
c { next }
/^[ \t]*$/ || /^\|/ || /^#/ || /^[ \t]*([-*+]|[0-9]+[.)])[ \t]/ {
  flush()
  if ($0 ~ /^[ \t]*([-*+]|[0-9]+[.)])[ \t]/) { ln = FNR; buf = $0 }
  next
}
{ if (buf == "") ln = FNR; buf = (buf == "" ? $0 : buf " " $0) }
END { flush() }
' "$F"
````

Pass `-v CAP=15` when auditing directives, subagent prompts, or CLI help.

## Pass condition

Every hit is fixed or is a deliberate quotation of external text. Quoted error strings, code identifiers, and cited source material are exempt — DTS never rewrites a verbatim span.
