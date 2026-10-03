# Decisions

# Week 1: the stack, the first call, and what it costs

Copy this into your `DECISIONS.md` and fill it in. Keep the headings. In
week 13 this becomes a section of your project report that you do not have
to write.

---

## Week 1

**Run conditions.** Everything below was produced on:

- machine: Asus Zenbook; Intel Core Ultra 9 185H processor; 32 GB RAM; Intel Arc Graphics
- model: qwen3:4b-instruct
- served by: Ollama, one request at a time, locally
- date: 2026-09-17

Every number in this file is meaningless without those four lines, so they
are stated once here and referred to rather than repeated.

### 1. Machine and model set

I am running the required model set: `qwen3:4b-instruct`.

I did not yet run the optional models; I will pull them before week 9 when the vision work begins.

### 2. The first call

| | |
| finish reason | stop |
| prompt tokens | 24 |
| completion tokens | 45 |
| elapsed | 3.24730416400007 s |

Because the finish reason was `stop`, I treated the response as complete. If
it were a truncation, I would reject it as incomplete and retry or report the
failure rather than use it as a final answer.

The answer was: "To register a change of address, visit your local
government website or contact your municipal office to obtain the necessary
forms. Complete the form with your new address and submit it in person or by
mail, depending on your location."

### 3. Variance

| cell | distinct (recording) | distinct (mine) | median latency |
| closed_short, t=0.0 | 1/12 | 1/6 | 0.22 s |
| closed_short, t=1.0 | 1/12 | 1/6 | 0.20 s |
| open_list, t=0.0 | 1/12 | 1/6 | 2.69 s |
| open_list, t=1.0 | 11/12 | 6/6 | 2.52 s |

Which cell still returns a single answer at temperature 1.0, and why that one:

The `closed_short` cell still returns a single answer at temperature 1.0 because the prompt is tightly constrained and the answer is effectively fixed: the capital of Luxembourg is a single factual answer, so temperature does not create meaningful variation.

Which cells a test asserting exact string equality would pass on and what that tells me about testing this system:

Exact equality would pass reliably for `closed_short` at both temperatures and for `open_list, t=0.0` in these runs. It would not be reliable for `open_list, t=1.0`, where all six local outputs differed. This shows that tests should assert a structured contract or acceptable properties for open-ended output, not exact text unless the output is constrained.

**The sentence that carries into week 10.**
At temperature 0 the model repeated the same output across runs, but at temperature 1.0 open-ended prompts could still produce multiple valid answers, so exact string equality is reliable only when the output space is constrained.

### 4. The cold start

- cold call: 7.99 s
- warm call: 0.19 s
- ratio: 41.39x

What this implies for a system that uses more than one model, and what I will do about it:

The 41.39x difference means that loading a model can dominate request latency. This shows that switching models inside a single workflow imposes a large latency penalty because the first request must load the model from disk. For a system that needs more than one model, I would keep each model resident for the task it serves and avoid swapping models mid-request; I would route by task instead of reloading a different model each time.

### 5. Cost, estimated

A 200-case golden set, at the token cost of my long case:

| | one run | nightly for the semester |
| small tier | 0.03352 EUR | 3.29 EUR |
| large tier | 2.49120 EUR | 244.14 EUR |

Estimates against the price list dated 2026-08-10, not measurements. The long case used 38 input tokens and 200 output tokens per case; the semester estimate assumes 200 cases nightly for 7 nights per week over 14 weeks. Running locally, my actual monetary cost was zero.

I would run the small tier nightly because its estimated semester cost is low enough for repeated checks. I would run the large tier before a release when additional quality is worth the much higher cost. I would not use the large tier nightly because the recurring estimate is about 244.14 EUR versus 3.29 EUR for the small tier.

### Deferred

/

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

# Week 2: a structured-output extractor, measured

Copy this into your `DECISIONS.md` and fill it in.

---

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
| category | | | |
| urgency | | | |
| due_date | | | |
| quote | | | |

### 4. What got worse

[Name the field, if any, and diagnose it. If nothing got worse, say so and
say how you checked. Then look at the failure lines rather than the counts,
and say whether any error disappeared or merely changed shape. A wrong label
that became a different wrong label has not been fixed.]

### 5. What the examples cost

- extra input tokens per call: [ ]
- per thousand calls: [ ]
- estimated euros per thousand calls on the small tier: [ ], against the
  price list dated [ ]. Estimate, not a measurement.

### 6. Ship it or not

[Which variant, on what evidence, and what would change your mind. Ten
records is not enough to be confident and saying so is worth more than
claiming a win. If your answer is "keep one example and drop the rest", say
which one and why.]

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
