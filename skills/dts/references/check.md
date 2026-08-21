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
awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} f{next}
/^```/{c=!c;next} c||/^\|/||/^ *$/{next}
{gsub(/`[^`]*`/,"X"); n=split($0,s,/[.!?]+[ \t]|[.!?]+$/);
 for(i=1;i<=n;i++){w=split(s[i],t," "); if(w>20) printf "%s:%d: %d words: %s\n",FILENAME,NR,w,s[i]}}' "$F"
````

Change `w>20` to `w>15` when auditing directives, subagent prompts, or CLI help.

## Pass condition

Every hit is fixed or is a deliberate quotation of external text. Quoted error strings, code identifiers, and cited source material are exempt — DTS never rewrites a verbatim span.
