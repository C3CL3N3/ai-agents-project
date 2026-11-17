"""Stage: the human approval gate. Written in week 8.

One gated step, the irreversible one: submitting a case (or posting an
invoice). It is week 8's `submit` node with its `interrupt`, in a graph of
its own with a SqliteSaver checkpoint, so a pause is a row on disk rather
than a variable in this process.

    request_approval(payload: dict, unattended: bool) -> dict

`payload` has week 8's interrupt shape: `action`, `case_id`, `arguments`
(the exact arguments, never a model's summary), `evidence`, `degraded`, and
`missing`. The return value has week 8's resume shape: `verdict`
("approve", "edit", "reject", or "timeout"), `by`, and `arguments`.

What an unanswered approval does: it times out to TIMEOUT_DEFAULT, which is
"timeout", and the pipeline treats that as NOT submitted. Nothing
irreversible happens without a person. In batch mode (`unattended=True`,
how week 10 runs the application) nobody is coming, so the timeout default
is returned at once instead of waiting.

Attended, the gate asks on the terminal and waits ATTENDED_TIMEOUT_S. With
no terminal attached (stdin is not a tty) nobody can answer, so it times
out at once too.

Week 8's rule holds: above the interrupt, read only.
"""

from __future__ import annotations

import json
import select
import sys
import time
import uuid
from typing import TypedDict

from project.trace import repo_root

DB = repo_root() / "artifacts" / "approvals.sqlite"
TIMEOUT_DEFAULT = "timeout"
ATTENDED_TIMEOUT_S = 120.0


class GateState(TypedDict):
    payload: dict
    decision: dict


def submit(state: GateState) -> dict:
    """The gated node. Nothing above the interrupt writes."""
    answer = interrupt(state["payload"])
    verdict = answer.get("verdict") or "reject"
    arguments = state["payload"].get("arguments", {})
    if verdict == "edit":
        arguments = {**arguments, **(answer.get("arguments") or {})}
    elif verdict != "approve":
        arguments = {}
    return {"decision": {"verdict": verdict, "by": answer.get("by", "?"),
                         "arguments": arguments,
                         "decided_at": time.time()}}


def _build(saver):
    from langgraph.graph import END, START, StateGraph
    g = StateGraph(GateState)
    g.add_node("submit", submit)
    g.add_edge(START, "submit")
    g.add_edge("submit", END)
    return g.compile(checkpointer=saver)


def interrupt(value):
    """LangGraph's interrupt, imported late so `import app` stays light."""
    from langgraph.types import interrupt as _interrupt
    return _interrupt(value)


def _ask_human(payload: dict, timeout: float) -> dict | None:
    """Ask on the terminal. None means nobody answered in time."""
    if not sys.stdin or not sys.stdin.isatty():
        return None
    print("\n  APPROVAL NEEDED: " + payload["action"])
    print("    arguments: " + json.dumps(payload.get("arguments"),
                                         ensure_ascii=False))
    print(f"    evidence:  {payload.get('evidence')}")
    if payload.get("degraded"):
        print(f"    DEGRADED, missing: {payload.get('missing')}")
    print(f"  approve / reject / edit field=value  "
          f"({timeout:.0f}s, then {TIMEOUT_DEFAULT}): ",
          end="", flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready:
        print()
        return None
    line = sys.stdin.readline().strip()
    if line.startswith("edit"):
        edits = dict(p.split("=", 1) for p in line.split()[1:] if "=" in p)
        return {"verdict": "edit", "by": "terminal", "arguments": edits}
    if line in ("approve", "a", "yes", "y"):
        return {"verdict": "approve", "by": "terminal"}
    return {"verdict": "reject", "by": "terminal"}


def request_approval(payload: dict, unattended: bool = False) -> dict:
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.types import Command

    DB.parent.mkdir(parents=True, exist_ok=True)
    thread = f"{payload.get('case_id', 'case')}-{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread}}
    with SqliteSaver.from_conn_string(str(DB)) as saver:
        graph = _build(saver)
        graph.invoke({"payload": payload, "decision": {}}, cfg)  # pauses

        answer = None if unattended else _ask_human(payload,
                                                    ATTENDED_TIMEOUT_S)
        if answer is None:
            answer = {"verdict": TIMEOUT_DEFAULT,
                      "by": "system:unattended" if unattended
                      else "system:timeout"}
        out = graph.invoke(Command(resume=answer), cfg)
    return {**out["decision"], "thread_id": thread}
