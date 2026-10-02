"""The classifier and the policy layer. TODO 2 and 3.

Two calls per request in the routed system: one to decide, one to answer.
The first is cheap and its output is inspectable. The second is the work.

The policy layer between them is about three lines of code and three design
decisions, and the decisions are where the marks are.
"""

from __future__ import annotations

import time
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from routes import ROUTES, SPECIALISTS, SYSTEM_ROUTER

from project.models import BASE_URL, API_KEY, SMALL


class Decision(BaseModel):
    route: Literal["request", "info", "status", "complaint", "other"]
    confidence: float = Field(ge=0, le=1)
    evidence: str = Field(max_length=200)


class Routed(BaseModel):
    """What the policy layer decided, and why."""

    decision: Decision
    applied_route: str
    policy_fired: str | None = None      # None means the decision stood
    evidence_ok: bool = True


# --------------------------------------------------------------------------
# TODO 2. The classifying call.
# --------------------------------------------------------------------------

def classify(client, text: str, model: str = SMALL.name,
             temperature: float = 0.0) -> tuple[Decision | None, dict]:
    """One cheap call whose only job is to pick a route.

    Build it the same way as week 2's extractor: a schema-constrained call
    with SYSTEM_ROUTER as the system message and `text` as the user message.
    Return (Decision or None, meta), where meta carries seconds,
    prompt_tokens, completion_tokens, and the raw string.

    Return None rather than raising when validation fails. You need to be
    able to count how often that happens, and an exception is not a count.

    Note what this call does not get: no tools, no reference material, and
    no instruction about how to answer. It decides and it stops. That is
    what makes it cheap enough to be worth adding, and it is what makes its
    output inspectable.
    """
    t0 = time.perf_counter()
    reply = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=120,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "decision",
                "schema": Decision.model_json_schema(),
            },
        },
        messages=[
            {"role": "system", "content": SYSTEM_ROUTER},
            {"role": "user", "content": text},
        ],
    )
    raw = reply.choices[0].message.content
    meta = {
        "seconds": time.perf_counter() - t0,
        "prompt_tokens": reply.usage.prompt_tokens,
        "completion_tokens": reply.usage.completion_tokens,
        "raw": raw,
        "error": None,
    }
    try:
        return Decision.model_validate_json(raw), meta
    except ValidationError as exc:
        meta["error"] = str(exc).splitlines()[0]
        return None, meta


# --------------------------------------------------------------------------
# TODO 3. The policy layer.
# --------------------------------------------------------------------------

# TODO 3a. Pick a number, but look at the distribution before you pick it.
#
# Choosing a threshold because 0.7 sounds reasonable is the mistake this
# exercise exists to catch. Run the classifier over the twenty four queries
# first, print the confidences, and then decide. On one of the two course
# models the answer will surprise you.
#
# Measured over the 24 queries at temperature 0:
#   SMALL  (qwen3:4b-instruct)  19/24. 0.99-1.00 on 22, and all 5 misroutes
#          sit at 0.99. The two 0.00s are Q-22/Q-23, both correct `other`.
#   LARGE  (qwen2.5:7b)         19/24. 0.95 on 13 (4 wrong), 1.00 on 11 (1 wrong).
# The confidence carries almost no information about correctness on either model.
#
# So the floor cannot be a misroute detector, and no value can make it one: a
# floor above 0.99 rejects 15 of 24 to catch 5. It is a backstop for a model
# that says it is guessing. 0.5 sits in the empty gap between 0.00 and 0.95
# on both models. The 0.00s only ever land on `other` (spam, injection), where
# the model is scoring "is this help desk business", so the floor skips
# `other`: moving an injection to `info` hands it to a specialist that answers.
CONFIDENCE_FLOOR = 0.5

# TODO 3b. Where does anything the policy rejects go?
#
# Not every route is equally safe to be wrong into. Ask what each specialist
# DOES on the sender's behalf, and pick the one whose actions are easiest to
# undo. One of the five logs a ticket, one escalates to a human, and one
# only answers. That should decide it.
# `request` logs a ticket and `complaint` escalates to a human, both of which
# create work someone has to undo. `info` only answers, and is forbidden to
# invent facts, so a wrong `info` reply costs the sender one more message.
SAFE_DEFAULT = "info"


def apply_policy(decision: Decision | None, text: str) -> Routed:
    """Take a Decision and return what will actually happen.

    Three checks. Each one is a design decision that goes in DECISIONS.md
    with a reason.

    1. The call produced no valid decision at all. Rare, and it still has to
       be handled, because the alternative is a crash on the one message
       unusual enough to break the schema.

    2. The evidence check, inherited from week 2 and still free. Is the
       evidence span actually in `text`? A router that invents its
       justification is a router you cannot audit. Note that this checks
       honesty, not correctness: a route can be right with fabricated
       evidence, and that is still a defect, because the evidence is what a
       human reviewing a misroute will read.

    3. The confidence floor from TODO 3a.

    Set `policy_fired` to a short string naming which check fired, or leave
    it None when the decision stood. You will count these at the checkpoint,
    and "the policy fired sometimes" is not a count.
    """
    if decision is None:
        placeholder = Decision(route=SAFE_DEFAULT, confidence=0.0, evidence="")
        return Routed(decision=placeholder, applied_route=SAFE_DEFAULT,
                      policy_fired="invalid_decision", evidence_ok=False)

    # Plain substring search. An empty span is trivially "in" any text, so
    # it does not count as evidence.
    span = decision.evidence.strip()
    evidence_ok = bool(span) and span in text
    if not evidence_ok:
        return Routed(decision=decision, applied_route=SAFE_DEFAULT,
                      policy_fired="evidence_not_verbatim", evidence_ok=False)

    if decision.confidence < CONFIDENCE_FLOOR and decision.route != "other":
        return Routed(decision=decision, applied_route=SAFE_DEFAULT,
                      policy_fired="below_threshold", evidence_ok=True)

    return Routed(decision=decision, applied_route=decision.route)


# --------------------------------------------------------------------------
# Given. The answering call.
# --------------------------------------------------------------------------

def respond(client, system: str, text: str,
            model: str = SMALL.name) -> tuple[str, dict]:
    t0 = time.perf_counter()
    reply = client.chat.completions.create(
        model=model, temperature=0.0, max_tokens=250,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": text}])
    return reply.choices[0].message.content, {
        "seconds": time.perf_counter() - t0,
        "prompt_tokens": reply.usage.prompt_tokens,
        "completion_tokens": reply.usage.completion_tokens,
    }
