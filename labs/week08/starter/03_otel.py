"""Homework: one run wrapped in OpenTelemetry spans.

    python 03_otel.py

Faults are aimed so that one trace shows all three things the homework
asks for:

    search:timeout@1.0   every search times out -> 3 retries, then fallback
    fees:flaky@1.0       the first fee call fails -> 1 retry, then ok
    the gate             interrupt, then a programmatic "approve"

The node functions and `call_with_policy` are wrapped in spans from the
outside, so graph.py and retry.py are not changed for tracing. Spans are
kept in memory and written to artifacts/week08_otel_trace.json.
"""

from __future__ import annotations

import json

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter)

import graph
from faults import FaultPlan
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from project.trace import repo_root

exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("week08")

_real_call = graph.call_with_policy


def traced_call(fn, *args, policy, fallback=None, validate=None, **kwargs):
    with tracer.start_as_current_span(f"policy:{fn.__name__}") as span:
        res = _real_call(fn, *args, policy=policy, fallback=fallback,
                         validate=validate, **kwargs)
        for a in res.attempts:
            span.add_event("retry.attempt" if a.n > 1 else "attempt",
                           {"n": a.n, "error": a.error or "",
                            "slept_s": round(a.slept, 3)})
        if res.used_fallback:
            span.add_event("fallback", {"fn": fallback.__name__})
        span.set_attribute("tries", res.tries)
        span.set_attribute("outcome", res.outcome)
        span.set_attribute("used_fallback", res.used_fallback)
        return res


def traced_node(name, fn):
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(
                f"node:{name}", record_exception=False,
                set_status_on_exception=False) as span:
            try:
                return fn(*args, **kwargs)
            except BaseException as exc:        # the interrupt raises
                span.add_event("gate.interrupt" if name == "submit"
                               else "exception", {"type": type(exc).__name__})
                raise
    return wrapper


graph.call_with_policy = traced_call
for _name in ("gather", "price", "draft", "submit"):
    setattr(graph, _name, traced_node(_name, getattr(graph, _name)))


def main() -> int:
    plan = FaultPlan.parse("search:timeout@1.0,fees:flaky@1.0", seed=42)
    cfg = {"configurable": {"thread_id": "otel-demo"}}
    app = graph.build(plan, InMemorySaver())

    with tracer.start_as_current_span("run:RB-2026-0042") as root:
        out = app.invoke(graph.initial("RB-2026-0042", "parking vignette"),
                         cfg)
        root.add_event("gate.paused",
                       {"action": out["__interrupt__"][0].value["action"]})
        # No human present: resumed programmatically, and the span says so.
        with tracer.start_as_current_span("gate:resume") as span:
            span.set_attribute("verdict", "approve")
            span.set_attribute("by", "script:03_otel")
            out = app.invoke(Command(resume={"verdict": "approve",
                                             "by": "script:03_otel"}), cfg)
        root.set_attribute("submitted", bool(out.get("submitted")))

    spans = exporter.get_finished_spans()
    by_id = {s.context.span_id: s for s in spans}

    def depth(s):
        d = 0
        while s.parent is not None and s.parent.span_id in by_id:
            s, d = by_id[s.parent.span_id], d + 1
        return d

    for s in sorted(spans, key=lambda s: s.start_time):
        attrs = {k: v for k, v in s.attributes.items()}
        print(f"{'  ' * depth(s)}{s.name}  "
              f"{(s.end_time - s.start_time) / 1e6:.1f} ms  {attrs or ''}")
        for e in s.events:
            print(f"{'  ' * depth(s)}  * {e.name} {dict(e.attributes)}")

    path = repo_root() / "artifacts" / "week08_otel_trace.json"
    path.write_text(json.dumps([json.loads(s.to_json()) for s in spans],
                               indent=2), encoding="utf-8")
    print(f"\n{len(spans)} spans written to {path.relative_to(repo_root())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
