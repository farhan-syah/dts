#!/usr/bin/env python3
"""Uniform completion interface across model providers.

Every caller passes a spec of the form `provider:model` and receives the same
Result shape, so bench.py and judge.py never contain provider-specific code.
Providers are declared in config.toml, which the user edits. Adding a provider
is a config entry, not a code change, whenever it speaks an existing wire
protocol.

Three wire protocols cover the field:
  ollama     native /api/chat
  openai     /v1/chat/completions — also DeepSeek, Groq, Together, OpenRouter,
             vLLM, LM Studio, and any other OpenAI-compatible endpoint
  anthropic  /v1/messages

Run this file directly to check which providers are reachable:
  ./providers.py
  ./providers.py --probe claude:opus ollama:deepseek-v4-pro:cloud
"""
import json, os, shutil, subprocess, sys, time, tomllib, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(ROOT, "config.toml")
# 429 is deliberately absent. A provider quota does not refill during a run, so
# retrying spends more of an exhausted budget and delays a clear message.
RETRY_STATUS = {408, 409, 425, 500, 502, 503, 504}


class ProviderError(RuntimeError):
    pass


class QuotaError(ProviderError):
    """Provider refused for quota or rate reasons. Retrying cannot help."""


class Result:
    # `deterministic` is False when the provider ignored the seed. The bench
    # pairs arms by seed, so a result without one cannot be compared cell by
    # cell, only in aggregate over reps.
    __slots__ = ("text", "in_tok", "out_tok", "spec", "raw", "deterministic")

    def __init__(self, text, in_tok, out_tok, spec, raw, deterministic=True):
        self.text = text
        self.in_tok = in_tok
        self.out_tok = out_tok
        self.spec = spec
        self.raw = raw
        self.deterministic = deterministic

    def usage(self):
        """Small dict worth persisting. The full raw reply is too large to store.

        `cost_usd` is what a provider reports, which for a subscription CLI is a
        notional meter rather than a charge. Absent providers report nothing.
        """
        d = self.raw if isinstance(self.raw, dict) else {}
        u = d.get("usage") or {}
        out = {k: u[k] for k in
               ("cache_creation_input_tokens", "cache_read_input_tokens")
               if k in u}
        mu = d.get("modelUsage") or {}
        cost = sum(v.get("costUSD", 0) for v in mu.values() if isinstance(v, dict))
        if cost:
            out["cost_usd"] = round(cost, 6)
        return out

    def __repr__(self):
        return (f"Result({self.spec} in={self.in_tok} out={self.out_tok} "
                f"chars={len(self.text)})")


def load_config(path=CONFIG):
    if not os.path.exists(path):
        raise ProviderError(f"missing config: {path}")
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    provs = cfg.get("providers", {})
    if not provs:
        raise ProviderError(f"no [providers.*] tables in {path}")
    for name, p in provs.items():
        if p.get("kind") not in ("ollama", "openai", "anthropic", "claude-cli"):
            raise ProviderError(
                f"provider {name!r}: kind must be ollama, openai, anthropic, "
                f"or claude-cli")
        if p["kind"] != "claude-cli" and not p.get("base_url"):
            raise ProviderError(f"provider {name!r}: base_url is required")
    return cfg


def split_spec(spec):
    """`provider:model` -> (provider, model). Model may itself contain colons."""
    if ":" not in spec:
        raise ProviderError(
            f"bad spec {spec!r} — use provider:model, e.g. ollama:qwen3:14b")
    prov, model = spec.split(":", 1)
    if not prov or not model:
        raise ProviderError(f"bad spec {spec!r} — use provider:model")
    return prov, model


def _api_key(p, name):
    env = p.get("api_key_env")
    if not env:
        return None
    key = os.environ.get(env)
    if not key:
        raise ProviderError(
            f"provider {name!r} needs {env}, which is unset. "
            f"Export it, or drop the provider from config.toml.")
    return key


def _build(kind, base, key, model, system, user, seed, temp, max_tokens):
    if kind == "ollama":
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": user}]
        return (f"{base}/api/chat",
                {"Content-Type": "application/json"},
                {"model": model, "messages": msgs, "stream": False,
                 "think": False,
                 "options": {"seed": seed, "temperature": temp,
                             "num_predict": max_tokens}})
    if kind == "openai":
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": user}]
        h = {"Content-Type": "application/json"}
        if key:
            h["Authorization"] = f"Bearer {key}"
        return (f"{base}/chat/completions", h,
                {"model": model, "messages": msgs, "temperature": temp,
                 "seed": seed, "max_tokens": max_tokens})
    # anthropic
    h = {"Content-Type": "application/json", "anthropic-version": "2023-06-01"}
    if key:
        h["x-api-key"] = key
    body = {"model": model, "max_tokens": max_tokens, "temperature": temp,
            "messages": [{"role": "user", "content": user}]}
    if system:
        body["system"] = system
    return (f"{base}/messages", h, body)


def _parse(kind, d):
    if kind == "ollama":
        m = d.get("message", {})
        txt = m.get("content", "")
        # Some reasoning models ignore think:false and emit into `thinking`
        # first. With a small token budget the budget is spent before any
        # content appears, and the reply looks empty for no visible reason.
        if not txt and m.get("thinking"):
            raise RuntimeError(
                f"model returned only reasoning, no answer "
                f"({len(m['thinking'])} chars of thinking, "
                f"stopped on {d.get('done_reason')!r}). "
                f"Raise max_tokens, or judge with a non-reasoning model.")
        return (txt, d.get("prompt_eval_count"), d.get("eval_count"))
    if kind == "openai":
        ch = d.get("choices") or []
        txt = ch[0].get("message", {}).get("content", "") if ch else ""
        u = d.get("usage") or {}
        return txt, u.get("prompt_tokens"), u.get("completion_tokens")
    parts = d.get("content") or []
    txt = "".join(b.get("text", "") for b in parts if b.get("type") == "text")
    u = d.get("usage") or {}
    return txt, u.get("input_tokens"), u.get("output_tokens")


def isolated_home(root):
    """Build a HOME the CLI can run from without the operator's own config.

    `claude -p` loads the user's global memory file even when the system prompt
    is replaced, so a bare run would inject DTS into every arm and measure
    nothing. This links credentials and settings, and supplies an empty memory
    file in their place.

    It also creates an empty `work/` directory. The CLI is an agent: run it
    inside this repository and it reads the standard's own files, so a baseline
    answer starts explaining "the DTS error shape". Neutral cwd, or no baseline.
    """
    home = os.path.abspath(root)
    cdir = os.path.join(home, ".claude")
    os.makedirs(cdir, exist_ok=True)
    os.makedirs(os.path.join(home, "work"), exist_ok=True)
    real = os.path.expanduser("~/.claude")
    for name in (".credentials.json", "settings.json"):
        src, dst = os.path.join(real, name), os.path.join(cdir, name)
        if os.path.exists(src) and not os.path.exists(dst):
            os.symlink(src, dst)
    mem = os.path.join(cdir, "CLAUDE.md")
    if not os.path.exists(mem):
        open(mem, "w").write("")
    return home


def _claude_cli(p, model, system, user, timeout, max_tokens):
    """Run the local Claude CLI.

    The CLI exposes no seed and no temperature, so this path is NOT
    reproducible. Every other provider pins both, and the bench pairs arms by
    giving them the same seed for the same prompt and rep. Here two runs of one
    cell can differ by several times in length, so read medians over many reps
    and never a single cell. `deterministic` on the Reply records this.
    """
    exe = p.get("command", "claude")
    if not shutil.which(exe):
        raise ProviderError(f"{exe} is not on PATH")
    home = p.get("home")
    env = dict(os.environ)
    if home:
        env["HOME"] = isolated_home(home)
    cmd = [exe, "-p", user, "--model", model, "--output-format", "json"]
    mode = p.get("system_mode", "append")
    if mode == "replace":
        # Replacing drops the harness prompt, so this measures the model rather
        # than the agent. An empty arm still needs a prompt, or the CLI supplies
        # its default and the baseline stops being a baseline.
        cmd += ["--system-prompt", system.strip() or "You are a helpful assistant."]
        cmd += ["--exclude-dynamic-system-prompt-sections"]
    elif system.strip():
        cmd += ["--append-system-prompt", system]
    # Neutral working directory, so no arm can read the repository under test.
    work = os.path.join(env["HOME"], "work") if home else None
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       env=env, cwd=work, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        tail = (r.stderr or r.stdout)[-400:]
        if "usage limit" in tail.lower() or "rate limit" in tail.lower():
            raise QuotaError(f"claude-cli: quota exhausted. {tail}")
        raise ProviderError(f"claude-cli exit {r.returncode}: {tail}")
    try:
        d = json.loads(r.stdout)
    except Exception:
        raise ProviderError(f"claude-cli: unparseable output: {r.stdout[:300]}")
    if d.get("is_error"):
        raise ProviderError(f"claude-cli: {d.get('result', '')[:300]}")
    u = d.get("usage") or {}
    return d.get("result", ""), u.get("input_tokens"), u.get("output_tokens"), d


def complete(spec, system, user, *, cfg=None, seed=0, temperature=0.2,
             max_tokens=4096, timeout=240, retries=3):
    """Send one completion. Returns Result. Raises ProviderError on failure."""
    cfg = cfg or load_config()
    prov, model = split_spec(spec)
    p = cfg["providers"].get(prov)
    if not p:
        known = ", ".join(sorted(cfg["providers"]))
        raise ProviderError(f"unknown provider {prov!r}. Configured: {known}")
    kind = p["kind"]
    if kind == "claude-cli":
        for attempt in range(retries):
            try:
                txt, itok, otok, raw = _claude_cli(
                    p, model, system, user, timeout, max_tokens)
                if not (txt or "").strip():
                    raise ProviderError(f"{spec}: empty completion")
                # The CLI takes no seed, so this cell is not reproducible.
                return Result(txt, itok, otok, spec, raw, deterministic=False)
            except QuotaError:
                raise
            except Exception as e:
                if attempt == retries - 1:
                    raise ProviderError(f"{spec}: {e}")
                time.sleep(2 ** attempt)
    base = p["base_url"].rstrip("/")
    key = _api_key(p, prov)
    url, headers, body = _build(kind, base, key, model, system, user,
                                seed, temperature, max_tokens)

    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(body).encode(), headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            if isinstance(d, dict) and d.get("error"):
                raise ProviderError(f"{spec}: {d['error']}")
            txt, itok, otok = _parse(kind, d)
            if not (txt or "").strip():
                raise ProviderError(f"{spec}: empty completion")
            return Result(txt, itok, otok, spec, d)
        except urllib.error.HTTPError as e:
            detail = e.read()[:400].decode(errors="replace")
            if e.code == 429:
                raise QuotaError(f"{spec}: quota exhausted. {detail}")
            last = ProviderError(f"{spec}: HTTP {e.code} {detail}")
            if e.code not in RETRY_STATUS:
                raise last
        except ProviderError as e:
            last = e
        except Exception as e:
            last = ProviderError(f"{spec}: {type(e).__name__}: {e}")
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    raise last


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=CONFIG)
    ap.add_argument("--probe", nargs="*",
                    help="specs to send a one-word test completion to")
    a = ap.parse_args()

    cfg = load_config(a.config)
    print(f"config: {a.config}\n")
    print(f"{'provider':<14}{'kind':<11}{'key env':<22}{'status'}")
    for name, p in sorted(cfg["providers"].items()):
        env = p.get("api_key_env") or "-"
        if env == "-":
            st = "ready (no key needed)"
        else:
            st = "ready" if os.environ.get(env) else f"NOT SET: export {env}"
        print(f"{name:<14}{p['kind']:<11}{env:<22}{st}")

    specs = a.probe if a.probe is not None else cfg.get("bench", {}).get("models", [])
    if not specs:
        print("\nNo specs to probe. Pass --probe provider:model, or set "
              "bench.models in config.toml.")
        return
    print(f"\nprobing {len(specs)} spec(s)")
    bad = 0
    for s in specs:
        try:
            r = complete(s, "", "Reply with the single word: ok",
                         cfg=cfg, max_tokens=512, timeout=90, retries=1)
            print(f"  OK   {s:<30}{r.out_tok} out tok  {r.text.strip()[:20]!r}")
        except ProviderError as e:
            bad += 1
            print(f"  FAIL {s:<30}{e}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
