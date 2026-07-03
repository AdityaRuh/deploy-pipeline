# safe-push — an AI-driven git push gate

> **Nothing reaches your remote until every check is green.**

`safe-push` sits between you and GitHub. When you push, it validates the
branch in a **disposable worktree** (your working folder is never touched):
runs your tests, has an AI review the diff, applies mechanically-safe fixes
automatically, parks anything affecting code intent for **your** approval —
and only then pushes and opens the pull request.

Built from scratch in dependency-free Python — five small, readable scripts.

## Install

```sh
git clone https://github.com/AdityaRuh/deploy-pipeline.git
cd deploy-pipeline
./install.sh
```

Requirements: `git`, `python3` (3.9+), and the
[Claude Code CLI](https://claude.com/claude-code), logged in
(`curl -fsSL https://claude.ai/install.sh | bash`, then run `claude` once to
sign in — uses your Claude subscription, no API billing). Optional:
[`gh`](https://cli.github.com) for automatic PR creation. macOS/Linux.

## Quick start

```sh
cd your-project
safe-push-init                  # config file + pre-push hook + gate remote
$EDITOR .safe-push.yaml         # set your test command (e.g. npm test)
```

That's it. Two ways to ship:

**Blocking (can't be forgotten):**
```sh
git push        # the pre-push hook validates first; push proceeds only if green
```

**Background (push and keep working):**
```sh
safe-push-daemon start          # once
git push gate my-branch         # returns instantly
# ...keep coding. A notification reports the verdict.
# If fixes need your judgment:
safe-push-daemon review         # see each diff, approve/reject with y/n
```

Approved fixes become a commit on top of your push, get re-validated, and
the fixed branch is forwarded to origin with a PR — automatically.

## What runs on every push

1. **Worktree isolation** — a throwaway copy of the exact commit being
   shipped; your working folder stays untouched
2. **Your checks** — `test:`, then optional `lint:` and `docs:` commands
3. **AI review** — sees only the outgoing diff; must name a concrete
   failing input before it may block (no style nitpicks)
4. **Fixes** — whitespace-safe ones auto-apply (verified mechanically, not
   by trusting the model); anything meaningful waits for your y/n
5. **Ship** — push + PR only when green. Timeouts, unclear verdicts, and
   crashed reviews all **fail closed**.

Escape hatch for emergencies: `SAFE_PUSH_BYPASS=1 git push`

## The tools

| Command | What it does |
|---|---|
| `safe-push-init` | one-time repo setup: config, pre-push hook, gate remote |
| `safe-push-final` | the shipping gate (also `--background`, `--hook`, `--autofix`) |
| `safe-push-daemon` | background service: `start` / `stop` / `status` / `review` |
| `safe-push-team` | interactive pre-commit review: reviewer → fixer → verifier |
| `safe-push-tui` | dashboard: run gates, manage the daemon, approve fixes |

## Configuration (`.safe-push.yaml`)

```yaml
test: npm test          # required for a strong gate; exit non-zero on failure
lint: make lint         # optional
docs:                   # optional
agent: claude -p        # any agent CLI that takes a prompt and prints a reply
base_branch: main       # what PRs are compared against
```

## Safety model

Trust is placed in code, never in the model's claims about itself:
whitespace-only auto-fixes are verified by stripping whitespace and comparing;
truncated "complete file" fixes are rejected; a fix that breaks tests is
rolled back automatically; every AI exchange is logged to `logs/` for replay;
and the human approves every change that touches code intent.

## Development

`benchmark/` holds 13 diffs with known verdicts (8 real bugs incl. command
injection and a mutable-default trap; 5 clean, incl. two regression traps).
Run `python3 benchmark/run-benchmark.py` after changing any review prompt —
it reports **capability** (bugs caught) and **regression** (clean not blocked)
separately, and prints the reviewer's reasoning for every miss.

---

*Every guard in this code exists because something once went wrong without it.*
