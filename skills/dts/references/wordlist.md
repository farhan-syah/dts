<!-- dts:no-lint -->

# DTS wordlist

## Kill on sight

Delete these. They add tokens and no information.

`simply`, `just` (as intensifier), `easily`, `seamless`, `seamlessly`, `robust`, `powerful`, `comprehensive`, `elegant`, `crucial`, `vital`, `essential`, `significant`, `leverage`, `utilize`, `delve`, `navigate` (as metaphor), `unlock`, `empower`, `streamline`, `holistic`, `cutting-edge`, `best-in-class`, `game-changing`

## Delete the phrase entirely

- `it is worth noting that`
- `it is important to note that`
- `keep in mind that`
- `that said`
- `at the end of the day`
- `needless to say`
- `as you can see`
- `I hope this helps`
- `Great question` / `You're absolutely right` / `Sure thing`

## Shorten

| Replace                 | With            |
| ----------------------- | --------------- |
| `in order to`           | `to`            |
| `prior to`              | `before`        |
| `subsequent to`         | `after`         |
| `due to the fact that`  | `because`       |
| `at this point in time` | `now`           |
| `has the ability to`    | `can`           |
| `is able to`            | `can`           |
| `make a decision`       | `decide`        |
| `perform compression`   | `compress`      |
| `provide support for`   | `support`       |
| `a number of`           | give the number |

## Collapse hedge stacks

A hedge stack is two or more qualifiers on one claim. Keep one hedge, or state the uncertainty as a fact.

| Replace                       | With                            |
| ----------------------------- | ------------------------------- |
| `might possibly be caused by` | `The cause is not confirmed.`   |
| `it appears that it may`      | `It can`                        |
| `could potentially`           | `can`                           |
| `seems to suggest that`       | `suggests` or state the finding |

## Collapse synonyms

One idea, one word. The word is fixed, never picked fresh each time. A rule that says "pick one by intent" produces rotation, because the model re-decides on every sentence.

| Concept                  | Write       | Never write                                   |
| ------------------------ | ----------- | --------------------------------------------- |
| Confirm a state or value | `check`     | verify, confirm, validate, ensure             |
| Something went wrong     | `error`     | failure, issue, problem, fault                |
| Program settings         | `config`    | configuration, settings, options, preferences |
| A path holding files     | `directory` | folder, dir                                   |
| A callable               | `function`  | method, routine, handler, procedure           |
| Make something happen    | `run`       | execute, invoke, trigger, kick off            |
| Get data over a network  | `fetch`     | retrieve, pull, grab, download                |
| Change existing content  | `modify`    | update, edit, alter, adjust, tweak            |
| Bring into existence     | `create`    | make, generate, build, add, produce           |
| Take out of existence    | `remove`    | delete, drop, purge, clear, strip             |

Two exemptions, and only two:

- **The code wins.** When the codebase names a symbol `validate_token` or a type `Settings`, write that identifier verbatim. It is a technical span, not prose.
- **The domain wins.** When a term carries a distinct technical meaning, keep it. `validate` against a schema is not `check`. `fetch` in a CPU pipeline is not a network call.

Outside those two cases, the canonical word applies with no judgment call.
