#!/usr/bin/env python3
"""
run-benchmark.py — the reviewer's report card.

8 diffs with KNOWN correct answers (5 contain real bugs, 3 are clean).
We show each one to the reviewer and score its verdicts.

The two scores are kept separate ON PURPOSE:

  CAPABILITY  — of the 5 bug diffs, how many did it BLOCK?
                (low is normal at first; this is the score you IMPROVE)
  REGRESSION  — of the 3 clean diffs, how many did it APPROVE?
                (must stay near 100%; this is the score you PROTECT —
                 a guard that blocks good code gets uninstalled)

Mixing them into one number hides the difference between
"reviewer got smarter" and "reviewer got paranoid".

Run it after EVERY change to the review prompt or rules:
    python3 benchmark/run-benchmark.py
Costs 8 AI calls (~1-3 minutes).
"""

import os
import pathlib
import subprocess
import sys

CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")
CASES_DIR = pathlib.Path(__file__).parent / "cases"

# Single-shot version of the reviewer (no tools) so every case
# costs exactly one AI call and results are comparable run-to-run.
REVIEW_PROMPT = """You are a code reviewer guarding a git push.
Judge from the diff alone — you cannot run tests or read other files.
Report real problems only (bugs, broken logic, security issues) — no style
nitpicks. Cryptic or unconventional code that is nevertheless CORRECT is
not a problem: before you BLOCK, you must name a concrete, realistic input
that produces a wrong result or crash — if you cannot name one, APPROVE.
Policy on crashes: a crash on a realistic edge-case input (an empty list,
a zero divisor, a missing key) COUNTS as a real problem, even though the
crash itself is "standard Python behavior" — UNLESS the code explicitly
documents that crash as intended. Do not soften this rule with words like
"warranted" or "defensible"; undocumented edge-case crash = BLOCK.
End your reply with EXACTLY ONE line:
DECISION: APPROVE   (safe to push)
DECISION: BLOCK     (contains a real problem)

Review this diff:

```diff
{diff}
```"""


def ask_claude(prompt):
    result = subprocess.run(
        [CLAUDE_BIN, "-p", prompt], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("❌ Could not reach Claude. Are you logged in? Run: claude")
        sys.exit(1)
    return result.stdout.strip()


def main():
    cases = sorted(CASES_DIR.glob("*.txt"))
    if not cases:
        print("No cases found in benchmark/cases/")
        sys.exit(1)

    print(f"🧪 Running benchmark: {len(cases)} cases, 1 AI call each...\n")
    bugs_caught, bugs_total = 0, 0
    clean_passed, clean_total = 0, 0

    for case_file in cases:
        lines = case_file.read_text().splitlines()
        expected = lines[0].replace("EXPECT:", "").strip()   # APPROVE / BLOCK
        note = lines[1].replace("NOTE:", "").strip()
        diff = "\n".join(lines[2:])

        reply = ask_claude(REVIEW_PROMPT.format(diff=diff))
        if "DECISION: BLOCK" in reply:
            verdict = "BLOCK"
        elif "DECISION: APPROVE" in reply:
            verdict = "APPROVE"
        else:
            verdict = "NO DECISION"   # counts as wrong either way

        correct = verdict == expected
        mark = "✅" if correct else "❌"
        print(f"{mark} {case_file.stem:28} expected {expected:7} got {verdict}")
        if not correct:
            print(f"     (the case: {note})")
            # Observability: show WHY it decided wrongly, so failures are
            # diagnosable from the report instead of guesswork.
            for line in reply.splitlines()[-6:]:
                print(f"       | {line}")

        if expected == "BLOCK":
            bugs_total += 1
            bugs_caught += int(correct)
        else:
            clean_total += 1
            clean_passed += int(correct)

    print("\n──────────── report card ────────────")
    print(f"CAPABILITY  (bugs caught):      {bugs_caught}/{bugs_total}")
    print(f"REGRESSION  (clean not blocked): {clean_passed}/{clean_total}")
    if clean_passed < clean_total:
        print("⚠  Regression score dropped — the reviewer is over-blocking.")
        print("   Fix this FIRST, even before chasing more bugs.")


if __name__ == "__main__":
    main()
