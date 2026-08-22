<!-- dts:no-lint -->

# Examples

Real unedited output from Claude Opus 5. Each standard is the entire system prompt: no agent harness, no memory file, nothing else loaded.

No route to a Claude model accepts a seed, so these are single samples and cannot be reproduced exactly.

Counts are words of visible reply. These runs went through OpenRouter, which bills reasoning tokens inside the output count, so a token figure here would measure thinking the reader never sees.

```sh
cd bench
./bench.py --model openrouter:anthropic/claude-opus-5 \
  --arms baseline eli5 ste100 caveman concise dts --ids ex02 --temp 0
```

## Explaining a concept

```
Explain the difference between a process and a thread.
```

<table>
<tr><th>Standard</th><th>Words</th><th>vs&nbsp;base</th><th>Facts</th><th align="left">Dropped</th></tr>
<tr><td>No standard</td><td align="right">573</td><td align="right">&mdash;</td><td align="center">5/5</td><td>nothing</td></tr>
<tr><td>ASD-STE100</td><td align="right">362</td><td align="right">-37%</td><td align="center">5/5</td><td>nothing</td></tr>
<tr><td>ELI5</td><td align="right">174</td><td align="right">-70%</td><td align="center">4/5</td><td>scheduling</td></tr>
<tr><td>Concise</td><td align="right">217</td><td align="right">-62%</td><td align="center">4/5</td><td>scheduling</td></tr>
<tr><td><b>DTS</b></td><td align="right">233</td><td align="right">-59%</td><td align="center"><b>5/5</b></td><td>nothing</td></tr>
<tr><td>Caveman</td><td align="right">171</td><td align="right">-70%</td><td align="center">4/5</td><td>scheduling</td></tr>
</table>
 
### Side by side
 
<table>
<tr><th width="50%">No standard — 573 words</th><th width="50%">DTS — 233 words</th></tr>
<tr>
<td valign="top">

## The short version

A **process** is an independent program in execution with its own private memory space. A **thread** is a unit of execution _inside_ a process; multiple threads in the same process share that process's memory.

Analogy: a process is a house, threads are the people living in it. Each house has its own plumbing, furniture, and locked front door. The people inside share all of it — which makes cooperation easy and stepping on each other's toes equally easy.

## What each one owns

**A process has:**

- Its own virtual address space (code, heap, globals, data segments)
- Open file descriptors, sockets, environment variables
- A process ID, security context, and permissions
- At least one thread (the "main" thread)

**A thread has its own:**

- Stack (local variables, call frames)
- Program counter and CPU registers
- Thread ID and scheduling priority
- Thread-local storage

**Threads share** everything else in the process: the heap, global variables, file descriptors, and loaded code.

## Comparison

|                | Process                                            | Thread                                    |
| -------------- | -------------------------------------------------- | ----------------------------------------- |
| Memory         | Private, isolated                                  | Shared within process                     |
| Creation cost  | High (new page tables, address space)              | Low                                       |
| Context switch | Expensive (TLB flush, page table swap)             | Cheaper (same address space)              |
| Communication  | IPC: pipes, sockets, shared memory, message queues | Direct — just read/write shared variables |
| Crash impact   | Isolated; other processes survive                  | Usually kills the whole process           |
| Debugging      | Easier to reason about                             | Race conditions, deadlocks, heisenbugs    |

## Why the isolation matters

Because processes don't share memory, a bug in one can't corrupt another's data — the MMU enforces this in hardware. That's why Chrome runs each tab as a separate process: a crashing tab shouldn't take down your browser.

Because threads _do_ share memory, they're fast to coordinate but require discipline. Two threads incrementing the same counter without a lock will produce wrong results, because `count++` isn't atomic — it's load, add, store, and the interleaving can lose updates. This is why you need mutexes, atomics, condition variables, and so on.

## Choosing between them

**Use threads when:** you need shared access to a large in-memory data structure, you're doing I/O-bound work (network servers, GUIs that must stay responsive), or coordination is frequent and fine-grained.

**Use processes when:** you want fault isolation, you're running untrusted or plugin code, you need to bypass a runtime limitation (Python's GIL prevents CPU-bound threads from scaling, so `multiprocessing` is the answer), or the work is embarrassingly parallel with little shared state.

## A few nuances worth knowing

- **Linux blurs the line.** The kernel schedules `task_struct`s; both processes and threads are tasks created via `clone()` with different sharing flags. A "thread" is just a task that shares the address space with its siblings.
- **Windows draws it sharply.** Process creation is genuinely expensive there, which historically pushed Windows software toward threads and Unix software toward `fork()`.
- **Not all threads are OS threads.** Goroutines, virtual threads (Java 21+), and async/await coroutines are _user-space_ concurrency multiplexed onto a smaller pool of OS threads. They're far cheaper — millions are feasible — but they can't be preempted by the kernel in the same way.
- **Modern practice often mixes both.** A typical web server runs N worker processes (one per core, for isolation and GIL avoidance), each with a thread pool or event loop inside.

</td>
<td valign="top">

A process owns its own memory space. A thread runs inside a process and shares that space with sibling threads.

| Aspect             | Process                                   | Thread                                   |
| ------------------ | ----------------------------------------- | ---------------------------------------- |
| Address space      | Private, isolated by the MMU              | Shared with all threads in the process   |
| Creation cost      | High — page tables, file descriptor table | Low — stack and register set only        |
| Crash blast radius | Contained to that process                 | Kills the whole process                  |
| Communication      | Pipes, sockets, shared memory segments    | Direct reads of shared variables         |
| Scheduling unit    | Kernel schedules it                       | Kernel schedules it (for native threads) |
| Private state      | Everything                                | Stack, registers, thread-local storage   |

Consequences that matter in practice:

- Data races exist only between threads. Shared memory needs locks, atomics, or message passing.
- Process isolation costs context-switch time. Switching threads in one process skips the page-table flush.
- A segfault in one thread takes down every thread. Use separate processes when fault isolation is required.
- Python threads are constrained by the GIL for CPU-bound work. Use `multiprocessing` there.

Edge cases:

- Linux implements both with `clone`. Threads are tasks sharing `CLONE_VM`, so the kernel distinction is thinner than the model.
- Green threads and coroutines are scheduled in userspace. The kernel sees one thread, so a blocking syscall stalls all of them.

</td>
</tr>
</table>

<details>
<summary>Every reply in full, raw</summary>

**No standard** — 573 words

```markdown
## The short version

A **process** is an independent program in execution with its own private memory space. A **thread** is a unit of execution _inside_ a process; multiple threads in the same process share that process's memory.

Analogy: a process is a house, threads are the people living in it. Each house has its own plumbing, furniture, and locked front door. The people inside share all of it — which makes cooperation easy and stepping on each other's toes equally easy.

## What each one owns

**A process has:**

- Its own virtual address space (code, heap, globals, data segments)
- Open file descriptors, sockets, environment variables
- A process ID, security context, and permissions
- At least one thread (the "main" thread)

**A thread has its own:**

- Stack (local variables, call frames)
- Program counter and CPU registers
- Thread ID and scheduling priority
- Thread-local storage

**Threads share** everything else in the process: the heap, global variables, file descriptors, and loaded code.

## Comparison

|                | Process                                            | Thread                                    |
| -------------- | -------------------------------------------------- | ----------------------------------------- |
| Memory         | Private, isolated                                  | Shared within process                     |
| Creation cost  | High (new page tables, address space)              | Low                                       |
| Context switch | Expensive (TLB flush, page table swap)             | Cheaper (same address space)              |
| Communication  | IPC: pipes, sockets, shared memory, message queues | Direct — just read/write shared variables |
| Crash impact   | Isolated; other processes survive                  | Usually kills the whole process           |
| Debugging      | Easier to reason about                             | Race conditions, deadlocks, heisenbugs    |

## Why the isolation matters

Because processes don't share memory, a bug in one can't corrupt another's data — the MMU enforces this in hardware. That's why Chrome runs each tab as a separate process: a crashing tab shouldn't take down your browser.

Because threads _do_ share memory, they're fast to coordinate but require discipline. Two threads incrementing the same counter without a lock will produce wrong results, because `count++` isn't atomic — it's load, add, store, and the interleaving can lose updates. This is why you need mutexes, atomics, condition variables, and so on.

## Choosing between them

**Use threads when:** you need shared access to a large in-memory data structure, you're doing I/O-bound work (network servers, GUIs that must stay responsive), or coordination is frequent and fine-grained.

**Use processes when:** you want fault isolation, you're running untrusted or plugin code, you need to bypass a runtime limitation (Python's GIL prevents CPU-bound threads from scaling, so `multiprocessing` is the answer), or the work is embarrassingly parallel with little shared state.

## A few nuances worth knowing

- **Linux blurs the line.** The kernel schedules `task_struct`s; both processes and threads are tasks created via `clone()` with different sharing flags. A "thread" is just a task that shares the address space with its siblings.
- **Windows draws it sharply.** Process creation is genuinely expensive there, which historically pushed Windows software toward threads and Unix software toward `fork()`.
- **Not all threads are OS threads.** Goroutines, virtual threads (Java 21+), and async/await coroutines are _user-space_ concurrency multiplexed onto a smaller pool of OS threads. They're far cheaper — millions are feasible — but they can't be preempted by the kernel in the same way.
- **Modern practice often mixes both.** A typical web server runs N worker processes (one per core, for isolation and GIL avoidance), each with a thread pool or event loop inside.
```

**ASD-STE100** — 362 words

```markdown
## Process

A process is one instance of a program that runs on a computer. The operating system gives each process its own memory space. Each process also has its own process ID, file handles, and environment variables. No other process can read this memory space directly.

## Thread

A thread is one path of execution inside a process. Every process has a minimum of one thread. A process can start more threads, and all of them run in the same memory space. Each thread has its own stack, its own registers, and its own program counter. All threads of one process share the heap and the open file handles.

## The main differences

| Item                    | Process                                      | Thread                                       |
| ----------------------- | -------------------------------------------- | -------------------------------------------- |
| Memory space            | Its own                                      | Shared with the other threads of the process |
| Cost to create          | High                                         | Low                                          |
| Communication           | Through pipes, sockets, or shared memory     | Through shared memory in the process         |
| Effect of a fatal error | The other processes continue                 | The whole process stops                      |
| Data protection         | The operating system separates the processes | The program must use locks                   |

## Effects on a program

The operating system needs more time and more memory to make a new process than to make a new thread. A switch between two processes also needs a switch of the memory space, and this switch costs more time. As a result, threads are faster for work that one program divides into parallel parts.

Processes give better isolation. An error in one process does not damage the memory of another process, but an error in one thread can stop every thread in the same process. Two threads that write to the same variable at the same time can also cause a data race. The program must use a lock, a mutex, or another mechanism to prevent this race.

## A note on Linux

On Linux, the kernel schedules processes and threads as tasks of the same kind. The difference is the set of resources that the tasks share. Two threads share one memory space, and two processes do not.
```

**ELI5** — 174 words

```markdown
**Process = a whole kitchen.**
It has its own space. Its own fridge, its own counters.
Two kitchens can't reach into each other's fridge.

**Thread = a cook in that kitchen.**
One kitchen can have many cooks. They all share the same fridge and counters.

That's the big difference: **threads share memory, processes don't.**

**Why it matters:**

- Threads are fast to start and talk to each other. Same fridge, just grab it.
- But cooks can bump into each other. Two cooks grabbing the same egg = bug. This is called a _race condition_ (two things touching the same data at once, and the order decides who wins).
- Processes are safer. Separate kitchens, no bumping. But slower to start, and passing food between kitchens takes work.

**Rule of thumb:**

- Need speed and shared data? Threads.
- Need safety, or one crash shouldn't kill everything? Processes.

One crash in a kitchen burns down that kitchen only. One bad cook can ruin the whole kitchen for everyone in it.

That's it. Go rest.
```

**Concise** — 217 words

```markdown
A **process** is an independent program in execution with its own private address space; a **thread** is a unit of execution _inside_ a process, sharing that address space with sibling threads.

|                | Process                                         | Thread                                           |
| -------------- | ----------------------------------------------- | ------------------------------------------------ |
| Memory         | Own virtual address space (heap, globals, code) | Shares process memory; own stack + registers     |
| Creation cost  | Expensive (page tables, PCB)                    | Cheap                                            |
| Communication  | IPC: pipes, sockets, shared memory, signals     | Direct — just read/write shared variables        |
| Isolation      | Crash kills only that process                   | Crash/corruption can take down whole process     |
| Context switch | Costly (TLB/page-table swap)                    | Cheaper (same address space)                     |
| Owns           | File descriptors, PID, signal handlers          | Thread ID, stack, thread-local storage, priority |

**Practical consequences**

- Threads need synchronization (mutexes, atomics) because shared mutable state causes data races. Processes mostly avoid this by construction.
- Use processes for fault isolation and security boundaries (browser tabs, worker pools in Python where the GIL limits threads).
- Use threads for tight cooperation on shared data with low overhead (server request handling, parallel compute on a shared buffer).

Linux blurs the line: both are `task_struct`s created by `clone()`; threads are just tasks that share memory, FDs, and signal handlers via flags like `CLONE_VM`.
```

**DTS** — 233 words

```markdown
A process owns its own memory space. A thread runs inside a process and shares that space with sibling threads.

| Aspect             | Process                                   | Thread                                   |
| ------------------ | ----------------------------------------- | ---------------------------------------- |
| Address space      | Private, isolated by the MMU              | Shared with all threads in the process   |
| Creation cost      | High — page tables, file descriptor table | Low — stack and register set only        |
| Crash blast radius | Contained to that process                 | Kills the whole process                  |
| Communication      | Pipes, sockets, shared memory segments    | Direct reads of shared variables         |
| Scheduling unit    | Kernel schedules it                       | Kernel schedules it (for native threads) |
| Private state      | Everything                                | Stack, registers, thread-local storage   |

Consequences that matter in practice:

- Data races exist only between threads. Shared memory needs locks, atomics, or message passing.
- Process isolation costs context-switch time. Switching threads in one process skips the page-table flush.
- A segfault in one thread takes down every thread. Use separate processes when fault isolation is required.
- Python threads are constrained by the GIL for CPU-bound work. Use `multiprocessing` there.

Edge cases:

- Linux implements both with `clone`. Threads are tasks sharing `CLONE_VM`, so the kernel distinction is thinner than the model.
- Green threads and coroutines are scheduled in userspace. The kernel sees one thread, so a blocking syscall stalls all of them.
```

**Caveman** — 171 words

```markdown
**Process** = own memory space. OS gives it virtual address space, file descriptors, PID.

**Thread** = execution unit inside process. Shares address space with sibling threads.

|                | Process                                     | Thread                                                  |
| -------------- | ------------------------------------------- | ------------------------------------------------------- |
| Memory         | private                                     | shared (heap, globals, code)                            |
| Own            | PID, page table, fd table                   | stack, registers, program counter, thread-local storage |
| Crash          | kills self only                             | can corrupt whole process                               |
| Create cost    | high (page tables, copy/COW)                | low                                                     |
| Communicate    | IPC: pipes, sockets, shared memory, signals | direct memory read/write                                |
| Context switch | expensive (TLB flush, page table swap)      | cheap (same address space)                              |

Key consequence: threads share memory, so need locks/atomics — race conditions, deadlocks possible. Processes isolated, so no data races but pay IPC cost + serialization.

Linux detail: both are `task_struct`. `clone()` flags decide sharing. `CLONE_VM|CLONE_FILES|CLONE_SIGHAND` = thread. No flags = process (`fork()`).

Pick processes for fault isolation + security (browser tabs). Pick threads for shared-state work + fast communication.
```

</details>

## Writing an error message

```
Write the error message a user sees when their config file has an invalid port number.
```

<table>
<tr><th>Standard</th><th>Words</th><th>vs&nbsp;base</th><th>Facts</th><th align="left">Dropped</th></tr>
<tr><td>No standard</td><td align="right">254</td><td align="right">&mdash;</td><td align="center">4/4</td><td>nothing</td></tr>
<tr><td>ASD-STE100</td><td align="right">287</td><td align="right">+13%</td><td align="center">4/4</td><td>nothing</td></tr>
<tr><td>ELI5</td><td align="right">108</td><td align="right">-57%</td><td align="center">4/4</td><td>nothing</td></tr>
<tr><td>Concise</td><td align="right">122</td><td align="right">-52%</td><td align="center">4/4</td><td>nothing</td></tr>
<tr><td><b>DTS</b></td><td align="right">153</td><td align="right">-40%</td><td align="center"><b>4/4</b></td><td>nothing</td></tr>
<tr><td>Caveman</td><td align="right">108</td><td align="right">-57%</td><td align="center">4/4</td><td>nothing</td></tr>
</table>

### Side by side

<table>
<tr><th width="50%">No standard — 254 words</th><th width="50%">DTS — 153 words</th></tr>
<tr>
<td valign="top">

**Primary error message**

```
Error: invalid value for 'port' in config.yaml (line 14)

    14 |   port: 99999
                ^^^^^

  Port must be an integer between 1 and 65535.

  Hint: did you mean 9999?

  For more details, see: https://docs.example.com/config#port
```

**Variants for related failure cases**

Non-numeric value:

```
Error: invalid value for 'port' in config.yaml (line 14)

    14 |   port: "eighty"
                ^^^^^^^^^

  Port must be an integer between 1 and 65535, but got a string: "eighty".
```

Privileged port without permission:

```
Error: cannot bind to 'port' 80 from config.yaml (line 14)

  Ports below 1024 require elevated privileges.

  Hint: use a port above 1023 (e.g. 8080), or run with sudo.
```

Empty or missing value:

```
Error: missing value for 'port' in config.yaml (line 14)

  Port is required. Set it to an integer between 1 and 65535,
  or remove the key to use the default (8080).
```

**Why this shape works**

- **Names the file and line**, so the user doesn't have to hunt for it.
- **Echoes the offending value** with a caret pointer, confirming what the parser actually read (catches quoting and YAML-coercion surprises).
- **States the valid range**, not just "invalid" — the constraint is the actionable part.
- **Suggests a fix** when one is inferable (typo, common default), but never guesses silently.
- **Exits non-zero and fails fast** at startup rather than at first request.

If you tell me the language/framework, I can match your existing error conventions (e.g. Go's `fmt.Errorf` wrapping, Rust's `thiserror` + `miette` diagnostics, or Python's `pydantic` ValidationError formatting).

</td>
<td valign="top">

```
Error: invalid port in /etc/myapp/config.yaml line 12
  server.port: "8O80"
Port must be an integer from 1 to 65535.
Modify server.port, then rerun `myapp start`.
```

Parts and why each stays:

| Part        | Content                                                                 |
| ----------- | ----------------------------------------------------------------------- |
| What failed | `invalid port` plus the config key `server.port`                        |
| Where       | Absolute path and line number                                           |
| Exact input | `"8O80"` quoted verbatim, so the letter `O` versus digit `0` is visible |
| Rule        | Accepted range 1 to 65535                                               |
| Next action | Modify the key, then the exact rerun command                            |

Two variants if your port rule is stricter:

- Privileged ports rejected — replace the rule line with `Port must be an integer from 1024 to 65535 unless the process runs as root.`
- Port already bound — this is a different error, not an invalid port. Report it at bind time with the owning PID.

</td>
</tr>
</table>

<details>
<summary>Every reply in full, raw</summary>

**No standard** — 254 words

````markdown
**Primary error message**

```
Error: invalid value for 'port' in config.yaml (line 14)

    14 |   port: 99999
                ^^^^^

  Port must be an integer between 1 and 65535.

  Hint: did you mean 9999?

  For more details, see: https://docs.example.com/config#port
```

**Variants for related failure cases**

Non-numeric value:

```
Error: invalid value for 'port' in config.yaml (line 14)

    14 |   port: "eighty"
                ^^^^^^^^^

  Port must be an integer between 1 and 65535, but got a string: "eighty".
```

Privileged port without permission:

```
Error: cannot bind to 'port' 80 from config.yaml (line 14)

  Ports below 1024 require elevated privileges.

  Hint: use a port above 1023 (e.g. 8080), or run with sudo.
```

Empty or missing value:

```
Error: missing value for 'port' in config.yaml (line 14)

  Port is required. Set it to an integer between 1 and 65535,
  or remove the key to use the default (8080).
```

**Why this shape works**

- **Names the file and line**, so the user doesn't have to hunt for it.
- **Echoes the offending value** with a caret pointer, confirming what the parser actually read (catches quoting and YAML-coercion surprises).
- **States the valid range**, not just "invalid" — the constraint is the actionable part.
- **Suggests a fix** when one is inferable (typo, common default), but never guesses silently.
- **Exits non-zero and fails fast** at startup rather than at first request.

If you tell me the language/framework, I can match your existing error conventions (e.g. Go's `fmt.Errorf` wrapping, Rust's `thiserror` + `miette` diagnostics, or Python's `pydantic` ValidationError formatting).
````

**ASD-STE100** — 287 words

````markdown
**Primary message (value is not in the permitted range):**

```
Error: invalid port number in ./config.yaml, line 12.

"port" is set to 70000. A port number must be from 1 to 65535.
Set "port" to a number from 1 to 65535. Then start sqlpipe again.
```

**Variant — the value is not a number:**

```
Error: invalid port number in ./config.yaml, line 12.

"port" is set to "8O80". This value is not a number.
Set "port" to a number from 1 to 65535. Then start sqlpipe again.
```

**Variant — the port is reserved and the process has no privilege:**

```
Error: cannot use port 80 from ./config.yaml, line 12.

Ports from 1 to 1023 need root privilege. This process does not have root privilege.
Set "port" to a number from 1024 to 65535, or start the process as root.
```

---

**Notes on the choices**

The message follows the three-part pattern for error text: what happened, the cause, then the fix as an imperative. Each sentence gives one new fact.

Removed items and the reason for each:

- "Oops", "Sorry", "Please" — filler, no fact.
- "invalid or malformed" — one word does the job.
- "should be between 1 and 65535" — "should" reads as optional. The requirement is "must", and the fix is an imperative.
- "Please ensure your config is valid" — "ensure" is not an approved verb, and the sentence gives no action. The imperative names the key and the range.
- "For more information, see the documentation." — no target, no fact. Name the section or delete it.

The file path, the line number, and the key name `"port"` are technical names. They stay exact, and each counts as one word.
````

**ELI5** — 108 words

````markdown
Here's the message:

```
Error: invalid port in config.

  File:  /etc/myapp/config.yaml
  Line:  12
  Found: port: 70000

Ports must be a whole number from 1 to 65535.
Fix line 12, then run: myapp --check-config
```

**Why this shape:** it says what broke, where it broke, what's allowed, and the exact next command. No guessing.

**One choice for you:**

1. **Keep the file + line number** (above). Needs your parser to track line numbers. Best if it already does.
2. **Drop the line number**, just say `File: /etc/myapp/config.yaml` and `Found: port: 70000`. Easier to build.

I'd go with **1** if line numbers are free, else **2**. Not worth extra work.
````

**Concise** — 122 words

````markdown
```
Error: invalid port number in config file

  /etc/myapp/config.toml:12
   12 | port = 70000
          ^^^^^ must be an integer between 1 and 65535

Ports above 65535 are not valid TCP/UDP ports. Use 8080 for local
development, or 0 to let the OS assign a free port.
```

Variants for other bad inputs on the same line:

| Input                              | Message under the caret                   |
| ---------------------------------- | ----------------------------------------- |
| `port = "abc"`                     | `expected an integer, found string "abc"` |
| `port = -1`                        | `must be an integer between 1 and 65535`  |
| `port = 80` (unprivileged process) | `ports below 1024 require root; try 8080` |

Keep the exit code non-zero (`1`) and write to stderr so scripts can detect the failure.
````

**DTS** — 153 words

````markdown
```
Error: invalid port in /etc/myapp/config.yaml line 12
  server.port: "8O80"
Port must be an integer from 1 to 65535.
Modify server.port, then rerun `myapp start`.
```

Parts and why each stays:

| Part        | Content                                                                 |
| ----------- | ----------------------------------------------------------------------- |
| What failed | `invalid port` plus the config key `server.port`                        |
| Where       | Absolute path and line number                                           |
| Exact input | `"8O80"` quoted verbatim, so the letter `O` versus digit `0` is visible |
| Rule        | Accepted range 1 to 65535                                               |
| Next action | Modify the key, then the exact rerun command                            |

Two variants if your port rule is stricter:

- Privileged ports rejected — replace the rule line with `Port must be an integer from 1024 to 65535 unless the process runs as root.`
- Port already bound — this is a different error, not an invalid port. Report it at bind time with the owning PID.
````

**Caveman** — 108 words

````markdown
```
Error: invalid port number in config file.

  config.toml:12
    port = 70000

Port must be an integer between 1 and 65535.
```

Notes on fields worth including:

- file path + line number, so user can jump straight there
- the offending value echoed back verbatim
- the valid range, so no second guess
- if port < 1024 on Unix and process unprivileged, separate message: `Port 80 requires root privileges. Use a port above 1023 or run with elevated permissions.`

Distinguish causes — non-numeric vs out-of-range vs reserved:

```
Error: invalid port number in config file.

  config.toml:12
    port = "eighty"

Expected an integer, got a string.
```
````

</details>

## Reviewing code

```
Review this: `def second(s): return s.split(',')[1]`
```

<table>
<tr><th>Standard</th><th>Words</th><th>vs&nbsp;base</th><th>Facts</th><th align="left">Dropped</th></tr>
<tr><td>No standard</td><td align="right">409</td><td align="right">&mdash;</td><td align="center">2/2</td><td>nothing</td></tr>
<tr><td>ASD-STE100</td><td align="right">325</td><td align="right">-21%</td><td align="center">2/2</td><td>nothing</td></tr>
<tr><td>ELI5</td><td align="right">187</td><td align="right">-54%</td><td align="center">2/2</td><td>nothing</td></tr>
<tr><td>Concise</td><td align="right">142</td><td align="right">-65%</td><td align="center">2/2</td><td>nothing</td></tr>
<tr><td><b>DTS</b></td><td align="right">298</td><td align="right">-27%</td><td align="center"><b>2/2</b></td><td>nothing</td></tr>
<tr><td>Caveman</td><td align="right">148</td><td align="right">-64%</td><td align="center">2/2</td><td>nothing</td></tr>
</table>

### Side by side

<table>
<tr><th width="50%">No standard — 409 words</th><th width="50%">DTS — 298 words</th></tr>
<tr>
<td valign="top">

## Review

The function works for the happy path, but it's fragile and under-specified. Notes in rough priority order:

### 1. Unhandled `IndexError`

Any input with fewer than two fields blows up:

```python
second("a")   # IndexError: list index out of range
second("")    # IndexError
second(",")   # '' — fine, but probably not what you want either
```

Decide on a contract and enforce it: raise a meaningful error (`ValueError("expected at least 2 comma-separated fields")`) or return a default (`None` / `""`). Silently propagating `IndexError` from a helper makes callers debug your internals.

### 2. This is not a CSV parser

If the input is real CSV, quoting and escapes will break it:

```python
second('a,"b,c",d')   # '"b'  ← wrong
```

If you control the format and it's guaranteed comma-free-and-unquoted, fine — say so in a docstring. Otherwise use `csv.reader` or `str.split` on a delimiter that can't appear in the data.

### 3. No whitespace handling

`second("a, b")` → `" b"`. If callers always `.strip()` the result, do it here instead. Either way, document the choice.

### 4. Unbounded split

`split(',')` builds a list of _every_ field just to discard all but one. On long lines that's wasted allocation. Use `maxsplit`:

```python
s.split(',', 2)[1]
```

Or avoid the list entirely with `partition`, which is also naturally safe:

```python
s.partition(',')[2].partition(',')[0]
```

(Though that quietly returns `""` for malformed input — the readability/explicitness tradeoff is yours.)

### 5. Naming

`second` and `s` say nothing. `second` _what_, of _what_? `second_field(line)` or `second_csv_column(row)` tells a reader what to expect without opening the definition.

### 6. Style / discoverability

PEP 8 discourages the body on the same line as `def`. There's no type hint and no docstring, so the input format — the single most important thing about this function — is undocumented.

### Suggested version

```python
def second_field(line: str, *, strip: bool = True) -> str:
    """Return the second comma-separated field of `line`.

    Assumes a simple unquoted format; not a general CSV parser.

    Raises:
        ValueError: if `line` has fewer than two fields.
    """
    parts = line.split(',', 2)
    if len(parts) < 2:
        raise ValueError(f"expected at least 2 comma-separated fields, got {line!r}")
    field = parts[1]
    return field.strip() if strip else field
```

### Bigger question

If this is used in one place, inline it — a one-line wrapper around `split` earns its keep only if it adds validation, documentation, or a name that clarifies intent. The version above does; the original mostly just hides a `split` call.

</td>
<td valign="top">

**Main error: `IndexError` on any input without a comma.** `second("abc")` raises `IndexError: list index out of range`. Same for `""`.

Other findings:

| Issue                           | Example             | Result                                 |
| ------------------------------- | ------------------- | -------------------------------------- |
| No whitespace strip             | `second("a, b")`    | `" b"`                                 |
| Naive split ignores CSV quoting | `second('a,"b,c"')` | `'"b'`                                 |
| Splits entire string            | 10 MB line          | scans all fields, needs only 2         |
| Names carry no meaning          | `second`, `s`       | reader cannot tell field vs. character |
| No type hints, no docstring     | —                   | —                                      |

Use `s.split(',', 2)[1]` to cap the work at three parts. `maxsplit=1` is wrong here — it returns the whole tail, not the second field.

Decision, two shapes:

- **Strict** — raise a named error. Pick this when a missing field is a bug upstream.
- **Lenient** — return a default. Pick this for tolerant log parsing.

Strict is my pick, because the current silent `IndexError` already hides the cause.

```python
def second_field(line: str, *, strip: bool = True) -> str:
    """Return the second comma-separated field of `line`.

    Raises ValueError if `line` has fewer than two fields.
    Does not handle quoted CSV fields — use the `csv` module for that.
    """
    parts = line.split(',', 2)
    if len(parts) < 2:
        raise ValueError(f"expected at least 2 comma-separated fields, got {len(parts)}: {line!r}")
    field = parts[1]
    return field.strip() if strip else field
```

For quoted or escaped input, drop the hand-rolled split:

```python
import csv
import io

def second_field_csv(line: str) -> str:
    """Return the second CSV field of `line`, honoring quoting."""
    row = next(csv.reader(io.StringIO(line)))
    if len(row) < 2:
        raise ValueError(f"expected at least 2 CSV fields, got {len(row)}: {line!r}")
    return row[1]
```

Run next:

```python
assert second_field("a,b,c") == "b"
assert second_field("a, b") == "b"
assert second_field_csv('a,"b,c",d') == "b,c"
```

</td>
</tr>
</table>

<details>
<summary>Every reply in full, raw</summary>

**No standard** — 409 words

````markdown
## Review

The function works for the happy path, but it's fragile and under-specified. Notes in rough priority order:

### 1. Unhandled `IndexError`

Any input with fewer than two fields blows up:

```python
second("a")   # IndexError: list index out of range
second("")    # IndexError
second(",")   # '' — fine, but probably not what you want either
```

Decide on a contract and enforce it: raise a meaningful error (`ValueError("expected at least 2 comma-separated fields")`) or return a default (`None` / `""`). Silently propagating `IndexError` from a helper makes callers debug your internals.

### 2. This is not a CSV parser

If the input is real CSV, quoting and escapes will break it:

```python
second('a,"b,c",d')   # '"b'  ← wrong
```

If you control the format and it's guaranteed comma-free-and-unquoted, fine — say so in a docstring. Otherwise use `csv.reader` or `str.split` on a delimiter that can't appear in the data.

### 3. No whitespace handling

`second("a, b")` → `" b"`. If callers always `.strip()` the result, do it here instead. Either way, document the choice.

### 4. Unbounded split

`split(',')` builds a list of _every_ field just to discard all but one. On long lines that's wasted allocation. Use `maxsplit`:

```python
s.split(',', 2)[1]
```

Or avoid the list entirely with `partition`, which is also naturally safe:

```python
s.partition(',')[2].partition(',')[0]
```

(Though that quietly returns `""` for malformed input — the readability/explicitness tradeoff is yours.)

### 5. Naming

`second` and `s` say nothing. `second` _what_, of _what_? `second_field(line)` or `second_csv_column(row)` tells a reader what to expect without opening the definition.

### 6. Style / discoverability

PEP 8 discourages the body on the same line as `def`. There's no type hint and no docstring, so the input format — the single most important thing about this function — is undocumented.

### Suggested version

```python
def second_field(line: str, *, strip: bool = True) -> str:
    """Return the second comma-separated field of `line`.

    Assumes a simple unquoted format; not a general CSV parser.

    Raises:
        ValueError: if `line` has fewer than two fields.
    """
    parts = line.split(',', 2)
    if len(parts) < 2:
        raise ValueError(f"expected at least 2 comma-separated fields, got {line!r}")
    field = parts[1]
    return field.strip() if strip else field
```

### Bigger question

If this is used in one place, inline it — a one-line wrapper around `split` earns its keep only if it adds validation, documentation, or a name that clarifies intent. The version above does; the original mostly just hides a `split` call.
````

**ASD-STE100** — 325 words

````markdown
## Summary

The function returns the second comma-delimited field of a string. It is correct for well-formed input. It fails with an unclear error for three common inputs, and it gives the wrong result for quoted CSV data.

## Faults

1. **No comma in the input.** `"abc".split(",")` returns a list of one item. The index `[1]` then raises `IndexError`. The message does not name the input or the cause.
2. **Empty input.** `"".split(",")` returns `[""]`. This also raises `IndexError`.
3. **Quoted commas.** For the input `'a,"b,c",d'` the function returns `'"b'`. The `csv` module reads quoted fields. `str.split` does not.
4. **Leading whitespace stays.** For the input `"a, b"` the function returns `" b"`.
5. **The body is on the signature line.** PEP 8 puts the body on the next line.
6. **No type hints and no docstring.** The caller cannot see the return type or the exceptions.
7. **The names give no information.** `second` and `s` do not say what the function reads.
8. **`split` has no maxsplit argument.** The call splits the whole string, and the function discards all fields after the second one.

## Suggested rewrite

```python
def second_field(line: str, separator: str = ",") -> str:
    """Return the second separator-delimited field of line.

    Raises ValueError if line has fewer than two fields.
    """
    fields = line.split(separator, 2)
    if len(fields) < 2:
        raise ValueError(f"no {separator!r} in input: {line!r}")
    return fields[1]
```

This version keeps the return value of the original for all valid input. It replaces `IndexError` with a `ValueError` that names the separator and the input.

## Notes

The `maxsplit` value of 2 stops the split after the second separator.

If the input is CSV data with quoted fields, use `csv.reader` instead of this function. The `csv` module handles quotes, escaped quotes, and embedded newlines.

If the fields can have leading spaces, add `.strip()` to the return value. This is a change in behavior, so make it only when the callers expect it.
````

**ELI5** — 187 words

````markdown
**What I did:** Read your function and walked through it by hand. Didn't run it.

**Does it work?** Yes — if the string always has a comma. Otherwise it blows up.

**The bugs**

1. No comma = crash.
   `second("hello")` → IndexError (means "there's no item #2").
2. Spaces stick around.
   `second("a, b")` gives `" b"`, not `"b"`.
3. Real CSV breaks it.
   `second('a,"b,c",d')` gives `'"b'`. Wrong. The quotes were supposed to keep `b,c` together.

**Your call — 2 options**

**Option A — quick and safe.** Use this if your strings are simple (no quotes inside).

```python
def second(s, default=None):
    parts = s.split(',')
    return parts[1].strip() if len(parts) > 1 else default
```

**Option B — real CSV.** Use this if the data comes from a spreadsheet or `.csv` file.

```python
import csv

def second(s, default=None):
    parts = next(csv.reader([s]))
    return parts[1].strip() if len(parts) > 1 else default
```

**I'd go with A** unless you know the data is CSV from a file. It's smaller and does the job.

**Do this now:** pick A or B, paste it in, then test with `second("hello")`. You should get `None`, not a crash.
````

**Concise** — 142 words

````markdown
Works, but it's fragile in three ways:

**Crashes on short input.** `second("abc")` raises `IndexError`. Any caller feeding user data needs a try/except or you need a default.

**No whitespace handling.** `second("a, b")` returns `" b"` with the leading space. Almost always a bug when the result is compared or used as a key.

**Not CSV-safe.** `second('"Smith, John",42')` returns `' John"'`. If the input is real CSV, use the `csv` module; if it's a simple delimited string, fine.

Also `split(',')` splits the whole string when you only need the first two fields — `split(',', 2)` is cheaper on long input, though it rarely matters.

Suggested:

```python
def second(s, default=None):
    """Return the second comma-separated field of s, stripped."""
    parts = s.split(',', 2)
    if len(parts) < 2:
        return default
    return parts[1].strip()
```

Consider a more descriptive name (`second_field`?) since `second` reads like a time unit.
````

**DTS** — 298 words

````markdown
**Main error: `IndexError` on any input without a comma.** `second("abc")` raises `IndexError: list index out of range`. Same for `""`.

Other findings:

| Issue                           | Example             | Result                                 |
| ------------------------------- | ------------------- | -------------------------------------- |
| No whitespace strip             | `second("a, b")`    | `" b"`                                 |
| Naive split ignores CSV quoting | `second('a,"b,c"')` | `'"b'`                                 |
| Splits entire string            | 10 MB line          | scans all fields, needs only 2         |
| Names carry no meaning          | `second`, `s`       | reader cannot tell field vs. character |
| No type hints, no docstring     | —                   | —                                      |

Use `s.split(',', 2)[1]` to cap the work at three parts. `maxsplit=1` is wrong here — it returns the whole tail, not the second field.

Decision, two shapes:

- **Strict** — raise a named error. Pick this when a missing field is a bug upstream.
- **Lenient** — return a default. Pick this for tolerant log parsing.

Strict is my pick, because the current silent `IndexError` already hides the cause.

```python
def second_field(line: str, *, strip: bool = True) -> str:
    """Return the second comma-separated field of `line`.

    Raises ValueError if `line` has fewer than two fields.
    Does not handle quoted CSV fields — use the `csv` module for that.
    """
    parts = line.split(',', 2)
    if len(parts) < 2:
        raise ValueError(f"expected at least 2 comma-separated fields, got {len(parts)}: {line!r}")
    field = parts[1]
    return field.strip() if strip else field
```

For quoted or escaped input, drop the hand-rolled split:

```python
import csv
import io

def second_field_csv(line: str) -> str:
    """Return the second CSV field of `line`, honoring quoting."""
    row = next(csv.reader(io.StringIO(line)))
    if len(row) < 2:
        raise ValueError(f"expected at least 2 CSV fields, got {len(row)}: {line!r}")
    return row[1]
```

Run next:

```python
assert second_field("a,b,c") == "b"
assert second_field("a, b") == "b"
assert second_field_csv('a,"b,c",d') == "b,c"
```
````

**Caveman** — 148 words

````markdown
`def second(s): return s.split(',')[1]`

Problems:

1. **IndexError** — no comma, or empty string. `second("abc")` crash. `second("")` crash.
2. **No strip** — `"a, b"` returns `" b"` with leading space.
3. **Not real CSV** — quoted fields with commas break it: `'a,"b,c"'` returns `'"b'`.
4. **Splits whole string** — use `maxsplit=1`, stop after first comma.
5. **Name** — `second` says nothing. `second_field` or `second_csv_field`.
6. No type hints, no docstring.

Fix (simple case, no quoting):

```python
def second_field(s: str, default: str | None = None) -> str | None:
    """Return second comma-separated field, stripped. default if absent."""
    parts = s.split(",", 1)
    return parts[1].strip() if len(parts) > 1 else default
```

Real CSV, use stdlib:

```python
import csv, io

def second_field(line: str) -> str | None:
    row = next(csv.reader(io.StringIO(line)), [])
    return row[1] if len(row) > 1 else None
```

Pick which depend on data. Quoted fields ever appear, take `csv`.
````

</details>

## Writing a README intro

```
Write the README intro paragraph for a Rust CLI that converts CSV to Parquet.
```

<table>
<tr><th>Standard</th><th>Words</th><th>vs&nbsp;base</th><th>Facts</th><th align="left">Dropped</th></tr>
<tr><td>No standard</td><td align="right">215</td><td align="right">&mdash;</td><td align="center">5/5</td><td>nothing</td></tr>
<tr><td>ASD-STE100</td><td align="right">237</td><td align="right">+10%</td><td align="center">5/5</td><td>nothing</td></tr>
<tr><td>ELI5</td><td align="right">163</td><td align="right">-24%</td><td align="center">4/5</td><td>convert|transform</td></tr>
<tr><td>Concise</td><td align="right">72</td><td align="right">-67%</td><td align="center">4/5</td><td>install|cargo|usage</td></tr>
<tr><td><b>DTS</b></td><td align="right">80</td><td align="right">-63%</td><td align="center"><b>4/5</b></td><td>install|cargo|usage</td></tr>
<tr><td>Caveman</td><td align="right">99</td><td align="right">-54%</td><td align="center">4/5</td><td>install|cargo|usage</td></tr>
</table>

### Side by side

<table>
<tr><th width="50%">No standard — 215 words</th><th width="50%">DTS — 80 words</th></tr>
<tr>
<td valign="top">

# csv2parquet

`csv2parquet` is a fast, single-binary command-line tool for converting CSV files into Apache Parquet. Built in Rust on top of Arrow, it streams data in batches so you can convert files much larger than memory, infers schemas automatically (or accepts one you define), and exposes the knobs that matter — compression codec, row group size, delimiter, and null handling. Whether you're prepping data for DuckDB, Spark, or pandas, there's no JVM to install and no Python environment to manage: just drop in the binary and go.

---

If you'd like a different flavor, here are two alternates:

**Shorter / punchier**

> `csv2parquet` turns CSV files into Apache Parquet, fast. It's a single Rust binary with no runtime dependencies — point it at a file, get columnar output with sensible defaults and full control over compression and schema when you need it.

**More technical / benchmark-forward**

> `csv2parquet` is a streaming CSV-to-Parquet converter written in Rust. It uses `arrow-rs` for zero-copy columnar buffers and `parquet-rs` for encoding, processing input in configurable record batches to keep memory flat regardless of input size. Typical throughput is _X_ GB/s on a single core, with optional multi-threaded conversion for directories of files.

Swap in your actual crate name and drop the placeholder benchmark once you have real numbers.

</td>
<td valign="top">

# csv2parquet

Converts CSV files to Apache Parquet. Reads from a path or stdin, writes columnar output with inferred or explicit schemas. Built on Arrow and the Rust Parquet writer.

```
csv2parquet data.csv -o data.parquet
```

**Features**

- Schema inference from a configurable row sample
- Explicit schema via JSON, overriding inference
- Compression: `snappy`, `gzip`, `zstd`, `lz4`, `brotli`, `none`
- Streaming writes, so file size is not bound by RAM
- Delimiter, quote, and header control for non-standard CSV

</td>
</tr>
</table>

<details>
<summary>Every reply in full, raw</summary>

**No standard** — 215 words

```markdown
# csv2parquet

`csv2parquet` is a fast, single-binary command-line tool for converting CSV files into Apache Parquet. Built in Rust on top of Arrow, it streams data in batches so you can convert files much larger than memory, infers schemas automatically (or accepts one you define), and exposes the knobs that matter — compression codec, row group size, delimiter, and null handling. Whether you're prepping data for DuckDB, Spark, or pandas, there's no JVM to install and no Python environment to manage: just drop in the binary and go.

---

If you'd like a different flavor, here are two alternates:

**Shorter / punchier**

> `csv2parquet` turns CSV files into Apache Parquet, fast. It's a single Rust binary with no runtime dependencies — point it at a file, get columnar output with sensible defaults and full control over compression and schema when you need it.

**More technical / benchmark-forward**

> `csv2parquet` is a streaming CSV-to-Parquet converter written in Rust. It uses `arrow-rs` for zero-copy columnar buffers and `parquet-rs` for encoding, processing input in configurable record batches to keep memory flat regardless of input size. Typical throughput is _X_ GB/s on a single core, with optional multi-threaded conversion for directories of files.

Swap in your actual crate name and drop the placeholder benchmark once you have real numbers.
```

**ASD-STE100** — 237 words

```markdown
## README intro (descriptive, pragmatic mode)

> # csv2parquet
>
> csv2parquet is a command-line tool that converts CSV files to Parquet files. The tool is written in Rust and runs as one binary. It reads a CSV file, finds the data type of each column, and writes a Parquet file. Command-line flags control the schema, the compression codec, and the size of each row group.

Word counts: 12, 11, 17, 14. All are less than the 25-word limit for descriptive text. Four sentences, one topic, active voice.

## Placeholders to correct

I do not have these facts, so confirm or change them:

1. The name `csv2parquet`. Replace it with the real name of your tool.
2. "runs as one binary". Remove this sentence if you ship the tool in another form.
3. Type inference. Remove the words "finds the data type of each column" if the tool needs a schema.
4. The three flags. Name only the flags that exist.

## Notes on the style

The intro is descriptive, so it has no imperative and no "you must" text. Put the install and usage commands in a separate procedural section, with a 20-word limit per sentence and one instruction per sentence.

The paragraph also has no "blazingly fast", "seamlessly", or "powerful". If you want a speed claim, give a number and the test conditions: "converts a 1 GB CSV file in 4 seconds on 8 cores."
```

**ELI5** — 163 words

```markdown
**Here's the paragraph.** I used `csv2parquet` as the name — swap it if yours is different.

---

`csv2parquet` is a small command-line tool that turns CSV files into Parquet. Parquet is a _columnar_ format — it stores data column by column instead of row by row, so files get much smaller and queries run much faster. Point it at a CSV, get a Parquet file back. It figures out your column types for you, streams large files instead of loading them into memory, and ships as a single Rust binary with no runtime to install.

---

**Your call — tone:**

1. **Keep it as-is.** Explains Parquet for people who don't know it. Good if your README is the first thing a stranger sees.
2. **Cut the Parquet explanation.** Shorter, assumes the reader knows data tooling.

I'd go with **1**. The extra sentence costs nothing and helps newcomers.

**Next:** paste it in, then tell me the real tool name and I'll fix the wording.
```

**Concise** — 72 words

```markdown
# csv2parquet

A fast, single-binary CLI for converting CSV files to Apache Parquet. It infers column types by sampling your data, streams records in batches so memory stays flat regardless of file size, and lets you pick the compression codec, row group size, and schema overrides when inference isn't enough. Point it at a file or pipe from stdin, and get a compressed, columnar Parquet file ready for DuckDB, Spark, or Pandas.
```

**DTS** — 80 words

````markdown
# csv2parquet

Converts CSV files to Apache Parquet. Reads from a path or stdin, writes columnar output with inferred or explicit schemas. Built on Arrow and the Rust Parquet writer.

```
csv2parquet data.csv -o data.parquet
```

**Features**

- Schema inference from a configurable row sample
- Explicit schema via JSON, overriding inference
- Compression: `snappy`, `gzip`, `zstd`, `lz4`, `brotli`, `none`
- Streaming writes, so file size is not bound by RAM
- Delimiter, quote, and header control for non-standard CSV
````

**Caveman** — 99 words

````markdown
```markdown
# csv2parquet

`csv2parquet` is a fast, dependency-free command-line tool for converting CSV files
into Apache Parquet. Written in Rust and built on Arrow, it streams input in
batches so files far larger than available memory can be converted without
issue. Schemas are inferred automatically from a configurable sample of rows, or
supplied explicitly when you need exact control over column types. Compression,
row-group size, and null handling are all tunable through flags, making it
suitable both for quick one-off conversions and for scripted use in data
pipelines.
```

Adjust: crate name, Arrow mention if not used, added flags.
````

</details>
