"""Stage: the planner and the reviewer. Written for week 5.

Week 5 built a planner, a free plan validator, and a reviewer against a toy
repository. The pattern transfers, the repository does not, so this file
keeps week 5's shapes and swaps the repository for the help desk's tools.

    Plan(goal, steps)               flat, because nested failed in week 5
    validate_plan(plan)             free checks against tools.REGISTRY
    Verdict(decision, reason)
    make_plan(question) -> Plan     one Pydantic AI call, NativeOutput
    review(...) -> None             a chosen pass-through, see below

The reviewer is NOT wired in, on purpose. Week 5 measured planner alone at
2/3 green and planner plus reviewer at 0/3, because the reviewer rejected
the correct fix. A reviewer with false negatives costs a call and blocks
good answers, so `review` returns None ("not reviewed") and DECISIONS.md
week 5 records why. It is a design, not a stub, so it carries no marker.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from project.models import LARGE

from .tools import REGISTRY

MODEL_NAME = LARGE.name

# Words that would mean the plan wants to change something in the world.
# The agent only has read tools, so a plan that wants to write is a plan
# that has misunderstood its job.
WRITE_WORDS = ("submit", "send", "email", "pay", "delete", "book", "file a")


class Plan(BaseModel):
    goal: str
    steps: list[str]


class Verdict(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str = Field(max_length=200)


_planner = None


def _get_planner():
    """Built on first use, so importing app/ never needs pydantic_ai."""
    global _planner
    if _planner is None:
        from pydantic_ai import Agent, NativeOutput

        from project.models import pydantic_ai_model
        tools = ", ".join(sorted(REGISTRY))
        _planner = Agent(
            pydantic_ai_model(LARGE), output_type=NativeOutput(Plan),
            retries=3, system_prompt=(
                "You plan how a help desk agent answers a resident of the "
                "commune of Remerbaach. You have NO tools and must not "
                "answer the question yourself: you write a short plan that "
                "the agent then follows.\n"
                f"The agent's only tools are: {tools}. search_services "
                "searches the commune handbook, compute does arithmetic.\n"
                "Write between one and four steps. Every plan must search "
                "the handbook before it answers. Never plan to submit, "
                "send, pay or change anything."))
    return _planner


def make_plan(question: str) -> Plan:
    """One planner call. A failed call returns an empty plan, which the
    validator refuses, rather than inventing a plan the model never made."""
    try:
        return _get_planner().run_sync(
            question, model_settings={"temperature": 0.0}).output
    except Exception as exc:                              # noqa: BLE001
        return Plan(goal=f"planner failed: {type(exc).__name__}"[:200],
                    steps=[])


def validate_plan(plan: Plan) -> tuple[bool, list[str]]:
    """Free checks, no model. Same idea as week 5, new domain."""
    problems: list[str] = []
    steps = [s.casefold() for s in plan.steps]

    if not 1 <= len(steps) <= 4:
        problems.append("plan must contain between one and four steps")
    if steps and not any("search" in s or "handbook" in s for s in steps):
        problems.append("plan never searches the handbook, so it would "
                        "answer from nothing")
    # Only a step that STARTS with a write verb is the agent planning to act.
    # "Tell the resident to submit form X" is advice, and is allowed.
    if any(s.lstrip("-*0123456789. ").startswith(w)
           for s in steps for w in WRITE_WORDS):
        problems.append("plan proposes an action that writes, and the "
                        "agent only has read tools")
    return not problems, problems


def review(question: str, answer: str,
           evidence: list[str]) -> Verdict | None:
    """Not reviewed, by decision (week 5: the reviewer rejected the correct
    fix and turned 2/3 green into 0/3). None means "not reviewed", never an
    approval."""
    return None
