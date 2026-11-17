"""Block 3. The gate, and what the state will not tell you. TODO 7.

Run it as TWO separate invocations. That is the whole exercise: if the pause
only survives inside one script, it is a session variable with extra steps.

    python 02_gate.py start
    python 02_gate.py resume approve      # or reject, or edit

The written answer is at the bottom, and the second half of it is the part
that is not on any slide.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from faults import FaultPlan
from graph import build, initial
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from project.trace import repo_root, write_json

DB = repo_root() / "artifacts" / "week08_runs.sqlite"
CASE = "RB-2026-0042"

# Homework: an unanswered approval times out after this long, and the
# timeout default is "do not submit, hold for a person". `sweep` is what a
# scheduler would run every few minutes.
APPROVAL_TIMEOUT_S = 4 * 60 * 60


def show(graph, cfg) -> None:
    snap = graph.get_state(cfg)
    print(f"    next node:     {snap.next}")
    print(f"    side effects:  {snap.values.get('side_effects')}")
    print(f"    events:        {snap.values.get('events')}")


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "start"
    verdict = sys.argv[2] if len(sys.argv) > 2 else "approve"
    cfg = {"configurable": {"thread_id": CASE}}
    plan = FaultPlan.parse("")          # no faults, the gate is the subject

    DB.parent.mkdir(parents=True, exist_ok=True)
    if mode == "start":
        DB.unlink(missing_ok=True)

    with SqliteSaver.from_conn_string(str(DB)) as saver:
        graph = build(plan, saver)

        if mode == "start":
            out = graph.invoke(initial(CASE, "parking vignette"), cfg)
            payload = out["__interrupt__"][0].value
            print("  the run has PAUSED at the gate\n")
            print(f"    action:    {payload['action']}")
            print(f"    arguments: {payload['arguments']}")
            print(f"    evidence:  {payload['evidence']}")
            print(f"    degraded:  {payload['degraded']}")
            show(graph, cfg)
            print("\n  This process can now exit, or be killed. Then run:")
            print("    python 02_gate.py resume approve")
            return 0

        before = graph.get_state(cfg)
        if not before.next:
            raise SystemExit("Nothing is paused. Run `start` first.")

        if mode == "sweep":
            # python 02_gate.py sweep [timeout_seconds]
            limit = float(sys.argv[2]) if len(sys.argv) > 2                 else APPROVAL_TIMEOUT_S
            asked = before.tasks[0].interrupts[0].value["asked_at"]
            waited = time.time() - asked
            if waited < limit:
                print(f"  still waiting: {waited:.0f}s of {limit:.0f}s")
                return 0
            print(f"  TIMEOUT: unanswered for {waited:.0f}s "
                  f"(limit {limit:.0f}s), applying the default")
            verdict = "timeout"
            out = graph.invoke(Command(resume={"verdict": "timeout",
                                               "by": "system:timeout"}), cfg)
            print(f"    submitted: {out.get('submitted')}")
            print(f"    decision:  {out.get('decision')}")
            show(graph, cfg)
            write_json("artifacts/week08_approval.json", {
                "case_id": CASE, "verdict": "timeout",
                "by": "system:timeout", "waited_s": round(waited, 1),
                "submitted": out.get("submitted"),
                "events": out.get("events")})
            print("\n  decision record written to "
                  "artifacts/week08_approval.json")
            return 0
        print(f"  resuming a run this process did not create")
        print(f"    it was paused before: {before.next}\n")

        resume = {"verdict": verdict, "by": "a.muller"}
        if verdict == "edit":
            # The approver's most common response is neither approve nor
            # reject: it is approve with one field changed. A gate with no
            # edit path throws away correct work and trains the approver to
            # approve rather than to correct.
            resume["arguments"] = {"fee": {"fee_eur": 55.0, "period": "year"}}

        out = graph.invoke(Command(resume=resume), cfg)
        print(f"    submitted: {out.get('submitted')}")
        print(f"    decision:  {out.get('decision')}")
        print(f"    fee now:   {out.get('fee')}")
        show(graph, cfg)

        record = {"case_id": CASE, "verdict": verdict,
                  "by": "a.muller", "submitted": out.get("submitted"),
                  "decision": out.get("decision"),
                  "arguments": out.get("fee"),
                  "evidence": out.get("passages"),
                  "events": out.get("events")}
        write_json("artifacts/week08_approval.json", record)
        print("\n  decision record written to artifacts/week08_approval.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# --------------------------------------------------------------------------
# TODO 7, the written answer.
# --------------------------------------------------------------------------
#
# Which step is gated: `submit`, because it is the only step that changes
# something outside the program (a case is filed in the commune's system)
# and cannot be taken back. `gather`, `price` and `draft` only read or
# compute, and they are cheap to rerun, so gating them would only teach the
# approver to click "approve" without reading.
#
# The part that is not on any slide. With W08_WRITE_ABOVE=1 the node writes
# a line to artifacts/week08_side_effect.log above the interrupt. Run
# `start` then `resume approve`: the log has TWO lines (two different pids),
# but `side_effects` in the recorded state shows no duplicate at all. The
# first execution raised to pause, so its return value was thrown away,
# while its write to the outside world stayed. So the state is not evidence
# that something happened once. The rule: above an interrupt, read only, and
# every write goes below it (or is idempotent, keyed by case id).
