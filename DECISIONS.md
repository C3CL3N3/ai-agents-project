# Decisions
## Week 1

**Run conditions.** Everything below was produced on:

- machine: 14-inch MacBook Pro (2021), Apple M1 Pro chip with an 8-core CPU 14-core GPU, 16GB RAM
- model: qwen3:4b-instruct
- served by: Ollama, one request at a time, locally
- date: [2026-09-17]

Every number in this file is meaningless without those four lines, so they
are stated once here and referred to rather than repeated.

### 1. Machine and model set

I am running the [required / required plus optional] model set.

[If you could not run the optional models, say so and say what you will do
before week 9. This is a constraint on your project, not a failure, and
naming it now is worth more than discovering it in week 9.]

### 2. The first call

```
Answer: To register a change of address, visit your local government website or contact your municipal office to obtain the necessary forms. Complete the form with your new address and submit it in person or by mail, depending on local requirements.
Finish reason: stop
Prompt tokens: 24, Completion tokens: 45
Elapsed time: 4.341789083999174
0.04 EUR per thousand calls on the small tier (24 in, 45 out per call), price list of 2026-08-10. Estimate, not a measurement.
```

| | |
| finish reason | stop |
| prompt tokens | 24 |
| completion tokens | 45 |
| elapsed | 4.341789083999174 |

One sentence on the finish reason: what my program would do differently if
it came back as a truncation rather than a normal stop.

[...]

### 3. Variance

| cell | distinct (recording) | distinct (mine) | median latency |
| closed_short, t=0.0 | 1/12 | 1/6 | 0.09 s |
| closed_short, t=1.0 | 1/12 | 1/6 | 0.08 s |
| open_list, t=0.0 | 1/12 | 1/6 | 0.92 s |
| open_list, t=1.0 | 11/12 | 6/6 | 0.82 s |

Which cell still returns a single answer at temperature 1.0, and why that
one:

The closed_short cell still returns a single answer at temperature 1.0 because the prompt is tightly constrained and the answer is effectively fixed: the capital of Luxembourg is a single factual answer, so temperature does not create meaningful variation.

Which cells a test asserting exact string equality would pass on, and what
that tells me about testing this system:

A test asserting exact string equality would pass on closed_short, t=0.0, closed_short, t=1.0, and open_list, t=0.0, but it would fail on open_list, t=1.0. This tells me that exact string matching is only reliable when the output is constrained and deterministic; open-ended prompts at temperature 1.0 can legitimately produce different valid answers.

**The sentence that carries into week 10.** At temperature 0 the model repeated the same output across runs, but at temperature 1.0 an open-ended prompt could still produce multiple valid answers, so exact string equality is reliable only when the output space is constrained.todo 

### 4. The cold start

- cold call: 1.29 s
- warm call: 0.09 s
- ratio: 14.26x

What this implies for a system that uses more than one model, and what I
will do about it:

This shows that switching models inside a single workflow imposes a large latency penalty because the first request must load the model from disk. For a system that needs more than one model, I would keep each model resident for the task it serves and avoid swapping models mid-request; I would route by task instead of reloading a different model each time. Cold/warm ratio: 1.29 s / 0.09 s = 14.26x.

### 5. Cost, estimated

A 200-case golden set, at the token cost of my long case:

| | one run | nightly for the semester |
| small tier | 0.00017 EUR | 3.29 EUR |
| large tier | 0.01246 EUR | 244.14 EUR |

Computation: long case = 38 in, 200 out. Small = (38/1e6 * 0.20) + (200/1e6 * 0.80) = 0.000168 EUR/run; semester = 0.000168 * 200 * 7 * 14 = 3.29 EUR. Large = (38/1e6 * 12.00) + (200/1e6 * 60.00) = 0.012456 EUR/run; semester = 0.012456 * 200 * 7 * 14 = 244.14 EUR.

Estimates against the price list dated 2026-08-10, not measurements. Running locally, my actual monetary cost was zero.

Which tier I would run nightly, which I would run before a release, and why
not the same one for both:

I would run the small tier nightly because it is cheap enough for repeated checks, and I would run the large tier before a release when output quality matters more than the additional cost. I would not use the same tier for both because the trade-off is between cost efficiency and model capability.

### Deferred

[Anything you did not get to, and why. An explicit deferral with a reason is
engineering. Silence is not, and the project rubric can tell the
difference.]
