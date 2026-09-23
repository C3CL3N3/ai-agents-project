# Decisions

## Week 1

**Run conditions.** Everything below was produced on:

- machine: 14-inch MacBook Pro (2021), Apple M1 Pro chip with an 8-core CPU 14-core GPU, 16GB RAM
- model: qwen3:4b-instruct
- served by: Ollama, one request at a time, locally
- date: 2026-09-17

Every number in this file is meaningless without those four lines, so they
are stated once here and referred to rather than repeated.

### 1. Machine and model set

I am running the required model set.

I did not yet run the optional models; I will pull them before week 9 when the vision work begins.

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

If the finish reason were "length" instead of "stop", I would treat the answer as truncated and reject it as incomplete instead of assuming it was a valid final response.

### 3. Variance

| cell | distinct (recording) | distinct (mine) | median latency |
| closed_short, t=0.0 | 1/12 | 1/6 | 0.08 s |
| closed_short, t=1.0 | 1/12 | 1/6 | 0.08 s |
| open_short, t=0.0 | 1/12 | 1/6 | 1.07 s |
| open_short, t=1.0 | 5/12 | 6/6 | 1.07 s |
| open_list, t=0.0 | 1/12 | 1/6 | 0.92 s |
| open_list, t=1.0 | 11/12 | 6/6 | 0.89 s |
| open_reasoning, t=0.0 | 1/12 | not run | 5.41 s |
| open_reasoning, t=1.0 | 12/12 | not run | 5.41 s |

Which cell still returns a single answer at temperature 1.0, and why that
one:

The closed_short cell still returns a single answer at temperature 1.0 because the prompt is tightly constrained and the answer is effectively fixed: the capital of Luxembourg is a single factual answer, so temperature does not create meaningful variation.

Which cells a test asserting exact string equality would pass on, and what
that tells me about testing this system:

A test asserting exact string equality would pass on closed_short, t=0.0, closed_short, t=1.0, and open_short, t=0.0, and it would fail on open_short, t=1.0, open_list, t=1.0, and open_reasoning, t=1.0. This tells me that exact string matching is only reliable when the output is constrained and deterministic; open-ended prompts at temperature 1.0 can legitimately produce different valid answers.

**The sentence that carries into week 10.** At temperature 0 the model repeated the same output across runs, but at temperature 1.0 open-ended prompts could still produce multiple valid answers, so exact string equality is reliable only when the output space is constrained.

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

Computation: long case = 38 in, 200 out. Small = (38/1e6 _ 0.20) + (200/1e6 _ 0.80) = 0.000168 EUR/run; semester = 0.000168 _ 200 _ 7 _ 14 = 3.29 EUR. Large = (38/1e6 _ 12.00) + (200/1e6 _ 60.00) = 0.012456 EUR/run; semester = 0.012456 _ 200 _ 7 _ 14 = 244.14 EUR.

Estimates against the price list dated 2026-08-10, not measurements. Running locally, my actual monetary cost was zero.

Which tier I would run nightly, which I would run before a release, and why
not the same one for both:

I would run the small tier nightly because it is cheap enough for repeated checks, and I would run the large tier before a release when output quality matters more than the additional cost. I would not use the same tier for both because the trade-off is between cost efficiency and model capability.

### Deferred

I did not yet run the full eight-cell variance sweep on my own machine because the homework extension was still in progress at the time of the week 1 checkpoint; the two live cells and the replay comparison were sufficient to complete the required analysis for this week.

## Week 2

**Run conditions.** model: [ ] | temperature: 0.0 | prompt version: [ ] |
served locally | date: [YYYY-MM-DD] | scored on: [the recording / my own
machine]

### 1. The output contract

The conventions I chose, and why:

- due_date, when the message states no date: [ ]
- due_date, when the message states only a relative expression: [ ]
- quote, and what "verbatim" means in my scorer: [ ]
- what my scorer does with a record that failed validation: [ ]

[One sentence on why the last one matters. A scorer that skips the records
it could not parse reports a number that improves as the model gets worse.]

### 2. Zero-shot, per field

| field | correct | of |
| category | | 10 |
| urgency | | 10 |
| due_date | | 10 |
| quote | | 10 |
| invalid records | | 10 |

My prediction, written before block 3: examples will help most on [ ]
because [ ].

### 3. Few-shot

Examples chosen, and the job each one does:

| example | why it is in the block | field it should move |
| | | |
| | | |
| | | |

| field | zero-shot | few-shot | move |
| category | 9/10 | 9/10 | 0 |
| urgency | 10/10 | 10/10 | 0 |
| due_date | 7/10 | 7/10 | 0 |
| quote | 10/10 | 8/10 | -2 |

### 4. What got worse

The quote field got worse, from 10/10 to 8/10. The few-shot output copied the
German REQ-03 quote with `korrigeren` instead of the source's `korrigieren`,
and added a non-source character to the REQ-04 quote. These are genuine
substring failures, not scorer noise. The category and due-date errors did
not disappear: category remained wrong on one record, and three invented due
dates remained wrong. The examples changed the shape of the quote failures
by teaching tidied or corrupted copying, rather than fixing an existing
error.

### 5. What the examples cost

- extra input tokens per call: 310
- per thousand calls: 310,000
- estimated euros per thousand calls on the small tier: 62.00, against the
  price list dated 2026-08-10. Estimate, not a measurement.

### 6. Ship it or not

I would keep the zero-shot variant. Few-shot did not improve category,
urgency, or due_date, and reduced quote accuracy by two records while adding
310 input tokens per call. The sample has only ten records, so this is useful
evidence rather than a confident general conclusion. I would change my mind
if a larger held-out set showed a repeatable improvement in a field that
matters more than the quote regression, without introducing new exact-copy
failures.

### Sensitivity variant

Variant assigned: [ ]. What I changed: [ ]. What moved: [ ].

[If nothing moved, say so. A knob that changes nothing measurable is a real
result, and it tells the room which knobs are worth arguing about.]

### The gold set

Ten cases written to `artifacts/goldset.json`, tagged by language.

One thing my scorer cannot currently detect:

[This is the most valuable line on the page. An example: "our scorer cannot
tell a correctly formatted date that is simply the wrong date from a
correctly extracted one, because it only compares strings."]

### Deferred

[Anything you did not get to, and why.]
